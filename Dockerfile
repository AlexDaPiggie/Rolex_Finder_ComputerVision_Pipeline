FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection; AutoProcessor.from_pretrained('IDEA-Research/grounding-dino-base'); AutoModelForZeroShotObjectDetection.from_pretrained('IDEA-Research/grounding-dino-base')"

COPY src ./src
COPY models ./models
COPY data/processed/class_mapping.json ./data/processed/class_mapping.json

CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-10000}"]