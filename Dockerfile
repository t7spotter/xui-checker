FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so they cache across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static

# Run as a non-root user.
RUN useradd --create-home appuser
USER appuser

EXPOSE 8001

# The run command lives in docker-compose.yml.
