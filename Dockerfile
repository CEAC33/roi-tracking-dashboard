FROM python:3.11-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ /app/backend/

# Copy the scripts directory
COPY scripts/ /app/scripts/

# Copy and make the startup script executable
COPY backend/start.sh /app/
RUN chmod +x /app/start.sh

EXPOSE 8000

# Set the working directory to where the API is located
WORKDIR /app/backend

CMD ["/app/start.sh"] 