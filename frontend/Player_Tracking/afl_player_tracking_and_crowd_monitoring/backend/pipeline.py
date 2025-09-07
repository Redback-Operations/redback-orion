import os, shutil, glob, subprocess, argparse
from pathlib import Path
from dataclasses import dataclass
import yaml

# ----------------- utils -----------------
def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def yolo_txt_lines(path: Path):
    if not path.exists(): return []
    with path.open() as f:
        return [ln.strip() for ln in f if ln.strip()]

def write_lines(path: Path, lines):
    ensure_dir(path.parent)
    with path.open("w") as f:
        f.write("\n".join(lines))

def parse_yolo_line(ln):
    parts = ln.split()
    cls = int(float(parts[0]))
    xc, yc, w, h = map(float, parts[1:5])
    return cls, (xc, yc, w, h), parts

def iou_xywh(a, b):
    ax1, ay1 = a[0]-a[2]/2, a[1]-a[3]/2
    ax2, ay2 = a[0]+a[2]/2, a[1]+a[3]/2
    bx1, by1 = b[0]-b[2]/2, b[1]-b[3]/2
    bx2, by2 = b[0]+b[2]/2, b[1]+b[3]/2
    ix1, iy1 = max(ax1,bx1), max(ay1,by1)
    ix2, iy2 = min(ax2,bx2), min(ay2,by2)
    iw, ih = max(0, ix2-ix1), max(0, iy2-iy1)
    inter = iw * ih
    area_a = (ax2-ax1) * (ay2-ay1)
    area_b = (bx2-bx1) * (by2-by1)
    union = area_a + area_b - inter + 1e-9
    return inter / union

def center_inside(inner, outer):
    """Return True if inner box center lies inside outer box."""
    cx, cy = inner[0], inner[1]
    x1 = outer[0] - outer[2]/2
    y1 = outer[1] - outer[3]/2
    x2 = outer[0] + outer[2]/2
    y2 = outer[1] + outer[3]/2
    return (x1 <= cx <= x2) and (y1 <= cy <= y2)

# ----------------- config -----------------
@dataclass
class Cfg:
    root: Path
    manual_clips: list
    images: Path
    labels_manual: Path
    labels_auto: Path
    labels_remap: Path
    labels_dense: Path
    viz: Path
    data_yaml: Path
    imgsz: int
    conf: float
    coco_classes: list
    iou_thr: float
    draw_preview: bool
    names: dict

def load_cfg(p: Path) -> Cfg:
    d = yaml.safe_load(p.read_text())
    root = Path(d["root"])
    ds   = d["dataset"]
    yolo = d["yolo"]
    merg = d["merge"]
    names = ds.get("names", {0: "player", 1: "ball"})
    # keys may come in as strings from YAML; normalize to int
    names = {int(k): str(v) for k, v in names.items()}
    return Cfg(
        root=root,
        manual_clips=[root/Path(x) for x in d["manual_clips"]],
        images=root/Path(ds["images"]),
        labels_manual=root/Path(ds["labels_manual"]),
        labels_auto=root/Path(ds["labels_auto"]),
        labels_remap=root/Path(ds["labels_remap"]),
        labels_dense=root/Path(ds["labels_dense"]),
        viz=root/Path(ds["viz"]),
        data_yaml=root/Path(ds["data_yaml"]),
        imgsz=int(yolo["imgsz"]),
        conf=float(yolo["conf"]),
        coco_classes=list(yolo["classes"]),
        iou_thr=float(merg["iou_thr"]),
        draw_preview=bool(merg.get("draw_preview", True)),
        names=names
    )

# ----------------- steps -----------------
def step_collect_manual(cfg: Cfg):
    print("==> Collect manual frames & labels")
    for p in [cfg.images, cfg.labels_manual]:
        if p.exists():
            shutil.rmtree(p)
        ensure_dir(p)
    for clip in cfg.manual_clips:
        prefix = clip.name
        for ip in sorted(glob.glob(str(clip/"images" / "*"))):
            ip = Path(ip)
            stem = f"{prefix}__{ip.stem}"
            out_img = cfg.images / f"{stem}{ip.suffix.lower()}"
            shutil.copy2(ip, out_img)
            lp = clip/"labels"/f"{ip.stem}.txt"
            if lp.exists():
                shutil.copy2(lp, cfg.labels_manual/f"{stem}.txt")
    print("Manual collection done.")

