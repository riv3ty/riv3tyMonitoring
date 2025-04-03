# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create dynamic telegram_config.py from environment variables
RUN echo 'import os\n\
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")\n\
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")' > telegram_config.py

# Create volume for persistent data
VOLUME ["/app/instance"]

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/ || exit 1

# Run the server
CMD ["python", "server.py"]
