FROM python:3.9-slim

WORKDIR /app

# Create a directory for logs with proper permissions
RUN mkdir -p /app/logs && chmod 777 /app/logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY flight_agent.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "flight_agent.py"] 