def step_auto_detect(cfg: Cfg):
    print("==> YOLO predict (person & sports ball)")
    if cfg.labels_auto.exists():
        shutil.rmtree(cfg.labels_auto)
    ensure_dir(cfg.labels_auto)

    runs = cfg.root/"runs_auto"
    if runs.exists():
        shutil.rmtree(runs)

    cmd = [
        "yolo", "mode=predict", "model=yolo11x.pt",
        f"source={str(cfg.images)}",
        f"imgsz={cfg.imgsz}", f"conf={cfg.conf}",
        "save=True", "save_txt=True",
        f"classes={','.join(str(c) for c in cfg.coco_classes)}",
        f"project={str(runs)}", "name=auto"
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    labels_dirs = list(runs.glob("auto/labels"))
    if not labels_dirs:
        raise RuntimeError("Could not find YOLO predictions 'labels' folder.")
    src = labels_dirs[0]
    for f in src.glob("*.txt"):
        shutil.copy2(f, cfg.labels_auto/f.name)
    print("Auto-detect labels collected.")

def step_remap(cfg: Cfg):
    print("==> Remap COCO -> our schema")
    ensure_dir(cfg.labels_remap)
    id_map = {0: 0, 32: 1}  # COCO person->player, sports ball->ball
    kept, dropped = 0, 0
    for p in sorted(cfg.labels_auto.glob("*.txt")):
        out_lines = []
        for ln in yolo_txt_lines(p):
            cls, box, parts = parse_yolo_line(ln)
            if cls in id_map:
                parts[0] = str(id_map[cls])
                out_lines.append(" ".join(parts))
                kept += 1
            else:
                dropped += 1
        write_lines(cfg.labels_remap/p.name, out_lines)
    print(f"Remapped: kept {kept}, dropped {dropped} other classes.")

def step_merge(cfg: Cfg):
    print("==> Merge manual + auto (manual always wins)")
    ensure_dir(cfg.labels_dense)
    kept_auto, dropped_auto = 0, 0
    frames = 0

    for ip in sorted(cfg.images.glob("*")):
        stem = ip.stem
        man_path = cfg.labels_manual/f"{stem}.txt"
        auto_path = cfg.labels_remap/f"{stem}.txt"
        out_path = cfg.labels_dense/f"{stem}.txt"

        man_lines = yolo_txt_lines(man_path)
        auto_lines = yolo_txt_lines(auto_path)

        # parse manual
        man_boxes = []
        for ln in man_lines:
            cls, box, parts = parse_yolo_line(ln)
            man_boxes.append((cls, box))

        out_lines = list(man_lines)  # start with all manual boxes

        # rule: drop auto if SAME CLASS and (IoU>=thr OR center_inside)
        for ln in auto_lines:
            cls_a, box_a, parts_a = parse_yolo_line(ln)
            covered = False
            for cls_m, box_m in man_boxes:
                if cls_a == cls_m and (iou_xywh(box_a, box_m) >= cfg.iou_thr or center_inside(box_a, box_m)):
                    covered = True
                    break
            if covered:
                dropped_auto += 1
            else:
                out_lines.append(" ".join(parts_a))
                kept_auto += 1

        write_lines(out_path, out_lines)
        frames += 1

    print(f"Merged {frames} frames. Kept auto: {kept_auto}, dropped auto: {dropped_auto}.")

def step_viz(cfg: Cfg):
    if not cfg.draw_preview:
        print("==> Skipping viz (disabled).")
        return
    print("==> Viz overlays (green=manual, blue=auto)")
    ensure_dir(cfg.viz)
    try:
        import cv2
    except ImportError:
        print("OpenCV not installed, skipping viz. (pip install opencv-python)")
        return

    def to_px(box, w, h):
        xc,yc,bw,bh = box
        x1 = int((xc-bw/2)*w); y1 = int((yc-bh/2)*h)
        x2 = int((xc+bw/2)*w); y2 = int((yc+bh/2)*h)
        return x1,y1,x2,y2

    for ip in sorted(cfg.images.glob("*")):
        stem = ip.stem
        img = cv2.imread(str(ip))
        if img is None: 
            continue
        h, w = img.shape[:2]

        # Load manual, auto, and final dense annotations
        manual_lines = yolo_txt_lines(cfg.labels_manual/f"{stem}.txt")
        auto_lines = yolo_txt_lines(cfg.labels_remap/f"{stem}.txt")
        dense_lines = yolo_txt_lines(cfg.labels_dense/f"{stem}.txt")

        # Parse manual boxes
        manual_boxes = []
        for ln in manual_lines:
            cls, box, _ = parse_yolo_line(ln)
            manual_boxes.append((cls, box))

        # Parse all dense boxes (final result)
        dense_boxes = []
        for ln in dense_lines:
            cls, box, _ = parse_yolo_line(ln)
            dense_boxes.append((cls, box))

        # Determine which boxes in dense are from manual vs auto
        manual_box_set = set()
        auto_only_boxes = []

        # First, mark all manual boxes and draw them
        for cls, box in manual_boxes:
            manual_box_set.add((cls, tuple(box)))
            x1, y1, x2, y2 = to_px(box, w, h)
            
            # Draw green rectangle for manual
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add object name and source label
            obj_name = cfg.names.get(cls, f"class_{cls}")
            label = f"{obj_name} (manual)"
            
            # Calculate text size for better positioning
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Draw text background for better readability
            cv2.rectangle(img, (x1, y1-text_height-10), (x1+text_width, y1), (0, 255, 0), -1)
            cv2.putText(img, label, (x1, y1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)

        # Now find auto-only boxes (those in dense that aren't manual)
        for cls, box in dense_boxes:
            box_tuple = tuple(box)
            if (cls, box_tuple) not in manual_box_set:
                # This is an auto-only detection
                # Double-check it's not covered by any manual box using the same logic as merge
                covered = False
                for cls_m, box_m in manual_boxes:
                    if cls == cls_m and (iou_xywh(box, box_m) >= cfg.iou_thr or center_inside(box, box_m)):
                        covered = True
                        break
                
                if not covered:
                    auto_only_boxes.append((cls, box))

        # Draw auto-only boxes in blue
        for cls, box in auto_only_boxes:
            x1, y1, x2, y2 = to_px(box, w, h)
            
            # Draw blue rectangle for auto
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # Add object name and source label
            obj_name = cfg.names.get(cls, f"class_{cls}")
            label = f"{obj_name} (auto)"
            
            # Calculate text size for better positioning
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Draw text background for better readability
            cv2.rectangle(img, (x1, y1-text_height-10), (x1+text_width, y1), (255, 0, 0), -1)
            cv2.putText(img, label, (x1, y1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imwrite(str(cfg.viz/f"{stem}.jpg"), img)
    print("Viz complete.")

def step_make_data_yaml(cfg: Cfg):
    print("==> Write data.yaml")
    content = {
        "path": str(cfg.root/"dataset").replace("\\","/"),
        "train": "images",
        "val":   "images",
        "names": {int(k): str(v) for k, v in cfg.names.items()}
    }
    ensure_dir(cfg.data_yaml.parent)
    with cfg.data_yaml.open("w") as f:
        yaml.safe_dump(content, f)
    print("data.yaml written.")

# ----------------- main -----------------
STAGES = ["collect", "auto", "remap", "merge", "viz", "datayaml", "all"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--stage", default="all", choices=STAGES)
    args = ap.parse_args()

    cfg = load_cfg(Path(args.config))

    if args.stage in ("collect","all"):  step_collect_manual(cfg)
    if args.stage in ("auto","all"):     step_auto_detect(cfg)
    if args.stage in ("remap","all"):    step_remap(cfg)
    if args.stage in ("merge","all"):    step_merge(cfg)
    if args.stage in ("viz","all"):      step_viz(cfg)
    if args.stage in ("datayaml","all"): step_make_data_yaml(cfg)

if __name__ == "__main__":
    main()