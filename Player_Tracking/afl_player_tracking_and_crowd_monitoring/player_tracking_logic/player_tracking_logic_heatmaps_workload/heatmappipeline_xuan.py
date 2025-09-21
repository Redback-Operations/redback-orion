""" 
---------------------------------------------------
REQUIREMENTS
---------------------------------------------------
pip install numpy pandas matplotlib scipy


---------------------------------------------------
headers required
---------------------------------------------------
frame_id, player_id, timestamp_s, x1, y1, x2, y2, cx, cy, w, h, confidence


---------------------------------------------------
BASIC USAGE
---------------------------------------------------
# CMD or terminal 
py .\\heatmappipeline.py --inputs "Data.csv:Data" --out-dir outputs


"""
import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.ndimage import gaussian_filter

# -------------------------
# Defaults and schema
# -------------------------

# These column names MUST exist in each CSV.
# If your source uses different names, rename the columns in a pre-step or here.
REQUIRED_COLS = [
    "frame_id","player_id","timestamp_s","x1","y1","x2","y2","cx","cy","w","h","confidence" # ADJUSTED FOR XUAN CSV --- LUCAS
]

# AFL ground (typical) dimensions in metres.
# Length = tip-to-tip, Width = wing-to-wing. Adjust via CLI if needed.
DEFAULT_FIELD_LENGTH_M = 165.0
DEFAULT_FIELD_WIDTH_M  = 135.0

# Grid resolution and smoothing.
# nx/ny = number of bins; sigma = Gaussian blur in “bins”.
DEFAULT_NX = 200
DEFAULT_NY = 150
DEFAULT_SIGMA = 2.0

# -------------------------
# Schema + loading
# -------------------------

def assert_schema(df: pd.DataFrame, path: str):

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"{path} is missing required columns: {missing}\n"
            f"Found columns: {list(df.columns)}\n"
            f"Tip: ensure your header row is exactly: {REQUIRED_COLS}"
        )

def load_events_csv(path: str) -> pd.DataFrame:

    df = pd.read_csv(path)
    assert_schema(df, path)

    # Ensure numeric, drop bad rows (NaN/inf in x/y).
    for c in ["frame_id","player_id","timestamp_s","x1","y1","x2","y2","cx","cy","w","h","confidence"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["cx", "cy"])
    df = df[np.isfinite(df["cx"]) & np.isfinite(df["cy"])]
    return df.reset_index(drop=True)

def choose_weights(df: pd.DataFrame, mode: str | None): # HAVE ADJUSTED TO TAKE DATASET WHERE VISIBILITY COLUMN DOES NOT EXIST --- LUCAS

    if not mode:
        return None
    m = mode.lower().strip()

    # Use 'confidence' for weights with Xuans csv --- LUCAS
    conf_col = "confidence" if "confidence" in df.columns else ("conf" if "conf" in df.columns else None)

    if m in ("conf", "confidence"):
        if conf_col is None:  # no confidence column at all
            return None
        return pd.to_numeric(df[conf_col], errors="coerce").fillna(0).to_numpy(dtype=float)

    if m == "visibility":
        if "visibility" not in df.columns:
            # no visibility in Xuan's CSV unweighted
            return None
        return pd.to_numeric(df["visibility"], errors="coerce").fillna(0).to_numpy(dtype=float)

    if m in ("conf*visibility", "visibility*conf"):
        # conf * visibility; if visibility missing, treat as 1s (i.e. just conf)
        conf = (pd.to_numeric(df[conf_col], errors="coerce").fillna(0).to_numpy(dtype=float)
                if conf_col else np.zeros(len(df), dtype=float))
        vis = (pd.to_numeric(df["visibility"], errors="coerce").fillna(1).to_numpy(dtype=float)
               if "visibility" in df.columns else np.ones(len(df), dtype=float))
        return conf * vis
    # If someone passes an unexpected string, fail gracefully to unweighted.
    return None

# -------------------------
# Field + mapping helpers
# -------------------------

def raw_bbox(xs, ys, pad_ratio=0.02):

    xmin, xmax = float(np.min(xs)), float(np.max(xs))
    ymin, ymax = float(np.min(ys)), float(np.max(ys))
    dx, dy = max(xmax - xmin, 1e-9), max(ymax - ymin, 1e-9)
    return (xmin - dx*pad_ratio, xmax + dx*pad_ratio,
            ymin - dy*pad_ratio, ymax + dy*pad_ratio)

def raw_to_metres(x, y, bbox_raw, a, b):

    xmin, xmax, ymin, ymax = bbox_raw
    x_m = ((x - xmin) / max(1e-9, (xmax - xmin))) * (2*a) - a
    y_m = ((y - ymin) / max(1e-9, (ymax - ymin))) * (2*b) - b
    return x_m, y_m

