import io
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image
from matplotlib import cm as mpl_cm

from lisa_segmentor import LISASegmentor
from csrnet_service import CSRNetService

app = FastAPI(title="Crowd Density API", description="Video frame → Heatmap + People Count")

# Initialize models once (reused for all requests)
seg = LISASegmentor()
seg.initialize_model(precision="fp16", load_in_4bit=True)
print("✅ LISASegmentor initialized")

csr = CSRNetService(device="cuda")  # Change to "cuda" if GPU available
print("✅ CSRNetService initialized")

print("Available routes:")
for route in app.routes:
    print(route.path, route.methods)

def generate_heatmap_image(heatmap: np.ndarray, cmap: str = "jet") -> Image.Image:
    """Convert density map to colored heatmap PIL image in memory."""
    arr = heatmap.astype(np.float32)
    if not np.isfinite(arr).any():
        arr = np.zeros_like(arr, dtype=np.float32)
    else:
        arr = arr - np.nanmin(arr)
        maxv = np.nanmax(arr)
        if maxv > 0:
            arr = arr / maxv
    colormap = mpl_cm.get_cmap(cmap)
    colored = (colormap(arr)[..., :3] * 255.0).astype(np.uint8)  # drop alpha
    return Image.fromarray(colored)


@app.post("/analyze_frame/")
async def analyze_frame(file: UploadFile = File(...)):
    """
    Upload a video frame (image).
    Returns JSON with:
    - count: estimated number of people
    - heatmap: heatmap image (PNG bytes)
    """
    # Load uploaded image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Run segmentation with LISA
    prompt = "Where is the audience in the image? Output the segmentation mask."
    mask = seg.segment(image, prompt)

    # Run CSRNet on masked image
    density_map, count = csr.infer(image, mask)

    if count < 50:
        return StreamingResponse(
            content=Image.open(io.BytesIO(contents)).convert("RGB"),
            media_type="image/jpeg",
            headers={"People-Count": 0}
        )
    
    # Generate heatmap image in memory
    heatmap_img = generate_heatmap_image(density_map)
    img_byte_arr = io.BytesIO()
    heatmap_img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Return StreamingResponse with heatmap + JSON
    return StreamingResponse(
        content=img_byte_arr,
        media_type="image/png",
        headers={"People-Count": str(round(float(count), 2))}
    )
