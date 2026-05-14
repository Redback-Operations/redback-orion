FROM python:3.13.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    ultralytics \
    opencv-python-headless \
    pandas \
    numpy \
    matplotlib \
    scikit-learn

COPY . .

CMD ["tail", "-f", "/dev/null"]