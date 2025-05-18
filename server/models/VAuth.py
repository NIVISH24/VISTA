from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import sqlite3
import numpy as np
import torch, torchaudio, webrtcvad
from torchaudio.transforms import Resample
from speechbrain.inference.classifiers import EncoderClassifier
import io
from scipy.spatial.distance import cosine
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware


# Initialize components
vad = webrtcvad.Vad(1)  # aggressiveness 0–3
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa"
)

# Database connection
conn = sqlite3.connect("speakers.db", check_same_thread=False)
c = conn.cursor()
# Create tables
c.execute(
    """CREATE TABLE IF NOT EXISTS speakers(
            user_id TEXT PRIMARY KEY,
            embedding BLOB
        )"""
)
c.execute(
    """CREATE TABLE IF NOT EXISTS identifications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            result TEXT NOT NULL,
            user_id TEXT
        )"""
)
conn.commit()

def ensure_16k(wav: torch.Tensor, orig_fs: int) -> torch.Tensor:
    """Resample to 16 kHz if needed."""
    if orig_fs != 16000:
        resampler = Resample(orig_freq=orig_fs, new_freq=16000)
        wav = resampler(wav)
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

def get_embedding(wav_np: np.ndarray) -> np.ndarray:
    signal = torch.from_numpy(wav_np).unsqueeze(0)
    emb = classifier.encode_batch(signal)
    return emb.squeeze().cpu().numpy()

def create_app():
    app = FastAPI()
    app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allow all HTTP methods
            allow_headers=["*"],  # Allow all headers
        )
    @app.post("/enroll")
    async def enroll(
        user_id: str = Form(...),
        file1: UploadFile = File(...),
        file2: UploadFile = File(...),
        file3: UploadFile = File(...)
    ):
        embs = []
        for f in (file1, file2, file3):
            data = await f.read()
            wav, fs = torchaudio.load(io.BytesIO(data))         # wav: [channels, time]
            mono = wav.mean(dim=0, keepdim=True)                # convert to mono
            wav16k = ensure_16k(mono, fs)                       # resample if needed
            wav_np = wav16k.squeeze(0).numpy()
            speech = extract_speech(wav_np, 16000)
            embs.append(get_embedding(speech))
        avg_emb = np.mean(np.stack(embs), axis=0).astype(np.float32)
        c.execute("REPLACE INTO speakers VALUES (?,?)", (user_id, avg_emb.tobytes()))
        conn.commit()
        return JSONResponse({"status": "enrolled", "user_id": user_id})

    @app.post("/identify")
    async def identify(file: UploadFile = File(...), threshold: float = Form(0.40)):
        data = await file.read()
        wav, fs = torchaudio.load(io.BytesIO(data))
        mono = wav.mean(dim=0, keepdim=True)
        wav16k = ensure_16k(mono, fs)
        wav_np = wav16k.squeeze(0).numpy()
        speech = extract_speech(wav_np, 16000)
        probe = get_embedding(speech)

        best_score, best_id = -1.0, None
        for user_id, emb_blob in c.execute("SELECT user_id, embedding FROM speakers"):
            enrolled = np.frombuffer(emb_blob, dtype=np.float32)
            score = 1 - cosine(probe, enrolled)
            if score > best_score:
                best_score, best_id = score, user_id

        result = None
        if best_score >= threshold:
            result = 'known'
            response = {"result": "known", "user_id": best_id, "score": float(best_score)}
        else:
            result = 'unknown'
            response = {"result": "unknown", "max_score": float(best_score)}

        # Log identification
        timestamp = datetime.now(timezone.utc).isoformat()
        user_rec = best_id if result == 'known' else None
        c.execute(
            "INSERT INTO identifications (timestamp, result, user_id) VALUES (?, ?, ?)",
            (timestamp, result, user_rec)
        )
        conn.commit()

        return JSONResponse(response)

    @app.get("/dashboard/voice")
    async def dashboard_voice():
        rows = c.execute(
            "SELECT timestamp, result, COALESCE(user_id, 'unknown') AS user_id FROM identifications ORDER BY id"
        ).fetchall()
        data = [ {"timestamp": ts, "result": res, "user_id": uid} for ts, res, uid in rows ]
        return JSONResponse({"records": data})

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)
