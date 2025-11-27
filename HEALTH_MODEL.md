# Plant health detector workflow

This repository already contains the scripts you need to turn PlantDoc into a healthy vs unhealthy YOLO dataset, fine‑tune a detector, and run it live on the rover. The flow below keeps everything reproducible so you can hand the weights to your teammate’s UI when it is ready.

## 1. Prepare the dataset

1. Download and unzip the original PlantDoc object detection dataset into `datasets/PlantDoc-Object-Detection-Dataset` (already present in this repo).
2. Decide which PlantDoc classes you want to treat as **healthy**. The converter ships with a reasonable default list (see `DEFAULT_HEALTHY_CLASSES` inside `tools/csvtoyolo.py`), but you can override it by passing a text file with one class per line.
3. Convert the CSVs into YOLO format with the new health-aware options:
   ```bash
   python tools/csvtoyolo.py \
       --health-split \
       --health-healthy-list tools/healthy_classes.txt  # optional \
       --out-root datasets/plantdoc_health_yolo
   ```
   - Use `--class-map mapping.json` if you want a custom class remap (e.g., healthy/diseased/specific disease types).
   - Use `--drop-unmapped` to skip boxes whose class does not appear in the JSON map.
   - The script prints how many train/val images were written and drops a ready-to-use `dataset.yaml` into the target directory.

## 2. Train the model

1. Pick the Ultralytics checkpoint you want to fine-tune (`yolov8n.pt` is fast, `yolov8s.pt` is more accurate).
2. Launch training with the helper script (adjust hyper-parameters to taste):
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
3. The script automatically picks the best available device (MPS → CUDA → CPU). Override with `--device cpu|cuda|mps` when needed.
4. Monitor Ultralytics’ console output or open `runs/health/yolov8s_health/results.png` to double-check mAP and class balance. Increase epochs/batch or switch to a larger backbone if you need more accuracy.
5. To iterate quickly, edit `DEFAULT_HEALTHY_CLASSES`, regenerate the dataset, and re-run the script. You can also resume a previous run with `--resume`.

### Extra accuracy tips

- Clean up noisy PlantDoc labels (several raw images include multiple crops of the same leaf). Use `detect_webcam.py` to capture additional rover-specific imagery and add it to the dataset to reduce domain shift.
- Try a larger base checkpoint (`yolov8m.pt`) and/or higher resolution (`--imgsz 960`) if latency allows it.
- Ultralytics exposes many knobs via `model.train(...)`. You can clone `train_health_model.py` and tweak `lr0`, `close_mosaic`, `patience`, etc., or experiment with `--class-map` to keep certain disease classes separate instead of binning everything into “unhealthy.”

## 3. Run live inference

1. Point the webcam script at your freshly trained weights (any `.pt` from `runs/health/.../weights/`):
   ```bash
   python src/webcam_predict.py \
       --weights runs/health/yolov8s_health/weights/best.pt \
       --conf 0.35 \
       --source 0 \
       --health-labels healthy unhealthy
   ```
2. The HUD now shows a running tally of healthy vs unhealthy detections plus the total box count so you can forward the aggregated status to the UI or rover logic.
3. Adjust `--width/--height` for your USB camera and use `--imgsz` for the inference resolution. Pass a RTSP/HTTP stream into `--source` if you want to test from prerecorded footage.

## 4. Integrate with the UI / rover logic

- `webcam_predict.py` already exposes CLI flags for weights, confidence, and labels. Your teammate's UI can invoke it as a subprocess or directly import the helper functions to grab the annotated frame + summary string.
- If you need a programmatic API, refactor the main loop into a generator that yields `(annotated_frame, summary_dict)`; the current structure keeps that change straightforward.
- Once the UI is ready, agree on the schema for the health summary (e.g., JSON with counts per class) and extend `build_summary` to emit that shape.

## 5. What to do next

- Collect rover-specific footage (sun glare, night shots, different heights) and fine-tune again so the detector generalizes to your deployment domain.
- Consider adding a third class such as `unknown` or `background` via `--class-map` if you notice many false positives on non-plant objects.
- When you are ready to deploy on the rover, convert the trained weights to ONNX/CoreML/TensorRT using `ultralytics export` so the UI can run them efficiently on the edge device.
