FROM python:3.11-slim

# Install Node.js and Java
RUN apt-get update && apt-get install -y \
    curl \
    openjdk-21-jdk-headless \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY *.py ./


# Copy external converters
COPY external_converters/ ./external_converters/

# Make converters executable
RUN chmod +x external_converters/java/converter.jar

# Install Node.js dependencies (if any runtime deps are needed)
WORKDIR /app/external_converters/node
RUN if [ -f package.json ]; then npm install --only=production; fi

WORKDIR /app

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Run the application
CMD ["python", "app.py"]