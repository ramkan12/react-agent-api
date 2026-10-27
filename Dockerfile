# Small official Python image (Debian without extras)
FROM python:3.13-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer
# and skip reinstalling when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py app.py ./

# Run as a non-root user so the app has limited permissions inside the container
RUN useradd --create-home appuser
USER appuser

# Hosts like Render tell the app which port to use via $PORT; default to 8000 locally.
# 0.0.0.0 makes the server reachable from outside the container.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
