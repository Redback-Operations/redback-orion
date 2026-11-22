FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY player_service/requirements.txt .
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Model weights come from the GitHub release, checked against their SHA-256.
COPY training/download_models.py ./training/download_models.py
RUN python training/download_models.py player_ref_best.pt

COPY analysis_pipeline/ ./analysis_pipeline/
COPY player_service/ ./player_service/

WORKDIR /app/player_service

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
