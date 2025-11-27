#!/usr/bin/env python3
"""
Convenience script to fine-tune a YOLOv8 detector that classifies plants as healthy vs unhealthy.

Usage:
    python src/train_health_model.py --data datasets/plantdoc_health_yolo/dataset.yaml
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

# Torchvision NMS is not implemented on MPS; allow CPU fallback by default.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import torch
from ultralytics import YOLO

DEFAULT_DATA = Path("datasets/plantdoc_health_yolo/dataset.yaml")


def choose_device(pref: str) -> str:
    if pref != "auto":
        return pref
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Train a healthy vs unhealthy plant detector.")
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA,
                    help=f"YOLO dataset yaml (default: {DEFAULT_DATA}).")
    ap.add_argument("--model", default="yolov8n.pt",
                    help="Base model checkpoint to fine-tune (e.g. yolov8n.pt, yolov8s.pt).")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--imgsz", type=int, default=640,
                    help="Training image size (square).")
    ap.add_argument("--lr0", type=float, default=0.01,
                    help="Initial learning rate.")
    ap.add_argument("--patience", type=int, default=20,
                    help="Early-stopping patience based on mAP50-95.")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    ap.add_argument("--project", default="runs/health",
                    help="Folder under runs/ used by Ultralytics.")
    ap.add_argument("--name", default="yolov8n_health",
                    help="Run name (sub-folder under project).")
    ap.add_argument("--resume", action="store_true",
                    help="Resume the latest run in the same project/name.")
    ap.add_argument("--workers", type=int, default=8,
                    help="Number of dataloader workers.")
    ap.add_argument("--close-mosaic", type=int, default=15,
                    help="Disable mosaic augmentation for the last N epochs.")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    if not args.data.exists():
        raise SystemExit(f"Dataset yaml not found: {args.data}. Run tools/csvtoyolo.py first.")

    device = choose_device(args.device)
    print(f"[health-train] Using device={device}")
    if device == "mps":
        print("[health-train] PYTORCH_ENABLE_MPS_FALLBACK=1 (CPU fallback for ops missing on MPS).")

    model = YOLO(args.model)
    model.train(
        data=args.data.as_posix(),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        lr0=args.lr0,
        patience=args.patience,
        device=device,
        project=args.project,
        name=args.name,
        workers=args.workers,
        close_mosaic=args.close_mosaic,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
