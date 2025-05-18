from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import sqlite3
import numpy as np
from PIL import Image
import io
import os
import requests
import torch
from ultralytics import YOLO
from transformers import CLIPModel, CLIPProcessor
from scipy.spatial.distance import cosine
from fastapi.middleware.cors import CORSMiddleware

# Download & initialize face detector from Hugging Face (Bingsu/adetailer)
face_detector = YOLO('https://github.com/lindevs/yolov8-face/releases/latest/download/yolov8n-face-lindevs.pt')

# Initialize embedding model
clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

# Database setup
conn = sqlite3.connect('faces.db', check_same_thread=False)
c = conn.cursor()
c.execute(
    '''CREATE TABLE IF NOT EXISTS faces(
           user_id TEXT PRIMARY KEY,
           embedding BLOB
       )''')
conn.commit()

app = FastAPI()
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
def detect_and_crop(image: Image.Image) -> Image.Image:
    """Detects the largest face and returns the cropped face region."""
    results = face_detector(np.array(image))
    if not results or not results[0].boxes:
        return None
    boxes = results[0].boxes.xyxy.cpu().numpy()
    # select largest
    areas = (boxes[:,2] - boxes[:,0]) * (boxes[:,3] - boxes[:,1])
    x1, y1, x2, y2 = boxes[np.argmax(areas)].astype(int)
    return image.crop((x1, y1, x2, y2))

def get_embedding(face_img: Image.Image) -> np.ndarray:
    """Generates a normalized embedding for a face image."""
    inputs = clip_processor(images=face_img, return_tensors='pt')
    with torch.no_grad():
        emb = clip_model.get_image_features(**inputs)
    emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
    return emb.squeeze().cpu().numpy()


@app.post('/enroll')
async def enroll(
    user_id: str = Form(...),
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    file3: UploadFile = File(...)
):
    embeddings = []
    for f in (file1, file2, file3):
        data = await f.read()
        image = Image.open(io.BytesIO(data)).convert('RGB')
        face = detect_and_crop(image)
        if face is None:
            return JSONResponse({'error': 'No face detected.'}, status_code=400)
        embeddings.append(get_embedding(face))
    avg_emb = np.mean(np.stack(embeddings), axis=0).astype(np.float32)
    c.execute('REPLACE INTO faces VALUES (?,?)', (user_id, avg_emb.tobytes()))
    conn.commit()
    return JSONResponse({'status': 'enrolled', 'user_id': user_id})

@app.post('/identify')
async def identify(
    file: UploadFile = File(...),
    threshold: float = Form(0.5)
):
    data = await file.read()
    image = Image.open(io.BytesIO(data)).convert('RGB')
    face = detect_and_crop(image)
    if face is None:
        return JSONResponse({'error': 'No face detected.'}, status_code=400)
    probe = get_embedding(face)

    best_score, best_id = -1.0, None
    for user_id, emb_blob in c.execute('SELECT user_id, embedding FROM faces'):
        enrolled = np.frombuffer(emb_blob, dtype=np.float32)
        score = 1 - cosine(probe, enrolled)
        if score > best_score:
            best_score, best_id = score, user_id

    if best_score >= threshold:
        return JSONResponse({'result': 'known', 'user_id': best_id, 'score': float(best_score)})
    return JSONResponse({'result': 'unknown', 'max_score': float(best_score)})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3002)