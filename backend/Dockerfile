FROM python:3.11-slim as builder

WORKDIR /build
RUN pip install uv

COPY backend/pyproject.toml .
RUN uv pip install --python 3.11 -e . --no-cache-dir


FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY backend/src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
