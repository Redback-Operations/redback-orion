FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY player_service/requirements.txt .
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir scipy

COPY player_service/ ./player_service/
COPY player_tracking_logic/Yolov11_ByteTrack_Player_Tracking/ ./player_tracking_logic/Yolov11_ByteTrack_Player_Tracking/
COPY player_tracking_logic/Re-Identification/ ./player_tracking_logic/Re-Identification/
COPY player_tracking_logic/tackle_detection_shafqat_ullah/ ./player_tracking_logic/tackle_detection_shafqat_ullah/
COPY player_tracking_logic/Tracking_Ethan/ ./player_tracking_logic/Tracking_Ethan/

WORKDIR /app/player_service

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