def make_oval_mask_metres(nx, ny, a, b):

    x_edges = np.linspace(-a, a, nx + 1)
    y_edges = np.linspace(-b, b, ny + 1)
    xc = (x_edges[:-1] + x_edges[1:]) / 2
    yc = (y_edges[:-1] + y_edges[1:]) / 2
    Xc, Yc = np.meshgrid(xc, yc)
    mask = (Xc**2) / (a**2) + (Yc**2) / (b**2) <= 1.0
    return x_edges, y_edges, mask

def heatmap_in_metres(x_raw, y_raw, bbox_raw, a, b, nx, ny, sigma, weights=None):

    x_m, y_m = raw_to_metres(np.asarray(x_raw, float), np.asarray(y_raw, float), bbox_raw, a, b)
    x_edges, y_edges, mask = make_oval_mask_metres(nx, ny, a, b)

    # Note: np.histogram2d expects bins=[x_edges, y_edges] but returns H with shape (nx, ny),
    # so we transpose to align with imshow(origin="lower") which expects [y, x].
    H, _, _ = np.histogram2d(x_m, y_m, bins=[x_edges, y_edges], weights=weights)
    H = H.T
    Hs = gaussian_filter(H, sigma=sigma)  # smooth in bin-space
    Hs_masked = np.where(mask, Hs, np.nan)
    return Hs_masked, x_edges, y_edges

# -------------------------
# AFL field drawing
# -------------------------

def draw_afl_field_metres(ax, a, b,
                          centre_square=50.0,
                          centre_inner_d=3.0,
                          centre_outer_d=10.0,
                          goal_square_depth=9.0,
                          goal_square_width=6.4,
                          arc_r=50.0,
                          line_color="white", lw=2.0, alpha=0.95,
                          show_ticks=False):
    """Draw an AFL ground overlay (lines only) in metres on the given axes."""
    t = np.linspace(0, 2*np.pi, 800)

    # Oval boundary
    ax.plot(a*np.cos(t), b*np.sin(t), color=line_color, lw=lw, alpha=alpha)

    # Centre line
    ax.plot([0, 0], [-b, b], color=line_color, lw=lw, alpha=alpha*0.9)

    # Centre square (50 x 50)
    cs = centre_square/2.0
    ax.plot([-cs,  cs,  cs, -cs, -cs], [-cs, -cs, cs, cs, -cs],
            color=line_color, lw=lw-0.5, alpha=alpha*0.9)

    # Centre circles (outer 10 m, inner 3 m)
    th = np.linspace(0, 2*np.pi, 400)
    ax.plot((centre_outer_d/2.0)*np.cos(th), (centre_outer_d/2.0)*np.sin(th),
            color=line_color, lw=lw-0.5, alpha=alpha*0.9)
    ax.plot((centre_inner_d/2.0)*np.cos(th), (centre_inner_d/2.0)*np.sin(th),
            color=line_color, lw=lw-0.5, alpha=alpha*0.6)

    # 50 m arcs (left/right)
    phi_L = np.linspace(-np.pi/2, np.pi/2, 400)
    phi_R = np.linspace(np.pi/2, 3*np.pi/2, 400)
    ax.plot(-a + arc_r*np.cos(phi_L), 0 + arc_r*np.sin(phi_L),
            color=line_color, lw=lw-0.5, alpha=alpha*0.6)
    ax.plot( a + arc_r*np.cos(phi_R), 0 + arc_r*np.sin(phi_R),
            color=line_color, lw=lw-0.5, alpha=alpha*0.6)

    # Goal squares: 9 m deep x 6.4 m wide
    gs_w = goal_square_width/2.0
    ax.plot([-a, -a+goal_square_depth, -a+goal_square_depth, -a, -a],
            [-gs_w, -gs_w, gs_w, gs_w, -gs_w],
            color=line_color, lw=lw-0.5, alpha=alpha*0.9)
    ax.plot([ a,  a-goal_square_depth,  a-goal_square_depth,  a,  a],
            [-gs_w, -gs_w, gs_w, gs_w, -gs_w],
            color=line_color, lw=lw-0.5, alpha=alpha*0.9)

    # Goal line ticks (simple markers near tips)
    tick = 4.0
    for xg in (-a, a):
        ax.plot([xg, xg], [-tick, tick], color=line_color, lw=lw, alpha=alpha)

    # Axes cosmetic setup
    if show_ticks:
        ax.set_xlabel("Metres (X)")
        ax.set_ylabel("Metres (Y)")
        ax.set_xticks(np.arange(-a, a+1e-6, 20))
        ax.set_yticks(np.arange(-b, b+1e-6, 20))
        ax.grid(alpha=0.15, linewidth=0.8)
    else:
        ax.set_axis_off()

    ax.set_aspect('equal')

