#!/usr/bin/env python3
# Converts Pascal VOC XML in PlantDoc-Object-Detection-Dataset to YOLOv8 format.
# Usage:
#   python tools/voc_to_yolo.py --src datasets/PlantDoc-Object-Detection-Dataset --collapse-to-plant
from pathlib import Path
import argparse, xml.etree.ElementTree as ET, shutil

def parse_voc(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find("size")
    if size is None: return [], None, None
    w = float(size.find("width").text); h = float(size.find("height").text)
    boxes = []
    for obj in root.findall("object"):
        name = (obj.find("name").text or "").strip()
        bb = obj.find("bndbox")
        if bb is None: continue
        xmin = float(bb.find("xmin").text); ymin = float(bb.find("ymin").text)
        xmax = float(bb.find("xmax").text); ymax = float(bb.find("ymax").text)
        # sanity
        if xmax <= xmin or ymax <= ymin or w <= 0 or h <= 0: continue
        boxes.append((name, xmin, ymin, xmax, ymax, w, h))
    return boxes, w, h

def yolo_line(xmin, ymin, xmax, ymax, w, h, cid):
    bw, bh = xmax - xmin, ymax - ymin
    xc, yc = xmin + bw/2, ymin + bh/2
    return f"{cid} {xc/w:.6f} {yc/h:.6f} {bw/w:.6f} {bh/h:.6f}"

def convert_split(split_dir: Path, out_img: Path, out_lbl: Path, class_map: dict, collapse: bool):
    out_img.mkdir(parents=True, exist_ok=True)
    out_lbl.mkdir(parents=True, exist_ok=True)
    count = 0
    for xml in split_dir.glob("*.xml"):
        stem = xml.stem
        img = None
        # common extensions, try exact and case-insensitive
        for ext in [".jpg", ".jpeg", ".png"]:
            cand = split_dir / f"{stem}{ext}"
            if cand.exists(): img = cand; break
        if img is None:
            matches = [p for p in split_dir.iterdir() if p.stem.lower()==stem.lower() and p.suffix.lower() in [".jpg",".jpeg",".png"]]
            if matches: img = matches[0]
        if img is None:
            print(f"[WARN] image for {xml.name} not found"); continue

        anns, w, h = parse_voc(xml)
        # copy image
        shutil.copy2(img, out_img / img.name)
        # write labels (empty file allowed)
        lines = []
        for (name, xmin, ymin, xmax, ymax, w, h) in anns:
            cls = "plant" if collapse else name
            cid = class_map.setdefault(cls, len(class_map))
            lines.append(yolo_line(xmin, ymin, xmax, ymax, w, h, cid))
        (out_lbl / f"{img.stem}.txt").write_text("\n".join(lines))
        count += 1
    return count, class_map

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True, help="datasets/PlantDoc-Object-Detection-Dataset")
    ap.add_argument("--out", type=Path, default=Path("datasets/plantdoc_yolo"))
    ap.add_argument("--collapse-to-plant", action="store_true", help="Map all classes to 'plant'")
    args = ap.parse_args()

    train_dir = args.src / "TRAIN"
    test_dir  = args.src / "TEST"
    if not train_dir.exists() or not test_dir.exists():
        raise SystemExit(f"Missing TRAIN/TEST in {args.src}")

    out_tr_img = args.out / "images" / "train"
    out_va_img = args.out / "images" / "val"
    out_tr_lbl = args.out / "labels" / "train"
    out_va_lbl = args.out / "labels" / "val"

    classes = {}
    ntr, classes = convert_split(train_dir, out_tr_img, out_tr_lbl, classes, args.collapse_to_plant)
    nva, classes = convert_split(test_dir,  out_va_img, out_va_lbl, classes, args.collapse_to_plant)

    names = [None]*len(classes)
    for k,v in classes.items(): names[v]=k
    (args.out / "dataset.yaml").write_text(
        f"path: {args.out.as_posix()}\ntrain: images/train\nval: images/val\nnames: {names}\n"
    )
    print("✅ VOC → YOLO done")
    print(" Train imgs:", ntr, " Val imgs:", nva)
    print(" Classes:", classes)
    print(" YAML:", args.out / "dataset.yaml")

if __name__ == "__main__":
    main()
