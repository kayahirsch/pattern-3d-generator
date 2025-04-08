# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy your files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set environment variable manually
ENV FLASK_APP=wsgi.py

# Expose port for Fly.io
EXPOSE 8080

# Run Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
