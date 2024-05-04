FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/Cerberus-ik/preview_generator
WORKDIR /app

# Update system and install necessary libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libpq-dev \
    gcc

COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

# Command to run the application
CMD ["python", "main.py"]