def plot_heatmap_on_field_metres(
    H, x_edges, y_edges, a, b, title="", alpha_img=0.88, out_path=None
):
    """Render a heatmap on a green oval with AFL field lines and save PNG.

    - Uses a robust upper bound (99th percentile) for colour scaling.
    - Adds a small “20 m” scale bar.
    """
    fig, ax = plt.subplots(figsize=(11, 8))

    # Green oval background (grass vibe) beneath the heatmap
    t = np.linspace(0, 2*np.pi, 600)
    ax.fill(a*np.cos(t), b*np.sin(t), color=(0.05, 0.35, 0.05), alpha=0.95, zorder=0)

    extent = [x_edges.min(), x_edges.max(), y_edges.min(), y_edges.max()]
    finite_vals = H[np.isfinite(H)]
    vmax = (np.nanpercentile(finite_vals, 99) if finite_vals.size else np.nanmax(H)) or 1.0

    # Heatmap layer
    im = ax.imshow(
        H, origin="lower", extent=extent, aspect="equal",
        interpolation="bilinear", alpha=alpha_img,
        norm=Normalize(vmin=0.0, vmax=vmax), zorder=2
    )

    # Field lines drawn over the grass, under the heatmap for soft blending
    draw_afl_field_metres(ax, a, b, show_ticks=False)

    # 20 m scale bar (bottom-left)
    sb_y = -b + 8
    sb_x0, sb_x1 = -a + 12, -a + 32
    ax.plot([sb_x0, sb_x1], [sb_y, sb_y], color="white", lw=4, alpha=0.95)
    ax.text((sb_x0+sb_x1)/2, sb_y-4, "20 m", ha="center", va="top",
            color="white", fontsize=11)

    ax.set_title(title, color="white")

    # Colorbar on the right
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Intensity")

    # Clean frame
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fig.savefig(out_path, dpi=220)
    plt.close(fig)

def save_density_csv(H, x_edges, y_edges, out_csv_path):
    """Export the smoothed density as a tidy CSV: (x_m, y_m, density)."""
    os.makedirs(os.path.dirname(out_csv_path), exist_ok=True)
    xc = (x_edges[:-1] + x_edges[1:]) / 2
    yc = (y_edges[:-1] + y_edges[1:]) / 2
    Xc, Yc = np.meshgrid(xc, yc)
    df = pd.DataFrame({
        "x_m": Xc.flatten(),
        "y_m": Yc.flatten(),
        "density": np.nan_to_num(H, nan=0.0).flatten()
    })
    df.to_csv(out_csv_path, index=False)

# -------------------------
# Main
# -------------------------

def parse_inputs(pairs):
    """Parse ["path:label", ...] into a list of (path, label).

    If ":label" is omitted, the filename stem is used as the label.
    """
    out = []
    for p in pairs:
        if ":" in p:
            path, label = p.split(":", 1)
        else:
            path, label = p, os.path.splitext(os.path.basename(p))[0]
        out.append((path, label))
    return out

