FROM python:3.12-slim

WORKDIR /app

# Build deps for psycopg2 (no wheels) and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first — installing deps before source maximises layer cache
COPY pyproject.toml uv.lock ./

# Install runtime dependencies into a venv (no dev extras, no project package)
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --no-dev --no-install-project

# Copy application code
COPY app ./app
COPY main.py .
COPY .env.example .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /opt/venv
USER appuser

EXPOSE 5000

ENV FLASK_APP=main.py
ENV APP_ENV=production

CMD ["python", "main.py"]
