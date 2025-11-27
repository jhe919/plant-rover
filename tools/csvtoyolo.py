#!/usr/bin/env python3
from pathlib import Path
import shutil, csv, argparse, json
from collections import defaultdict

OD_ROOT = Path("datasets/PlantDoc-Object-Detection-Dataset")

DEFAULT_OUT_ROOT = Path("datasets/plantdoc_yolo")

# Default PlantDoc classes that we roughly treat as "healthy" foliage.
# Edit or override via --health-healthy-list to better match your dataset.
DEFAULT_HEALTHY_CLASSES = {
    "Apple leaf",
    "Bell_pepper leaf",
    "Blueberry leaf",
    "Cherry leaf",
    "Peach leaf",
    "Potato leaf",
    "Raspberry leaf",
    "Soyabean leaf",
    "Strawberry leaf",
    "Tomato leaf",
    "grape leaf",
}

CANDIDATE_COLS = {
    "filename": ["filename","file","image","image_name","img_name"],
    "width":    ["width","img_width","image_width","w"],
    "height":   ["height","img_height","image_height","h"],
    "class":    ["class","label","category","name"],
    "xmin":     ["xmin","x_min","x1","left"],
    "ymin":     ["ymin","y_min","y1","top"],
    "xmax":     ["xmax","x_max","x2","right"],
    "ymax":     ["ymax","y_max","y2","bottom"],
}

def map_header(header_row):
    lower = {h.lower().strip(): h for h in header_row}
    out = {}
    for k, alts in CANDIDATE_COLS.items():
        for a in alts:
            if a in lower:
                out[k] = lower[a]
                break
        if k not in out:
            raise ValueError(f"CSV missing required column like: {k} {CANDIDATE_COLS[k]}")
    return out

def yolo_line(w, h, xmin, ymin, xmax, ymax, class_id):
    bw, bh = xmax - xmin, ymax - ymin
    xc, yc = xmin + bw/2, ymin + bh/2
    return f"{class_id} {xc/w:.6f} {yc/h:.6f} {bw/w:.6f} {bh/h:.6f}"

def process_split(csv_path, img_dir, out_images, out_labels, class_to_id, class_mapper):
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    boxes = defaultdict(list)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        mapper = map_header(reader.fieldnames)
        for row in reader:
            fn = row[mapper["filename"]].strip()
            w  = float(row[mapper["width"]]);  h  = float(row[mapper["height"]])
            if w <= 0 or h <= 0:
                print(f"[WARN] Skipping {fn} due to invalid image size ({w}x{h}).")
                continue
            cls_raw = row[mapper["class"]].strip()
            xmin = float(row[mapper["xmin"]]); ymin = float(row[mapper["ymin"]])
            xmax = float(row[mapper["xmax"]]); ymax = float(row[mapper["ymax"]])
            cls = class_mapper(cls_raw) if class_mapper else cls_raw
            if cls is None:
                continue
            cid = class_to_id.setdefault(cls, len(class_to_id))
            boxes[fn].append((w,h,xmin,ymin,xmax,ymax,cid))

    copied = 0
    for fn, anns in boxes.items():
        src = img_dir / fn
        if not src.exists():
            cand = list(img_dir.rglob(Path(fn).name))
            if cand: src = cand[0]
            else:
                print(f"[WARN] Missing image in CSV: {fn}")
                continue
        dst_img = out_images / src.name
        shutil.copy2(src, dst_img)
        lbl_path = out_labels / (dst_img.stem + ".txt")
        with open(lbl_path, "w") as f:
            for (w,h,xmin,ymin,xmax,ymax,cid) in anns:
                f.write(yolo_line(w,h,xmin,ymin,xmax,ymax,cid) + "\n")
        copied += 1
    return copied, class_to_id

def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--collapse-to-plant", action="store_true",
                      help="Map all classes to a single 'plant' label (previous default).")
    mode.add_argument("--health-split", action="store_true",
                      help="Map PlantDoc labels to binary 'healthy' vs 'unhealthy' classes.")
    mode.add_argument("--class-map", type=Path,
                      help="Path to a JSON file {\"Original class\": \"new_name\", ...}.")
    ap.add_argument("--drop-unmapped", action="store_true",
                    help="When using --class-map, drop boxes whose class is missing from the map.")
    ap.add_argument("--health-healthy-list", type=Path,
                    help="Optional text file with one PlantDoc class per line treated as 'healthy'. "
                         "Defaults to a curated set of general foliage classes.")
    ap.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT,
                    help=f"Directory to write the YOLO dataset (default: {DEFAULT_OUT_ROOT}).")
    args = ap.parse_args()

    if not OD_ROOT.exists():
        raise SystemExit(f"Not found: {OD_ROOT}. Put the unzipped dataset there.")

    if args.class_map:
        raw_map = json.loads(args.class_map.read_text())
        if not isinstance(raw_map, dict):
            raise SystemExit("--class-map must point to a JSON object mapping class names.")
        def mapper(cls_raw):
            if cls_raw in raw_map:
                return raw_map[cls_raw]
            return None if args.drop_unmapped else cls_raw
        print(f"[class-map] Loaded {len(raw_map)} entries from {args.class_map}")
    elif args.health_split:
        if args.health_healthy_list:
            healthy = {
                line.strip() for line in args.health_healthy_list.read_text().splitlines() if line.strip()
            }
            print(f"[health-split] Loaded custom healthy set ({len(healthy)} classes).")
        else:
            healthy = set(DEFAULT_HEALTHY_CLASSES)
            print("[health-split] Using built-in healthy classes. Edit DEFAULT_HEALTHY_CLASSES if needed.")
        def mapper(cls_raw):
            return "healthy" if cls_raw in healthy else "unhealthy"
    elif args.collapse_to_plant:
        mapper = lambda _cls: "plant"
    else:
        mapper = None

    train_csv = OD_ROOT/"train_labels.csv"
    test_csv  = OD_ROOT/"test_labels.csv"
    train_imgs = OD_ROOT/"TRAIN"
    test_imgs  = OD_ROOT/"TEST"

    out_root = args.out_root

    classes = {}
    n_tr, classes = process_split(train_csv, train_imgs,
                                  out_root/"images"/"train", out_root/"labels"/"train",
                                  classes, mapper)
    n_va, classes = process_split(test_csv, test_imgs,
                                  out_root/"images"/"val", out_root/"labels"/"val",
                                  classes, mapper)

    names = [None]*len(classes)
    for name, idx in classes.items(): names[idx] = name
    (out_root/"dataset.yaml").write_text(
        f"path: {out_root.as_posix()}\ntrain: images/train\nval: images/val\nnames: {names}\n"
    )
    print("✅ Converted.")
    print("  Train imgs:", n_tr, " Val imgs:", n_va)
    print("  Classes:", classes)
    print("  Wrote:", out_root/"dataset.yaml")

if __name__ == "__main__":
    main()
