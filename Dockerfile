# HintAI Backend Docker Container
# Usage: docker build -t hintai . && docker run -p 8000:8000 hintai

FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ backend/
COPY data/ data/

# Expose WebSocket/HTTP port
EXPOSE 8000

# Run server
CMD ["python", "backend/api/main.py"]
