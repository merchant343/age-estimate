FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface \
    TRANSFORMERS_CACHE=/opt/huggingface/transformers

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY assignment2.py .
COPY static ./static

# 이미지 빌드 중 모델 다운로드 및 CPU 로딩을 검증한다.
RUN python -c "from transformers import pipeline; p=pipeline('image-classification', model='nateraw/vit-age-classifier', device=-1); print('MODEL_LOAD_OK', p.model.config._name_or_path)"

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "assignment2:app", "--host", "0.0.0.0", "--port", "8000"]
