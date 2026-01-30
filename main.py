import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import numpy as np
import librosa
import cv2
from ultralytics import YOLO
from PIL import Image

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# Load YOLO Model (Real Object Detection)
try:
    print("⏳ Loading YOLOv8 Model...")
    image_model = YOLO("yolov8n.pt")
    print("✅ YOLOv8 Model Loaded Successfully.")
except Exception as e:
    print(f"❌ Error loading YOLO: {e}")
    image_model = None

# --- REAL AUDIO LOGIC (Signal Processing) ---
def analyze_audio_real(file_path):
    """
    Calculates threat based on Volume (RMS) and Pitch (Spectral Centroid).
    High volume + High pitch (screeching/engines) = High Threat.
    """
    try:
        # Load audio (downsample to 22k for speed)
        y, sr = librosa.load(file_path, sr=22050, duration=5.0)
        
        # 1. Calculate Loudness (Root Mean Square)
        rms = np.mean(librosa.feature.rms(y=y))
        # Normalize RMS (Assuming 0.1 is very loud for underwater)
        loudness_score = min(100, (rms / 0.05) * 100)
        
        # 2. Calculate Frequency Sharpness (Spectral Centroid)
        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        # Normalize (Engines usually hit 1000Hz+)
        freq_score = min(100, (centroid / 3000) * 100)
        
        # Combined Score (60% Loudness, 40% Frequency)
        final_score = (loudness_score * 0.6) + (freq_score * 0.4)
        
        # Noise floor filter (if it's silent, return 0)
        if final_score < 10: return 0
        
        return int(final_score)
    except Exception as e:
        print(f"Audio Error: {e}")
        return 0

# --- REAL IMAGE LOGIC (Spatial Slicing) ---
def analyze_quadrant(image_slice_path):
    """
    Runs YOLOv8 on a specific slice of the image.
    """
    if not image_model: return 0
    try:
        results = image_model(image_slice_path, verbose=False)
        threat_score = 0
        
        # COCO Classes: 8=Boat, 0=Person, 4=Airplane
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                if cls_id == 8: # Boat/Ship
                    threat_score += 80 * conf # High threat
                elif cls_id == 0: # Person (Swimmer/Diver)
                    threat_score += 40 * conf
                elif cls_id == 4: # Airplane/Drone
                    threat_score += 60 * conf
                else:
                    threat_score += 5 * conf # Debris/Unknown
        
        return min(100, int(threat_score))
    except Exception as e:
        print(f"Image Error: {e}")
        return 0

@app.post("/scan-area")
async def scan_area(
    lat: float = Form(...),
    lng: float = Form(...),
    audio_file: UploadFile = File(...),
    image_file: UploadFile = File(...)
):
    # 1. Save uploaded files
    a_path = f"{TEMP_DIR}/{audio_file.filename}"
    i_path = f"{TEMP_DIR}/{image_file.filename}"
    
    with open(a_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    with open(i_path, "wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    # 2. Analyze Audio (Global for the area)
    # Sound travels far underwater, so we assume it applies to the whole sector roughly
    base_audio_risk = analyze_audio_real(a_path)

    # 3. Analyze Image (Split into 4 Quadrants)
    # We slice the image into 4 parts to get REAL location data
    original_img = Image.open(i_path)
    width, height = original_img.size
    mid_x, mid_y = width // 2, height // 2

    # Define Crops: (left, top, right, bottom)
    # NW (Top-Left), NE (Top-Right), SW (Bottom-Left), SE (Bottom-Right)
    sectors_info = [
        {"id": "ALPHA-1", "name": "NW Sector (Top-Left)", "crop": (0, 0, mid_x, mid_y), "lat": lat + 0.005, "lng": lng - 0.005},
        {"id": "BETA-2",  "name": "NE Sector (Top-Right)", "crop": (mid_x, 0, width, mid_y), "lat": lat + 0.005, "lng": lng + 0.005},
        {"id": "GAMMA-3", "name": "SW Sector (Btm-Left)", "crop": (0, mid_y, mid_x, height), "lat": lat - 0.005, "lng": lng - 0.005},
        {"id": "DELTA-4", "name": "SE Sector (Btm-Right)", "crop": (mid_x, mid_y, width, height), "lat": lat - 0.005, "lng": lng + 0.005},
    ]

    results = []

    for sector in sectors_info:
        # Create temp file for the crop
        crop_path = f"{TEMP_DIR}/{sector['id']}.jpg"
        cropped_img = original_img.crop(sector['crop'])
        cropped_img.save(crop_path)
        
        # Analyze ONLY this part of the image
        visual_risk = analyze_quadrant(crop_path)
        
        # Audio attenuates slightly over distance (simulation logic for realism)
        # We assume the hydrophone is at the center, so risk is constant-ish
        audio_risk = base_audio_risk 

        # Fusion: Total Threat
        total_score = int((audio_risk * 0.5) + (visual_risk * 0.5))
        
        # Classification
        if total_score > 75: 
            level, color = "HIGH", "red"
        elif total_score > 30: 
            level, color = "MEDIUM", "yellow"
        else: 
            level, color = "LOW", "green"
            
        results.append({
            "id": sector['id'],
            "name": sector['name'],
            "lat": sector['lat'],
            "lng": sector['lng'],
            "audio_score": audio_risk,
            "image_score": visual_risk,
            "total_score": total_score,
            "level": level,
            "color": color
        })
        
        # Clean up crop
        if os.path.exists(crop_path): os.remove(crop_path)

    # Cleanup main files
    # if os.path.exists(a_path): os.remove(a_path)
    # if os.path.exists(i_path): os.remove(i_path)

    return {"status": "success", "data": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)