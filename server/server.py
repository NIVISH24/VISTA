import sqlite3
import json
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
import numpy as np
import torch, torchaudio, webrtcvad
from torchaudio.transforms import Resample
from speechbrain.inference.classifiers import EncoderClassifier
from datetime import datetime, timezone
from scipy.spatial.distance import cosine

# --- Database Setup ---
DB_PATH = 'ultimate.db'
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

# Replace the global connection with this:
from fastapi import Depends
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
        
c.execute("""
CREATE TABLE IF NOT EXISTS voice_history(
    id INTEGER PRIMARY KEY,
    pc_id TEXT,
    user_id TEXT,
    timestamp REAL,
    result TEXT,
    score REAL
)""")
# Create top-level tables
c.execute("""
CREATE TABLE IF NOT EXISTS pcs(
    pc_id TEXT PRIMARY KEY,
    fingerprint TEXT
)""")
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id TEXT PRIMARY KEY
)""")
c.execute("""
CREATE TABLE IF NOT EXISTS pc_user_map(
    pc_id TEXT,
    user_id TEXT,
    PRIMARY KEY(pc_id, user_id),
    FOREIGN KEY(pc_id) REFERENCES pcs(pc_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)""")

# USB/hardware events
c.execute("""
CREATE TABLE IF NOT EXISTS usb_events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pc_id TEXT,
    event_type TEXT,
    timestamp REAL
)""")

# Voice embeddings
c.execute("""
CREATE TABLE IF NOT EXISTS voice_embeddings(
    user_id TEXT PRIMARY KEY,
    embedding BLOB
)""")

# Face embeddings
c.execute("""
CREATE TABLE IF NOT EXISTS face_embeddings(
    user_id TEXT PRIMARY KEY,
    embedding BLOB
)""")

# Keystroke/mouse raw events & anomalies
c.execute("""
CREATE TABLE IF NOT EXISTS raw_events(
    id INTEGER PRIMARY KEY,
    device_id TEXT,
    timestamp REAL,
    event_type TEXT,
    data TEXT
)""")
c.execute("""
CREATE TABLE IF NOT EXISTS anomalies(
    id INTEGER PRIMARY KEY,
    device_id TEXT,
    timestamp REAL,
    score REAL
)""")
# Add to database setup after table creation
c.execute("CREATE INDEX IF NOT EXISTS idx_raw_events_device ON raw_events(device_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_device ON anomalies(device_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_voice_history_pc ON voice_history(pc_id)")

conn.commit()

# --- Initialize Models ---
# Voice VAD and encoder
vad = webrtcvad.Vad(1)
voice_clf = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa"
)
# Keystroke Autoencoder (import your existing SequenceAutoencoder and optimizer here)
from models.KMStress import SequenceAutoencoder, optimizer, CRIT, load_sequences, infer_device, train_on_device
model = SequenceAutoencoder(input_size=6, hidden_size=64, latent_size=16)

app = FastAPI(title="Ultimate VAuth Server")

# --- Helper Functions ---
def ensure_16k(wav: torch.Tensor, orig_fs: int) -> torch.Tensor:
    if orig_fs != 16000:
        wav = Resample(orig_freq=orig_fs, new_freq=16000)(wav)
    return wav

def extract_speech(wav: np.ndarray, fs: int = 16000, frame_ms: int = 30) -> np.ndarray:
    frames = int(fs * frame_ms / 1000)
    speech = []
    for i in range(0, len(wav), frames):
        frame = wav[i:i+frames]
        if len(frame) < frames:
            break
        pcm = (frame * 32768).astype(np.int16).tobytes()
        if vad.is_speech(pcm, fs):
            speech.extend(frame)
    return np.array(speech)

def get_voice_embedding(wav_np: np.ndarray) -> np.ndarray:
    sig = torch.from_numpy(wav_np).unsqueeze(0)
    emb = voice_clf.encode_batch(sig)
    return emb.squeeze().cpu().numpy()

# --- KM Helpers ---
def load_sequences(conn, device_id, window_size=200):
    cur = conn.execute(
        "SELECT timestamp, event_type, data FROM raw_events "
        "WHERE device_id=? ORDER BY timestamp DESC LIMIT ?",
        (device_id, window_size),
    )
    rows = cur.fetchall()[::-1]  # Reverse to get chronological order

    feats = []
    prev_t = None
    for row in rows:
        t, et, d_json = row['timestamp'], row['event_type'], row['data']
        d = json.loads(d_json)
        delta = t - prev_t if prev_t else 0.0
        prev_t = t

        # Feature normalization
        is_click = 1 if et in ("click_down", "click_up") else 0
        is_key = 1 if et in ("key_down", "key_up") else 0
        x = d.get('x', 0)/1920  # Normalize assuming 1080p screen
        y = d.get('y', 0)/1080
        key = d.get('key_code', 0)/255  # Normalize keycodes
        
        feats.append([is_click, is_key, delta, x, y, key])

    if not feats:
        return None
    return torch.tensor([feats], dtype=torch.float32)

async def train_on_device(device_id, conn):
    seq = load_sequences(conn, device_id)
    if seq is None:
        return None
    out = model(seq)
    loss = CRIT(out, seq)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()

async def infer_device(device_id, conn, threshold=0.01):
    seq = load_sequences(conn, device_id)
    if seq is None:
        return False, 0.0
    with torch.no_grad():
        out = model(seq)
    err = torch.mean((out - seq) ** 2).item()
    return err > threshold, err
# --- API Endpoints ---

# PC & User Registration
@app.post("/register_pc")
def register_pc(pc_id: str = Form(...), fingerprint: str = Form(...)):
    c.execute("REPLACE INTO pcs(pc_id, fingerprint) VALUES (?,?)", (pc_id, fingerprint))
    conn.commit()
    return {"status": "pc_registered", "pc_id": pc_id}

@app.post("/register_user")
def register_user(user_id: str = Form(...)):
    c.execute("REPLACE INTO users(user_id) VALUES (?)", (user_id,))
    conn.commit()
    return {"status": "user_registered", "user_id": user_id}

@app.post("/map_pc_user")
def map_pc_user(pc_id: str = Form(...), user_id: str = Form(...)):
    c.execute("INSERT OR IGNORE INTO pc_user_map VALUES (?,?)", (pc_id, user_id))
    conn.commit()
    return {"status": "mapped", "pc_id": pc_id, "user_id": user_id}

# USB/Hardware events
@app.post("/usb_event")
def usb_event(pc_id: str = Form(...), event_type: str = Form(...), timestamp: float = Form(None)):
    ts = timestamp or datetime.now(timezone.utc).timestamp()
    c.execute("INSERT INTO usb_events(pc_id, event_type, timestamp) VALUES (?,?,?)", (pc_id, event_type, ts))
    conn.commit()
    return {"status": "usb_event_recorded", "pc_id": pc_id}

# Voice Endpoints
@app.post("/voice/enroll")
async def voice_enroll(user_id: str = Form(...), file1: UploadFile = File(...), file2: UploadFile = File(...), file3: UploadFile = File(...)):
    embs = []
    for f in (file1, file2, file3):
        data = await f.read()
        wav, fs = torchaudio.load(io.BytesIO(data))
        mono = wav.mean(dim=0, keepdim=True)
        wav16k = ensure_16k(mono, fs)
        wav_np = wav16k.squeeze(0).numpy()
        speech = extract_speech(wav_np)
        embs.append(get_voice_embedding(speech))
    avg = np.mean(np.stack(embs), axis=0).astype(np.float32)
    c.execute("REPLACE INTO voice_embeddings VALUES (?,?)", (user_id, avg.tobytes()))
    conn.commit()
    return JSONResponse({"status": "voice_enrolled", "user_id": user_id})

@app.post("/voice/identify")
async def voice_identify(file: UploadFile = File(...), threshold: float = Form(0.40), pc_id: str = Form(...)):
    data = await file.read()
    wav, fs = torchaudio.load(io.BytesIO(data))
    mono = wav.mean(dim=0, keepdim=True)
    wav16k = ensure_16k(mono, fs)
    speech = extract_speech(wav16k.squeeze(0).numpy())
    probe = get_voice_embedding(speech)

    best_score, best_id = -1.0, None
    for user_id, blob in c.execute("SELECT user_id, embedding FROM voice_embeddings"):
        enrolled = np.frombuffer(blob, dtype=np.float32)
        score = 1 - cosine(probe, enrolled)
        if score > best_score:
            best_score, best_id = score, user_id
    ts = datetime.now(timezone.utc).timestamp()
    if best_score >= threshold:
        c.execute(
            "INSERT INTO voice_history VALUES (?,?,?,?,?,?)",
            (None, pc_id, best_id, ts, "known", best_score)  # Now using pc_id from form
        )
        conn.commit()
        return JSONResponse({"result": "known", "user_id": best_id, "score": best_score})
    else:
        c.execute(
            "INSERT INTO voice_history VALUES (?,?,?,?,?,?)",
            (None, pc_id, None, ts, "unknown", best_score)  # Now using pc_id from form
        )
        conn.commit()
        return JSONResponse({"result": "unknown", "max_score": best_score})


# Keystroke/Mouse Endpoints
@app.post("/km/push_batch")
async def push_km(batch: dict, conn: sqlite3.Connection = Depends(get_db)):
    try:
        device_id = batch['device_id']
        events = batch['events']
        
        # Validate event format
        for ev in events:
            if not all(k in ev for k in ('timestamp', 'event_type', 'data')):
                raise HTTPException(status_code=400, detail="Invalid event format")
            
            # Insert each event inside the loop
            conn.execute(
                "INSERT INTO raw_events(device_id,timestamp,event_type,data) VALUES (?,?,?,?)",
                (device_id, ev['timestamp'], ev['event_type'], json.dumps(ev['data']))
            )
        # Cleanup old events
        conn.execute("""
            DELETE FROM raw_events WHERE id IN (
                SELECT id FROM raw_events
                WHERE device_id=?
                ORDER BY timestamp DESC
                LIMIT -1 OFFSET 1000
            )""", (device_id,))
        
        # Process anomalies
        loss = await train_on_device(device_id, conn)
        anomaly, score = await infer_device(device_id, conn)
        
        ts = events[-1]['timestamp'] if events else datetime.now(timezone.utc).timestamp()
        conn.execute(
            "INSERT INTO anomalies(device_id,timestamp,score) VALUES (?,?,?)",
            (device_id, ts, score*100))
        
        conn.commit()
        return {"anomaly": anomaly, "score": score*100, "loss": loss}

    except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))

# --- API Endpoints ---

# Dashboard APIs
@app.get("/dashboard/pcs")
def list_pcs():
    rows = c.execute("SELECT pc_id, fingerprint FROM pcs").fetchall()
    return [{"pc_id": pc, "fingerprint": fp} for pc, fp in rows]

@app.get("/dashboard/users")
def list_users():
    rows = c.execute("SELECT user_id FROM users").fetchall()
    return [u[0] for u in rows]

@app.get("/dashboard/mappings")
def list_mappings():
    rows = c.execute("SELECT pc_id, user_id FROM pc_user_map").fetchall()
    return [{"pc_id": pc, "user_id": user} for pc, user in rows]

@app.get("/dashboard/km/anomalies")
def dashboard_km(pc_id: str = Query(None), start: float = Query(None), end: float = Query(None)):
    q = "SELECT device_id, timestamp, score FROM anomalies"
    params = []
    if pc_id:
        q += " WHERE device_id=?"
        params.append(pc_id)
    if start is not None:
        q += " AND timestamp>=?" if params else " WHERE timestamp>=?"
        params.append(start)
    if end is not None:
        q += " AND timestamp<=?" if params else " WHERE timestamp<=?"
        params.append(end)
    rows = c.execute(q, tuple(params)).fetchall()
    return [{"device_id": d, "timestamp": t, "score": s} for d, t, s in rows]

@app.get("/dashboard/voice/history")
def dashboard_voice(pc_id: str = Query(None), user_id: str = Query(None), start: float = Query(None), end: float = Query(None)):
    q = "SELECT pc_id, user_id, timestamp, result, score FROM voice_history"
    params = []
    clauses = []
    if pc_id:
        clauses.append("pc_id=?"); params.append(pc_id)
    if user_id:
        clauses.append("user_id=?"); params.append(user_id)
    if start is not None:
        clauses.append("timestamp>=?"); params.append(start)
    if end   is not None:
        clauses.append("timestamp<=?"); params.append(end)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    rows = c.execute(q, tuple(params)).fetchall()
    return [
        {"pc_id": pc, "user_id": uid, "timestamp": ts, "result": res, "score": sc}
        for pc, uid, ts, res, sc in rows
    ]


@app.get("/km/anomalies")
def get_km(device_id: str = Query(...), start: float = Query(None), end: float = Query(None)):
    q = "SELECT timestamp, score FROM anomalies WHERE device_id=?"
    params = [device_id]
    if start: q += " AND timestamp>=?"; params.append(start)
    if end:   q += " AND timestamp<=?"; params.append(end)
    rows = conn.execute(q, tuple(params)).fetchall()
    return [{"timestamp": t, "score": s} for t,s in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
