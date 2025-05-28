# ────────────────────────────────────────────────────────────────────────────────
# Base Python image
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.9-slim

# ────────────────────────────────────────────────────────────────────────────────
# OS-level dependencies: Tesseract OCR + cleanup
# ────────────────────────────────────────────────────────────────────────────────
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      tesseract-ocr \
      libtesseract-dev \
      libleptonica-dev \
      pkg-config \
      gcc \
 && rm -rf /var/lib/apt/lists/*

# ────────────────────────────────────────────────────────────────────────────────
# Workdir & Python deps
# ────────────────────────────────────────────────────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ────────────────────────────────────────────────────────────────────────────────
# Copy app code and set start command
# ────────────────────────────────────────────────────────────────────────────────
COPY . .
ARG UVICORN_HOST=0.0.0.0
ARG UVICORN_PORT=8000
CMD ["uvicorn","src.api.main:app","--host","${UVICORN_HOST}","--port","${UVICORN_PORT}"]