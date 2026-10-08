# AI-Based Smart Traffic Violation Detection and Enforcement System

Production-style local prototype: a PySide6 CCTV monitor with editable road zones, temporal violation rules, reviewable evidence, SQLite persistence, and a FastAPI review API.

## Setup

Requires Python 3.11+. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For real detection, install `pip install ultralytics` and place a suitable YOLO model at `models/yolo11n.pt` (or change `config/app_config.json`). For OCR, install `easyocr`. Neither is required to open video and configure zones.

## Run

```powershell
python main.py
uvicorn backend.api:app --reload
```

The dashboard is served at `http://127.0.0.1:8000/dashboard/`; API docs are at `http://127.0.0.1:8000/docs`.

Enter an MP4 path, `0` for the default webcam, or an `rtsp://...` URL, then click **Connect**. The processing worker never blocks the GUI thread.

## Zone editing

Choose a tool, then click on the live frame. No Parking and Free Left polygons need 3+ vertices and finish on double-click. Stop Lines take two clicks. Signal ROI takes opposite rectangle corners. Right-click cancels the in-progress shape. Use Save zones to persist `config/zones.json`; select an item in the list to delete it.

No-parking uses a vehicle's bottom-centre point, starts a configurable 10-second grace timer, warns once, and confirms persistence after the configurable 5-second post-alarm window. Red-light crossings require the manual signal selector to be RED. Confirmed cases are designed for ANPR/evidence/database submission only—not automatic fines.

Evidence is saved below `evidence/YYYY-MM-DD/<violation-id>/`; configuration values live in `config/app_config.json`. Logs are written to `logs/app.log`.

## Tests

```powershell
python -m pytest tests -q
```

Hardware specifics: webcam permissions and RTSP credentials/network access must be configured on the host. The optional YOLO/OCR model downloads are external requirements.
