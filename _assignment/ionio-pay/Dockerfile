FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

RUN useradd --create-home --uid 1000 pay
USER pay

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

# One worker: the state is in memory. Threads, so that tok_slow does not block other requests.
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--timeout", "60", "--bind", "0.0.0.0:8000", "app:app"]
