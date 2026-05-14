FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY Crowd_Monitoring/2026_T1/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY Crowd_Monitoring/2026_T1/ .

EXPOSE 8002

CMD ["uvicorn", "shared.services.main:app", "--host", "0.0.0.0", "--port", "8002"]