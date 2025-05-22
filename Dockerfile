# Use an official Python runtime as a parent image
# Using Python 3.9 as an example, you can adjust to 3.10 or 3.11 if needed,
# ensuring compatibility with your dependencies.
FROM python:3.9-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Set environment variables for Python
# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files to disc.
# PYTHONUNBUFFERED=1: Ensures Python output (like print statements) is sent
#                     straight to terminal/logs without being buffered.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies if any are discovered during testing.
# For common Flask apps, this might not be needed initially.
# Example:
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container first to leverage Docker layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt .

# Install NLTK and download its necessary data packages (punkt, stopwords)
# NLTK_DATA environment variable will be set in Azure App Service
# to point to /usr/local/share/nltk_data where these are downloaded.
RUN pip install --no-cache-dir nltk \
    && python -m nltk.downloader -d /usr/local/share/nltk_data punkt \
    && python -m nltk.downloader -d /usr/local/share/nltk_data stopwords

# Install Python dependencies listed in requirements.txt
# --no-cache-dir reduces image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container.
# This includes your app.py, templates, static files, other .py modules.
COPY . .

# Create the instance and uploads directories within the WORKDIR (/app).
# The app.py also attempts to create these, but doing it here ensures they exist
# when the Gunicorn process starts.
# On Azure App Service for Containers, paths under /home (which /app often maps to) are persistent.
# Permissions: 777 is overly permissive but simplest for avoiding permission issues in Docker
# on a free tier where user management might not be a primary concern.
# For production, use a non-root user and more specific permissions.
RUN mkdir -p instance uploads \
    && chmod -R 777 instance uploads

# Inform Docker that the application inside the container will listen on port 8000.
# Azure App Service for Containers will automatically map traffic from its
# external ports (80/443) to this internal port if configured (WEBSITES_PORT=8000).
EXPOSE 8000

# Define the command to run the application using Gunicorn.
# - Gunicorn is a production-grade WSGI server.
# - "--bind 0.0.0.0:8000": Makes Gunicorn listen on all network interfaces within
#   the container on port 8000.
# - "--timeout 600": Sets a worker timeout of 600 seconds (10 minutes). This can be
#   helpful for longer synchronous tasks on the free tier, but be mindful of
#   overall request limits on App Service.
# - "app:app": Tells Gunicorn to find the Flask application instance named 'app'
#   in the file 'app.py'.
# - "--worker-class eventlet": Specifies the worker type for Gunicorn, essential for
#   Flask-SocketIO to function correctly with WebSockets.
# - "-w 1": Runs a single Gunicorn worker process. This is appropriate for the
#   limited resources of the Azure App Service Free (F1) tier.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "600", "app:app", "--worker-class", "eventlet", "-w", "1"]