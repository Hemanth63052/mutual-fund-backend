FROM python:3.12.3-slim

ENV APP_HOME=/app
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git wget curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR $APP_HOME

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Define default command
CMD ["python", "app.py"]
