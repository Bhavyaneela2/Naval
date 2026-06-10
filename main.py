import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import numpy as np
import librosa
from ultralytics import YOLO
from PIL import Image
import webbrowser
from threading import Timer

app = FastAPI()
# ---------------- OPEN BROWSER AUTOMATICALLY ----------------
def open_browser():
    webbrowser.open("http://localhost:8000/static/index.html")
# ---------------- ROUTES ----------------
@app.get("/")
def root():
    return FileResponse("static/index.html")

# ---------------- STATIC FILES ----------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- TEMP DIRECTORY ----------------
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# ---------------- LOAD YOLO MODEL ----------------
try:
    print("⏳ Loading YOLOv8 Model...")
    image_model = YOLO("yolov8n.pt")
    print("✅ YOLOv8 Model Loaded Successfully.")
except Exception as e:
    print(f"❌ Error loading YOLO: {e}")
    image_model = None

# ---------------- AUDIO ANALYSIS ----------------
def analyze_audio_real(file_path):
    try:
        y, sr = librosa.load(file_path, sr=22050, duration=5.0)

        rms = np.mean(librosa.feature.rms(y=y))
        loudness_score = min(100, (rms / 0.05) * 100)

        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        freq_score = min(100, (centroid / 3000) * 100)

        final_score = (loudness_score * 0.6) + (freq_score * 0.4)

        if final_score < 10:
            return 0

        return int(final_score)

    except Exception as e:
        print(f"Audio Error: {e}")
        return 0

# ---------------- IMAGE ANALYSIS ----------------
def analyze_quadrant(image_slice_path):
    if not image_model:
        return 0

    try:
        results = image_model(image_slice_path, verbose=False)
        threat_score = 0

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if cls_id == 8:
                    threat_score += 80 * conf
                elif cls_id == 0:
                    threat_score += 40 * conf
                elif cls_id == 4:
                    threat_score += 60 * conf
                else:
                    threat_score += 5 * conf

        return min(100, int(threat_score))

    except Exception as e:
        print(f"Image Error: {e}")
        return 0

# ---------------- SCAN API ----------------
@app.post("/scan-area")
async def scan_area(
    lat: float = Form(...),
    lng: float = Form(...),
    audio_file: UploadFile = File(...),
    image_file: UploadFile = File(...)
):

    a_path = f"{TEMP_DIR}/{audio_file.filename}"
    i_path = f"{TEMP_DIR}/{image_file.filename}"

    with open(a_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    with open(i_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    base_audio_risk = analyze_audio_real(a_path)

    original_img = Image.open(i_path)
    width, height = original_img.size
    mid_x, mid_y = width // 2, height // 2

    sectors_info = [
        {
            "id": "ALPHA-1",
            "name": "NW Sector (Top-Left)",
            "crop": (0, 0, mid_x, mid_y),
            "lat": lat + 0.005,
            "lng": lng - 0.005
        },
        {
            "id": "BETA-2",
            "name": "NE Sector (Top-Right)",
            "crop": (mid_x, 0, width, mid_y),
            "lat": lat + 0.005,
            "lng": lng + 0.005
        },
        {
            "id": "GAMMA-3",
            "name": "SW Sector (Bottom-Left)",
            "crop": (0, mid_y, mid_x, height),
            "lat": lat - 0.005,
            "lng": lng - 0.005
        },
        {
            "id": "DELTA-4",
            "name": "SE Sector (Bottom-Right)",
            "crop": (mid_x, mid_y, width, height),
            "lat": lat - 0.005,
            "lng": lng + 0.005
        },
    ]

    results = []

    for sector in sectors_info:

        crop_path = f"{TEMP_DIR}/{sector['id']}.jpg"

        cropped_img = original_img.crop(sector['crop'])
        cropped_img.save(crop_path)

        visual_risk = analyze_quadrant(crop_path)

        audio_risk = base_audio_risk

        total_score = int((audio_risk * 0.5) + (visual_risk * 0.5))

        if total_score > 75:
            level = "HIGH"
            color = "red"
        elif total_score > 30:
            level = "MEDIUM"
            color = "yellow"
        else:
            level = "LOW"
            color = "green"

        results.append({
            "id": sector["id"],
            "name": sector["name"],
            "lat": sector["lat"],
            "lng": sector["lng"],
            "audio_score": audio_risk,
            "image_score": visual_risk,
            "total_score": total_score,
            "level": level,
            "color": color
        })

        if os.path.exists(crop_path):
            os.remove(crop_path)

    return {
        "status": "success",
        "data": results
    }

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Timer(1, open_browser).start()

    uvicorn.run(
        app,
        host="localhost",
        port=8000
    )