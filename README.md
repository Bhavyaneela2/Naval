# README.md
# Naval Threat Surveillance System

AI-powered Naval Threat Detection and Surveillance System using:

- FastAPI
- YOLOv8
- Librosa Audio Analysis
- Leaflet Maps
- Chart.js
- Computer Vision
- Audio Signal Processing

## Features

- Real-time naval threat analysis
- Underwater hydrophone audio analysis
- YOLOv8 object detection
- Threat intensity visualization
- Interactive tactical dashboard
- Sector-based risk analysis
- Heatmap-style threat zones
## Tech Stack

### Backend
- FastAPI
- Python
- YOLOv8 (Ultralytics)
- OpenCV
- Librosa
- NumPy
- Pillow

### Frontend
- HTML
- CSS
- JavaScript
- Leaflet.js
- Chart.js
<img width="1920" height="1128" alt="Screenshot 2026-06-10 135551" src="https://github.com/user-attachments/assets/b9cbea64-8631-4240-97f4-4da11e0def7c" />
<img width="1920" height="1128" alt="Screenshot 2026-06-10 135528" src="https://github.com/user-attachments/assets/8bbd072d-cecb-4ed1-b0e4-bd9829092365" />

## Project Structure

```bash
naval/
│
├── main.py
├── requirements.txt
├── yolov8n.pt
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── temp_uploads/
│
└── venv/

## Installation

### Clone Repository

git clone https://github.com/Bhavyaneela2/Naval.git
cd Naval

### Create Virtual Environment
python -m venv venv


### Activate Virtual Environment

#### Windows
venv\Scripts\activate


#### Linux / Mac
source venv/bin/activate

### Install Dependencies
pip install -r requirements.txt


## Run Project
uvicorn main:app --reload


Open:
http://localhost:8000/static/index.html


## Deployment

Deployed using Render.

Start Command:
uvicorn main:app --host 0.0.0.0 --port 10000


## System Workflow

1. User selects target coordinates
2. Uploads hydrophone audio
3. Uploads surface imagery
4. AI engine processes:

   * Audio threat analysis
   * YOLOv8 object detection
5. Dashboard displays:

   * Threat score
   * Sector classification
   * Tactical map
   * Risk comparison charts



## Threat Classification

| Score Range | Level  |
| ----------- | ------ |
| 0-30        | LOW    |
| 31-75       | MEDIUM |
| 76-100      | HIGH   |



## Author

Neela Bhavya sri
Nunugonda Sankeerthana
Chitala Bhavana<img width="1920" height="1128" alt="Screenshot 2026-06-10 135551" src="https://github.com/user-attachments/assets/19877ba0-f7c9-4a2f-aced-8fbb73e4114a" />
<img width="1920" height="1128" alt="Screenshot 2026-06-10 135528" src="https://github.com/user-attachments/assets/e5a0edc9-6441-477b-be4e-8096cbda33c6" />

