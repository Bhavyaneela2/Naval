import os

# Create directories
os.makedirs("static", exist_ok=True)
os.makedirs("temp_uploads", exist_ok=True)
os.makedirs("models", exist_ok=True)

# 1. HTML FILE
html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Naval Threat Surveillance</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar">
    <div class="brand"><i class="fas fa-anchor"></i> NAVAL HYDRO SYSTEM</div>
    <div class="status"><i class="fas fa-circle" style="font-size:10px;"></i> SYSTEM ONLINE</div>
</nav>
<div class="container">
    <!-- PAGE 1 -->
    <div id="page-1">
        <h2><i class="fas fa-crosshairs"></i> Target Acquisition</h2>
        <div class="input-panel">
            <div id="map-select" style="height: 400px; width: 100%; border: 1px solid #334155;"></div>
            <div>
                <form id="scanForm">
                    <label>COORDINATES</label>
                    <div style="display:flex; gap:10px;">
                        <input type="text" id="lat" placeholder="Lat" readonly>
                        <input type="text" id="lng" placeholder="Lng" readonly>
                    </div>
                    <label>HYDROPHONE AUDIO</label>
                    <input type="file" id="audioFile" accept="audio/*">
                    <label>SURFACE IMAGERY</label>
                    <input type="file" id="imageFile" accept="image/*">
                    <br><br>
                    <button type="button" onclick="startScan()">INITIATE THREAT SCAN</button>
                </form>
            </div>
        </div>
    </div>
    <!-- PAGE 2 -->
    <div id="page-2" class="hidden loader-box">
        <h1>PROCESSING SENSOR DATA</h1>
        <p>Running TensorFlow Audio CNN... Running YOLOv8 Object Detection...</p>
        <div class="bar-container"><div class="bar-fill" id="loaderBar"></div></div>
        <p id="logText" style="color: #38bdf8; font-family: monospace;">> Initializing modules...</p>
    </div>
    <!-- PAGE 3 -->
    <div id="page-3" class="hidden">
        <div style="display:flex; justify-content:space-between;">
            <h2><i class="fas fa-chart-pie"></i> Tactical Debrief Report</h2>
            <button onclick="location.reload()" style="width: auto;">NEW SCAN</button>
        </div>
        <div id="cards-container" class="grid-4"></div>
        <div class="charts-area">
            <div class="chart-box"><h3>Threat Intensity Map</h3><div id="result-map" style="height: 300px;"></div></div>
            <div class="chart-box"><h3>Audio vs Visual Risk</h3><canvas id="riskChart"></canvas></div>
        </div>
    </div>
