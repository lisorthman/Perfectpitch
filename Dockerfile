# Use Python 3.10 slim image for smaller footprint
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY setup.py .
COPY README.md .
COPY src/ ./src/

# Copy artifacts directory
COPY artifacts/ ./artifacts/

# Create a non-root user for security
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app

# Switch to non-root user
USER streamlit

# Expose Streamlit default port
EXPOSE 8501

# Configure Streamlit
RUN mkdir -p /home/streamlit/.streamlit && \
    echo "[server]" > /home/streamlit/.streamlit/config.toml && \
    echo "headless = true" >> /home/streamlit/.streamlit/config.toml && \
    echo "port = 8501" >> /home/streamlit/.streamlit/config.toml && \
    echo "enableCORS = false" >> /home/streamlit/.streamlit/config.toml && \
    echo "enableXsrfProtection = true" >> /home/streamlit/.streamlit/config.toml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
