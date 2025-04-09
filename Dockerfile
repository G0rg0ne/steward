FROM python:3.9-slim

WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data && \
    chmod 777 /app/logs /app/data

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a startup script
RUN echo '#!/bin/bash\n\
python flight_agent.py & \
streamlit run app.py --server.port=8501 --server.address=0.0.0.0' > /app/start.sh && \
chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 