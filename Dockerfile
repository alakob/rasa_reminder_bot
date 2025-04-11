# Use an official Python runtime as a parent image
FROM python:3.8-slim as builder

WORKDIR /app

# Install system dependencies if needed
# RUN apt-get update && apt-get install -y --no-install-recommends <your-packages> && rm -rf /var/lib/apt/lists/*

# Copy just the requirements first to leverage Docker cache
COPY requirements.txt .

# Create and activate virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Build final image
FROM python:3.8-slim

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/venv ./venv

# Copy the rest of the application code
COPY . .

# Set environment variables (can be overridden)
# Default model, replace if needed or override via docker-compose/.env
ENV RASA_MODEL_NAME=20250411-160318-genteel-soul.tar.gz 
# Example DATABASE_URL for docker-compose internal network, override via docker-compose/.env
ENV DATABASE_URL=postgresql://user:password@db:5432/database 
ENV TWILIO_ACCOUNT_SID=""
ENV TWILIO_AUTH_TOKEN=""
ENV TWILIO_PHONE_NUMBER=""
ENV SLACK_BOT_TOKEN=""
# Add other necessary environment variables here

# Activate virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Expose ports (Rasa: 5005, Action Server: 5055)
EXPOSE 5005
EXPOSE 5055

# Default command to run Rasa server (can be overridden in docker-compose)
# CMD rasa run --enable-api --cors "*" --debug -m models/${RASA_MODEL_NAME} 