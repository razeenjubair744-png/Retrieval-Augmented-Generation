# Use an official Python 3.12 slim image to match our working environment
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# build-essential is required if any python packages need to compile C extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 7860 (Gradio default) but we dynamically bind to $PORT for Render
EXPOSE 7860

# Ensure logs are not buffered by Python so they stream immediately to the Render dashboard
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "gradio_app.py"]