def main():
    """Command-line entry point.

    Key choices your teammates might tweak:
    - --weight-mode: how to weight each plotted point (conf, visibility, both, or none)
    - --nx/--ny: spatial resolution (bigger = finer grid, slower)
    - --sigma: smoothing; try 1.0–4.0 depending on point sparsity
    - --group-by class_id: produce one heatmap per class within each CSV
    """
    ap = argparse.ArgumentParser(description="AFL oval heatmap generator")
    ap.add_argument(
        "--inputs", nargs="+", required=True,
        help='List like "file.csv:label". Label optional; defaults to file stem.'
    )
    ap.add_argument("--out-dir", default="heatmap_outputs", help="Output directory")
    ap.add_argument("--weight-mode", default="conf*visibility",
                    choices=["none", "conf", "visibility", "conf*visibility"],
                    help="Weighting for histogram bins")
    ap.add_argument("--field-length", type=float, default=DEFAULT_FIELD_LENGTH_M,
                    help="Oval length in metres (tip-to-tip)")
    ap.add_argument("--field-width", type=float, default=DEFAULT_FIELD_WIDTH_M,
                    help="Oval width in metres (wing-to-wing)")
    ap.add_argument("--nx", type=int, default=DEFAULT_NX, help="Grid bins in X")
    ap.add_argument("--ny", type=int, default=DEFAULT_NY, help="Grid bins in Y")
    ap.add_argument("--sigma", type=float, default=DEFAULT_SIGMA,
                    help="Gaussian smoothing sigma (bins)")
    """ap.add_argument("--group-by", default=None,
                    choices=[None, "class_id"],
                    help="Optional grouping to produce one heatmap per group")""" # COMMENTED OUT --- LUCAS
    ap.add_argument("--group-by", default=None,
                    choices=[None, "class_id", "player_id"],
                    help="Optional grouping to produce one heatmap per group") # ALLOWS GROUPING BY player_id IN THE CLI --- LUCAS
    args = ap.parse_args()
    print("DEBUG group-by:", args.group_by) # DEBUG --- LUCAS

    inputs = parse_inputs(args.inputs)
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    # Half-dimensions in metres
    a = args.field_length / 2.0
    b = args.field_width  / 2.0

    # Load all inputs first so we can compute a single shared raw bbox across them.
    # This ensures all figures align spatially and are directly comparable.
    loaded = []
    all_x, all_y = [], []

    for path, label in inputs:
        df = load_events_csv(path)
        loaded.append((df, label, path))
        all_x.append(df["cx"].to_numpy())
        all_y.append(df["cy"].to_numpy())

    # If no data at all (edge-case), invent a tiny bbox to avoid division-by-zero.
    all_x = np.concatenate(all_x) if len(all_x) else np.array([0.0])
    all_y = np.concatenate(all_y) if len(all_y) else np.array([0.0])
    shared_bbox_raw = raw_bbox(all_x, all_y)

    # Generate heatmaps per file (and optionally per class)
    for df, label, path in loaded:
        # Pick base weights once per file; subsetting below recomputes if needed.
        weights_base = None if args.weight_mode == "none" else choose_weights(df, args.weight_mode)

        if args.group_by == "class_id":
            # One output per class_id present in the file.
            classes = sorted(df["class_id"].dropna().unique().tolist())
            for cid in classes:
                sub = df[df["class_id"] == cid].reset_index(drop=True)
                if sub.empty:
                    continue
                # Recompute weights on the subset to keep alignment correct.
                w = None if weights_base is None else choose_weights(sub, args.weight_mode)
                H, xe, ye = heatmap_in_metres(
                    sub["cx"], sub["cy"], shared_bbox_raw, a, b,
                    args.nx, args.ny, args.sigma, w
                )
                title = f"{label} — class_id {cid} ({int(args.field_length)}×{int(args.field_width)} m)"
                img_out = os.path.join(out_dir, f"heatmap_{label}_class{int(cid)}.png")
                csv_out = os.path.join(out_dir, f"density_{label}_class{int(cid)}.csv")
                plot_heatmap_on_field_metres(H, xe, ye, a, b, title, out_path=img_out)
                save_density_csv(H, xe, ye, csv_out)
        
        elif args.group_by == "player_id": # ADDING PLAYER BRANCH --- LUCAS
            players = sorted(
                pd.to_numeric(df["player_id"], errors="coerce")
                .dropna().unique().astype(int).tolist())
            
            for pid in players:
                sub = df[df["player_id"] == pid].reset_index(drop=True)
                if sub.empty:
                    continue

                w = None if weights_base is None else choose_weights(sub, args.weight_mode)
                H, xe, ye = heatmap_in_metres(
                    sub["cx"], sub["cy"], shared_bbox_raw, a, b,
                    args.nx, args.ny, args.sigma, w
                )

                title = f"{label} - player_id {pid} ({int(args.field_length)}x{int(args.field_width)} m)"
                img_out = os.path.join(out_dir, f"heatmap_{pid}.png")
                csv_out = os.path.join(out_dir, f"density_player_{pid}.csv")
                plot_heatmap_on_field_metres(H, xe, ye, a, b, title, out_path=img_out)
                save_density_csv(H, xe, ye, csv_out)

        else:
            # Single heatmap for the entire file.
            H, xe, ye = heatmap_in_metres(
                df["cx"], df["cy"], shared_bbox_raw, a, b,
                args.nx, args.ny, args.sigma, weights_base
            )
            title = f"{label} — Density ({int(args.field_length)}×{int(args.field_width)} m)"
            img_out = os.path.join(out_dir, f"heatmap_{label}.png")
            csv_out = os.path.join(out_dir, f"density_{label}.csv")
            plot_heatmap_on_field_metres(H, xe, ye, a, b, title, out_path=img_out)
            save_density_csv(H, xe, ye, csv_out)

    print(f"Done. Outputs in: {os.path.abspath(out_dir)}")

if __name__ == "__main__":
    main()
