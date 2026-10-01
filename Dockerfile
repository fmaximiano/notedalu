FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/start.sh && mkdir -p /app/.data

ENV PYTHONUNBUFFERED=1 \
    NOTEDALU_DATA_DIR=/app/.data

ENTRYPOINT ["/app/start.sh"]
