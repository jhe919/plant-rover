# Plant Rover (Healthy vs Unhealthy Plants)

This repo trains and runs a YOLOv8 detector to tell whether leaves seen by your rover’s camera look healthy or unhealthy. It contains:

- A converter that turns the PlantDoc dataset CSVs into YOLO format with optional class remapping (`tools/csvtoyolo.py`).
- A training helper that fine-tunes YOLOv8 (GPU or CPU) on the binary “healthy vs unhealthy” task (`src/train_health_model.py`).
- Webcam utilities to test the trained weights live, plus scripts to check the camera, capture raw frames, etc (`src/webcam_predict.py`, `src/detect_webcam.py`, `src/test_camera.py`).
- Documentation (`HEALTH_MODEL.md`) outlining the full pipeline and integration tips for your teammate’s UI.

## Setup

1. **Install dependencies** (macOS example):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install ultralytics opencv-python torch torchvision
   ```
   On Apple Silicon, be sure you install the Metal (MPS) build of PyTorch per the [official instructions](https://pytorch.org/get-started/locally/).

2. **Check the environment**:
   ```bash
   python src/check_env.py
   ```
   Confirms Python/Torch versions and whether MPS/CUDA/CPU are available.

## Prepare the dataset

1. Download and unzip the original PlantDoc Object Detection dataset into `datasets/PlantDoc-Object-Detection-Dataset` (already in this repo for local use).
2. Convert the CSVs to YOLO format with the health split:
   ```bash
   python tools/csvtoyolo.py \
       --health-split \
       --health-healthy-list tools/healthy_classes.txt \
       --out-root datasets/plantdoc_health_yolo
   ```
   - Edit `tools/healthy_classes.txt` or pass your own file to control which PlantDoc labels count as “healthy”.
   - Use `--class-map mapping.json` if you need more than two classes.
   - The script writes `dataset.yaml` under the chosen output directory.

## Train a model

Use the helper script to fine-tune any YOLOv8 checkpoint:
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

- The script automatically picks the best device (`mps` → `cuda` → `cpu`). Override with `--device`.
- For quick experiments on macOS, try `--model yolov8n.pt --epochs 40 --batch 8 --imgsz 512`.
- Outputs (weights, metrics, plots) land under `runs/health/<name>/`.
- See `HEALTH_MODEL.md` for tuning ideas and accuracy tips.

## Run live webcam inference

1. Connect your camera and run:
   ```bash
   python src/webcam_predict.py \
       --weights runs/health/yolov8s_health/weights/best.pt \
       --conf 0.35 \
       --source 0 \
       --health-labels healthy unhealthy
   ```
2. The OpenCV window draws detections and shows a HUD with healthy/unhealthy counts plus the total number of boxes. Press `q` to quit.
3. Adjust `--source` for other cameras/streams, `--imgsz` for inference size, and `--width/--height` to match your rover camera.

Utility scripts:
- `src/test_camera.py`: verify the webcam feed without YOLO.
- `src/detect_webcam.py`: run the stock YOLOv8 model for comparison and dataset collection (`S` key saves frames).
- `tools/csvtoyolo.py`: regenerate YOLO labels if you tweak classes or add custom imagery.

## Status & next steps

Right now the project trains binary healthy/unhealthy detectors and visualizes counts in real time. Upcoming work:
- Integrate the webcam loop with your teammate’s UI (see ideas in `HEALTH_MODEL.md`).
- Export trained weights to ONNX/CoreML/TensorRT if you deploy to embedded hardware.
- Collect rover-specific footage to fine-tune on your target environment for better accuracy.

Questions? Run `python src/webcam_predict.py --help` or open an issue in this repo.
