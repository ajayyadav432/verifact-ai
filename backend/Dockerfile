FROM python:3.11-slim

WORKDIR /app

# Install dependencies (build context is repo root)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Railway injects PORT dynamically — do NOT hardcode it
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

