FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.3

WORKDIR /app

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry lock --no-update \
    && poetry install --only main --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ["python", "-c", "import sys,urllib.request; \
try: \
  r=urllib.request.urlopen('http://127.0.0.1:8000/docs', timeout=3); \
  sys.exit(0 if r.status==200 else 1); \
except Exception: \
  sys.exit(1)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
