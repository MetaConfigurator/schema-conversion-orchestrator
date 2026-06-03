FROM python:3.11-slim

# Install Node.js 18 and Java 21 JRE
RUN apt-get update && apt-get install -y \
    curl \
    openjdk-21-jre-headless \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app/src

# Install Python dependencies first (layer-cached separately from app code)
COPY requirements/runtime.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY src/ ./src/

# Copy external converters (JARs, compiled Node dist, robot.jar)
COPY external_converters/ ./external_converters/

# Install Node.js runtime dependencies
WORKDIR /app/external_converters/node
RUN if [ -f package.json ]; then npm install --omit=dev; fi

WORKDIR /app

EXPOSE 5002

# Allow up to 120 s for the first startup (LinkML + converter discovery take time)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Use gunicorn with a single sync worker; 120 s timeout covers slow conversions
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "1", "--timeout", "120", "schema_conversion_orchestrator.wsgi:application"]
