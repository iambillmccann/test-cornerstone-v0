FROM python:3.12-slim AS builder

WORKDIR /tmp/build

COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY apps/api/README.md apps/api/README.md

RUN pip install --user --no-cache-dir -e apps/api

FROM python:3.12-slim

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder /root/.local /root/.local

# Add local pip bin directory to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY apps/api/app app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')" || exit 1

# Run uvicorn server
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
