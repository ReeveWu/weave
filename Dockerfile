FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    libffi-dev \
    libgdk-pixbuf-2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    poppler-utils \
    shared-mime-info \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md requirements.txt ./
COPY server/requirements.txt ./server/requirements.txt
COPY weave ./weave
COPY server ./server

RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir -r server/requirements.txt

EXPOSE 10000

CMD ["sh", "-c", "uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
