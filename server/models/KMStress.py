import asyncio
import json
import sqlite3
import torch
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional

# --- Autoencoder definition ---
import torch

class SequenceAutoencoder(torch.nn.Module):
    def __init__(self, input_size, hidden_size, latent_size, n_heads=4):
        super().__init__()
        self.input_size  = input_size
        self.hidden_size = hidden_size

        # encoder
        self.encoder = torch.nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc_enc  = torch.nn.Linear(hidden_size, latent_size)

        # map latent → initial decoder hidden
        self.fc_dec  = torch.nn.Linear(latent_size, hidden_size)
        self.decoder = torch.nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.fc_out  = torch.nn.Linear(hidden_size, input_size)

        # attention over encoder outputs
        self.attn = torch.nn.MultiheadAttention(hidden_size, num_heads=n_heads, batch_first=True)

    def forward(self, x):
        # encode
        enc_out, (h, _) = self.encoder(x)               # enc_out: (B, T, H)
        z               = self.fc_enc(h[-1])            # (B, latent)

        # prepare decoder hidden from latent
        h_dec = self.fc_dec(z).unsqueeze(0)             # (1, B, H)
        c_dec = torch.zeros_like(h_dec)

        # attention: use decoder init state as query, encoder outputs as K/V
        # query shape (B, 1, H)
        q = h_dec.squeeze(0).unsqueeze(1)
        # enc_out is (B, T, H) so directly usable as K, V
        attn_out, _ = self.attn(q, enc_out, enc_out)    # (B, 1, H)

        # tile attended context over full sequence length
        seq_len = x.size(1)
        dec_in  = attn_out.expand(x.size(0), seq_len, self.hidden_size)

        # decode and project
        dec_out, _ = self.decoder(dec_in, (h_dec, c_dec))  # (B, T, H)
        out        = self.fc_out(dec_out)                  # (B, T, input)
        return out


# --- Pydantic models ---
class Event(BaseModel):
    device_id: str
    timestamp: float
    event_type: str   # "move","click_down","click_up","scroll","key_down","key_up"
    data: dict        # {"x":..,"y":..,"button":..} or {"dx":..,"dy":..} or {"key_code":..}

class Batch(BaseModel):
    device_id: str
    events: List[Event]

# --- Setup ---
DB_PATH = "events.db"
app     = FastAPI()
model   = SequenceAutoencoder(input_size=6, hidden_size=64, latent_size=16)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=0.03)
CRIT      = torch.nn.MSELoss()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_events(
            id INTEGER PRIMARY KEY,
            device_id TEXT,
            timestamp REAL,
            event_type TEXT,
            data TEXT
        )""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS anomalies(
            id INTEGER PRIMARY KEY,
            device_id TEXT,
            timestamp REAL,
            score REAL
        )""")
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

# --- Helpers ---
def store_batch(batch: Batch):
    conn = sqlite3.connect(DB_PATH)
    for ev in batch.events:
        conn.execute(
            "INSERT INTO raw_events(device_id,timestamp,event_type,data) VALUES (?,?,?,?)",
            (ev.device_id, ev.timestamp, ev.event_type, json.dumps(ev.data)),
        )
    conn.commit()
    conn.close()


def load_sequences(device_id, window_size=200):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT timestamp, event_type, data FROM raw_events "
        "WHERE device_id=? ORDER BY timestamp DESC LIMIT ?",
        (device_id, window_size),
    )
    rows = cur.fetchall()[::-1]
    conn.close()

    feats = []
    prev_t = None
    for t, et, d_json in rows:

        d     = json.loads(d_json)
        delta = t - prev_t if prev_t else 0.0
        prev_t = t

        # default zero vector
        is_click, is_key = 0, 0
        coords = [0.0, 0.0]
        key    = [0.0]

        # collapse downs/ups → click/key
        if et in ("click_down", "click_up"):
            is_click = 1
            coords = [d.get("x", 0)/1920, d.get("y", 0)/1080]
        elif et in ("key_down", "key_up"):
            is_key = 1
            key    = [d.get("key_code", 0)/255]

        feats.append([is_click, is_key, delta] + coords + key)

    if not feats:
        return None
    return torch.tensor([feats], dtype=torch.float)

async def train_on_device(device_id):
    seq = load_sequences(device_id)
    if seq is None:
        return None
    out  = model(seq)
    loss = CRIT(out, seq)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()

async def infer_device(device_id, threshold=0.01):
    seq = load_sequences(device_id)
    if seq is None:
        return False, 0.0
    out = model(seq)
    err = torch.mean((out - seq) ** 2).item()
    return err > threshold, err

# --- API endpoints ---
@app.post("/push_batch")
async def push_batch(batch: Batch):
    store_batch(batch)
    loss    = await train_on_device(batch.device_id)
    anomaly, score = await infer_device(batch.device_id)

    timestamp = (
        batch.events[-1].timestamp
        if batch.events
        else datetime.now(timezone.utc).timestamp()
    )

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO anomalies(device_id,timestamp,score) VALUES (?,?,?)",
        (batch.device_id, timestamp, score * 100),  # percent
    )
    # keep only latest 1000 raw_events per device
    conn.execute(
        """
        DELETE FROM raw_events
        WHERE id IN (
          SELECT id FROM raw_events
          WHERE device_id=?
          ORDER BY timestamp DESC
          LIMIT -1 OFFSET 1000
        )
        """, (batch.device_id,)
    )
    conn.commit()
    conn.close()

    return {"anomaly": anomaly, "score": score * 100, "loss": loss}

@app.get("/anomalies")
def get_anomalies(
    device_id: str = Query(...),
    start: Optional[float] = Query(None),
    end: Optional[float] = Query(None),
):
    q      = "SELECT timestamp, score FROM anomalies WHERE device_id=?"
    params = [device_id]
    if start is not None:
        q += " AND timestamp>=?"
        params.append(start)
    if end is not None:
        q += " AND timestamp<=?"
        params.append(end)

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.execute(q, tuple(params))
    rows = cur.fetchall()
    conn.close()

    return [{"timestamp": t, "score": s} for t, s in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.79.75", port=8000)
