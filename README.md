# Plant Rover (Healthy vs Unhealthy Plants)

This repository powers your rover’s plant-health workflow end-to-end:

- Converts PlantDoc labels into YOLO format and lets you map classes to healthy/unhealthy (`tools/csvtoyolo.py`, `tools/healthy_classes.txt`).
- Fine-tunes YOLOv8 detectors for real-time plant-health inference (`src/train_health_model.py`).
- Streams annotated webcam footage to your teammate’s RoverUI dashboard (`src/ui_stream_server.py` + `RoverUI-main/`).

Follow the sections below to prepare data, train, test, and launch the web UI.

---

## 1. Setup (Python side)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install ultralytics opencv-python torch torchvision flask flask-cors
python src/check_env.py  # confirms PyTorch+device
```

> On Apple Silicon, install the official MPS wheels from pytorch.org.

## 2. Prepare the PlantDoc dataset

1. Download/unzip [PlantDoc (object detection)](https://github.com/pratikkayal/PlantDoc-Dataset) into `datasets/PlantDoc-Object-Detection-Dataset/`.
2. Convert to YOLO format with the health split:
   ```bash
   python tools/csvtoyolo.py \
       --health-split \
       --health-healthy-list tools/healthy_classes.txt \
       --out-root datasets/plantdoc_health_yolo
   ```
   - Edit `tools/healthy_classes.txt` or pass a custom file to change which classes count as “healthy”.
   - Use `--class-map mapping.json` for custom label remaps.
   - Outputs live under `datasets/plantdoc_health_yolo/` with `dataset.yaml` for Ultralytics.

## 3. Train a YOLOv8 model

Typical run (tweak epochs/backbone as needed):
```bash
python src/train_health_model.py \
    --data datasets/plantdoc_health_yolo/dataset.yaml \
    --model yolov8s.pt \
    --epochs 150 \
    --batch 16 \
    --imgsz 640 \
    --project runs/health \
    --name yolov8s_health
```

Quick macOS-friendly run:
```bash
python src/train_health_model.py \
    --data datasets/plantdoc_health_yolo/dataset.yaml \
    --model yolov8n.pt \
    --epochs 40 \
    --batch 8 \
    --imgsz 512 \
    --project runs/health \
    --name yolov8n_health_fast
```

- Automatically picks `mps` → `cuda` → `cpu`; override with `--device`.
- Results: `runs/health/<name>/weights/best.pt`, `results.png`, `results.csv`, etc.
- Env var `PYTORCH_ENABLE_MPS_FALLBACK=1` is set automatically for MPS NMS compatibility.

## 4. Local webcam test (optional)

```bash
python src/webcam_predict.py \
    --weights runs/health/<run>/weights/best.pt \
    --conf 0.35 \
    --source 0 \
    --health-labels healthy unhealthy
```
Press `q` to exit. This shows detections in an OpenCV window outside the UI.

## 5. Stream detections to RoverUI

1. **Start the streaming backend** (MJPEG + JSON endpoints):
   ```bash
   python src/ui_stream_server.py \
       --weights runs/health/<run>/weights/best.pt \
       --conf 0.35 \
       --source 0 \
       --port 8000
   ```
   Endpoints:
   - `http://localhost:8000/video_feed` – annotated MJPEG stream
   - `http://localhost:8000/health` – JSON counts per class

2. **Run the RoverUI frontend** (Node 18+, npm):
   ```bash
   cd RoverUI-main
   npm install
   # Optional override if backend runs elsewhere:
   echo "VITE_STREAM_URL=http://localhost:8000/video_feed" > .env
   npm run dev -- --host
   ```
   Visit the printed Vite URL (usually `http://localhost:5173`). The Dashboard’s Live Camera Feed now shows the annotated stream and pause overlay as before.

3. **Dependencies**:
   - Node modules listed in `RoverUI-main/package.json` (Shadcn UI, Vite 6.x, etc.).
   - `npm audit` currently reports a moderate Vite dev-server advisory; safe to ignore for local development or upgrade when convenient (`npm audit fix --force`).

## 6. Repository hygiene & syncing

- `.gitignore` already excludes heavy artifacts: datasets/, `runs/`, `.venv/`, `*.pt`, etc.
- To version code:
  ```bash
  git init
  git add .
  git commit -m "Initial plant rover repo"
  git remote add origin <YOUR_GITHUB_URL>
  git branch -M main
  git push -u origin main
  ```
- If you train on another PC, copy `datasets/plantdoc_health_yolo` there, run training, and copy the resulting `runs/health/<run>/weights/best.pt` back for inference/UI.

## 7. Files of interest

- `src/train_health_model.py` – CLI for Ultralytics training.
- `src/ui_stream_server.py` – Flask bridge powering the UI feed.
- `src/webcam_predict.py` – standalone webcam viewer/debugger.
- `tools/csvtoyolo.py` – dataset converter with health split, class maps, and output directory control.
- `RoverUI-main/src/components/Dashboard.tsx` – loads the stream URL without altering the UI design.
- `HEALTH_MODEL.md` – broader workflow tips, accuracy advice, and UI integration notes.

You’re ready to start training, streaming, and showing plant-health detections inside the UI. Let me know when you need export scripts (ONNX/CoreML) or cloud deployment guidance.
