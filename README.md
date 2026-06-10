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

Neela Bhavya Sri


## License

MIT License
<img width="1920" height="1128" alt="Screenshot 2026-06-10 135551" src="https://github.com/user-attachments/assets/44e5a8ba-26a5-48d5-a5e4-4e42e6deff63" />
<img width="1920" height="1128" alt="Screenshot 2026-06-10 135528" src="https://github.com/user-attachments/assets/5e919db3-0ca6-4b5e-bc59-8743a5432cab" />


