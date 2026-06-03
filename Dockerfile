FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

# requirements.txt is currently UTF-16 LE, so normalize it before pip reads it.
RUN iconv -f UTF-16 -t UTF-8 requirements.txt > requirements.utf8.txt \
    && pip install --upgrade pip \
    && pip install -r requirements.utf8.txt \
    && pip install gunicorn whitenoise

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD sh -c 'python -c "import os, sys, urllib.request; port = os.getenv(\"PORT\", \"8000\"); urllib.request.urlopen(f\"http://127.0.0.1:{port}/health/\", timeout=3); sys.exit(0)"'

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && (python manage.py createcachetable django_cache || true) && python -m gunicorn pandajobs.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
