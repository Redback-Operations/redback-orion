📄 README.md (Player Tracking Service)
# 🎯 Player Tracking Service (YOLO + FastAPI)

This microservice runs player detection and tracking using **YOLOv8** with GPU acceleration (CUDA 12.1).  
It exposes a **FastAPI** server to handle video input and return tracking analytics.

---

## ⚙️ Requirements

- **Python 3.10** (recommended)
- **NVIDIA GPU** with CUDA 12.1 installed
- **Docker (optional)** if running PostgreSQL alongside

---

## 📦 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-repo>.git
cd afl-redback-orion/Player_Tracking/afl_player_tracking_and_crowd_monitoring/tracking_code

2. Create a virtual environment (Python 3.10)
py -3.10 -m venv venv
.\venv\Scripts\activate   # (Windows)
# or
source venv/bin/activate  # (Linux/Mac)

3. Upgrade pip
python -m pip install --upgrade pip

4. Install dependencies
pip install -r requirements.txt

5. Install PyTorch with CUDA 12.1 (GPU build)
pip uninstall torch torchvision torchaudio -y
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121


✅ Verify:

python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.version.cuda)"
# Expected: 2.5.1+cu121  True  12.1

🚀 Running the Service

Start the FastAPI server:

uvicorn main:app --reload --port 8001


The service will run at:

http://127.0.0.1:8001


Swagger docs available at:

http://127.0.0.1:8001/docs

🧪 Example Usage

Upload a video and trigger player tracking via backend.

Service will return:

Bounding box tracking per frame

Heatmaps

Analytics JSON output

🛠️ Notes

Requires CUDA 12.1 for GPU acceleration.

CPU-only mode is not recommended (too slow for real videos).

Works best when paired with the Backend API (/backend service).