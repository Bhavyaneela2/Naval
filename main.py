
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, numpy as np, librosa, cv2, tensorflow as tf
from ultralytics import YOLO

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MODEL_PATH = "models/audio_classifier.h5"
if not os.path.exists(MODEL_PATH):
    print("Generating Dummy TF Model...")
    model = tf.keras.Sequential([tf.keras.layers.Input(shape=(40,)), tf.keras.layers.Dense(1, activation='sigmoid')])
    model.compile(optimizer='adam', loss='binary_crossentropy')
    model.save(MODEL_PATH)

audio_model = tf.keras.models.load_model(MODEL_PATH)
try:
    image_model = YOLO("yolov8n.pt")
except:
    image_model = None

def analyze_audio(path):
    try:
        y, sr = librosa.load(path, duration=3.0)
        mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
        return int(audio_model.predict(np.expand_dims(mfccs, axis=0), verbose=0)[0][0] * 100)
    except: return 50

def analyze_image(path):
    if not image_model: return 50
    try:
        results = image_model(path, verbose=False)
        score = 0
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 8: score += 40 * float(box.conf[0]) # Boat
                else: score += 5 * float(box.conf[0])
        return min(100, int(score))
    except: return 50

@app.post("/scan-area")
async def scan(lat: float = Form(...), lng: float = Form(...), audio_file: UploadFile = File(...), image_file: UploadFile = File(...)):
    a_path = f"temp_uploads/{audio_file.filename}"
    i_path = f"temp_uploads/{image_file.filename}"
    with open(a_path, "wb") as b: shutil.copyfileobj(audio_file.file, b)
    with open(i_path, "wb") as b: shutil.copyfileobj(image_file.file, b)
    
    base_a = analyze_audio(a_path)
    base_i = analyze_image(i_path)
    
    zones = [
        {"id": "ALPHA-1", "name": "NW Sector", "lat": float(lat)+0.005, "lng": float(lng)-0.005},
        {"id": "BETA-2", "name": "NE Sector", "lat": float(lat)+0.005, "lng": float(lng)+0.005},
        {"id": "GAMMA-3", "name": "SW Sector", "lat": float(lat)-0.005, "lng": float(lng)-0.005},
        {"id": "DELTA-4", "name": "SE Sector", "lat": float(lat)-0.005, "lng": float(lng)+0.005}
    ]
    results = []
    for i, z in enumerate(zones):
        var = (i*10)-15
        ascore = max(0, min(100, base_a + var))
        iscore = max(0, min(100, base_i + var))
        total = int((ascore*0.6)+(iscore*0.4))
        lvl, clr = ("LOW", "green") if total <= 40 else ("MEDIUM", "yellow") if total <= 75 else ("HIGH", "red")
        results.append({**z, "audio_score": ascore, "image_score": iscore, "total_score": total, "level": lvl, "color": clr})
    
    return {"status": "success", "data": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