</div>
<script src="script.js"></script>
</body>
</html>"""

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html_code)

# 2. CSS FILE
css_code = """
:root { --bg-dark: #0f172a; --panel-bg: #1e293b; --neon-blue: #38bdf8; --neon-red: #f87171; --neon-yellow: #facc15; --neon-green: #4ade80; --text-white: #f8fafc; }
body { background-color: var(--bg-dark); color: var(--text-white); font-family: 'Segoe UI', sans-serif; margin: 0; }
.navbar { display: flex; justify-content: space-between; padding: 15px 30px; background: #020617; border-bottom: 2px solid var(--panel-bg); }
.brand { font-weight: bold; font-size: 1.2rem; letter-spacing: 2px; }
.status { color: var(--neon-green); font-family: monospace; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.hidden { display: none; }
.input-panel { background: var(--panel-bg); padding: 30px; border-radius: 8px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
input, button { width: 100%; padding: 12px; margin-top: 10px; background: var(--bg-dark); border: 1px solid #475569; color: white; box-sizing: border-box; }
button { background: var(--neon-blue); color: black; font-weight: bold; cursor: pointer; border: none; }
button:hover { opacity: 0.9; }
.loader-box { text-align: center; margin-top: 100px; }
.bar-container { width: 50%; height: 20px; background: #333; margin: 20px auto; border-radius: 10px; overflow: hidden; }
.bar-fill { height: 100%; width: 0%; background: var(--neon-blue); transition: width 0.5s; }
.grid-4 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }
.card { padding: 20px; border-radius: 6px; border-left: 5px solid white; }
.card.red { background: linear-gradient(145deg, #450a0a, #7f1d1d); border-color: var(--neon-red); }
.card.yellow { background: linear-gradient(145deg, #422006, #713f12); border-color: var(--neon-yellow); }
.card.green { background: linear-gradient(145deg, #052e16, #14532d); border-color: var(--neon-green); }
.score-big { font-size: 3rem; font-weight: bold; margin: 10px 0; }
.charts-area { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
.chart-box { background: var(--panel-bg); padding: 15px; border-radius: 8px; }
"""

with open("static/style.css", "w", encoding="utf-8") as f:
    f.write(css_code)

# 3. JS FILE
js_code = """
const map = L.map('map-select').setView([20.0, 80.0], 5);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);
let marker;
map.on('click', (e) => {
    if (marker) map.removeLayer(marker);
    marker = L.marker(e.latlng).addTo(map);
    document.getElementById('lat').value = e.latlng.lat.toFixed(5);
    document.getElementById('lng').value = e.latlng.lng.toFixed(5);
});

async function startScan() {
    const lat = document.getElementById('lat').value;
    const audio = document.getElementById('audioFile').files[0];
    const image = document.getElementById('imageFile').files[0];
    
    if (!lat || !audio || !image) { alert("Please select a location and upload files."); return; }
    
    document.getElementById('page-1').classList.add('hidden');
    document.getElementById('page-2').classList.remove('hidden');
    
    let width = 0;
    const interval = setInterval(() => { width += 5; document.getElementById('loaderBar').style.width = width + '%'; if(width > 90) clearInterval(interval); }, 100);
    
    const formData = new FormData();
    formData.append('lat', lat); formData.append('lng', document.getElementById('lng').value);
    formData.append('audio_file', audio); formData.append('image_file', image);
    
    try {
        const res = await fetch('/scan-area', { method: 'POST', body: formData });
        const data = await res.json();
        document.getElementById('loaderBar').style.width = '100%';
        setTimeout(() => renderDashboard(data.data), 500);
    } catch (err) { alert("Error connecting to AI Engine"); console.error(err); }
}

function renderDashboard(zones) {
    document.getElementById('page-2').classList.add('hidden');
    document.getElementById('page-3').classList.remove('hidden');
    const container = document.getElementById('cards-container'); container.innerHTML = '';
    const resMap = L.map('result-map').setView([zones[0].lat, zones[0].lng], 13);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(resMap);
    
    const labels = []; const aScores = []; const iScores = [];
    zones.forEach(z => {
        const card = document.createElement('div');
        card.className = `card ${z.color}`;
        card.innerHTML = `<div style="font-size:0.8rem; opacity:0.8;">${z.id} // ${z.name}</div><div class="score-big">${z.total_score}%</div><div style="font-size:0.8rem;">LEVEL: ${z.level}</div><small>Audio: ${z.audio_score} | Image: ${z.image_score}</small>`;
        container.appendChild(card);
        const bounds = [[z.lat - 0.002, z.lng - 0.002], [z.lat + 0.002, z.lng + 0.002]];
        let cHex = z.color === 'red' ? '#f87171' : (z.color === 'yellow' ? '#facc15' : '#4ade80');
        L.rectangle(bounds, { color: cHex, weight: 1 }).addTo(resMap).bindPopup(`<b>${z.id}</b>: ${z.level}`);
        labels.push(z.id); aScores.push(z.audio_score); iScores.push(z.image_score);
    });
    
    new Chart(document.getElementById('riskChart'), {
        type: 'bar',
        data: { labels: labels, datasets: [{ label: 'Audio', data: aScores, backgroundColor: '#38bdf8' }, { label: 'Visual', data: iScores, backgroundColor: '#c084fc' }] },
        options: { scales: { y: { beginAtZero: true, max: 100, grid: { color: '#334155'} } }, plugins: { legend: { labels: { color: 'white' } } } }
    });
}
"""

with open("static/script.js", "w", encoding="utf-8") as f:
    f.write(js_code)

# 4. MAIN BACKEND FILE
py_code = """
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
"""

with open("main.py", "w", encoding="utf-8") as f:
    f.write(py_code)

print("✅ Files created successfully!")