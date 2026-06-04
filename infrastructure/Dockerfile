FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir pip-tools

# Copy requirements
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY app ./app
COPY main.py .
COPY .env.example .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

ENV FLASK_APP=main.py
ENV ENVIRONMENT=production

CMD ["python", "main.py"]
