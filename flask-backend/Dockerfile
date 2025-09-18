# Use a slim Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose port (Flask runs on 5002)
EXPOSE 5002

# Run Flask using gunicorn (production-ready WSGI server)
# Adjust "app:app" if your Flask instance is called differently
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
