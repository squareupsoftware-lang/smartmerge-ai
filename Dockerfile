# Use lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Avoid Python buffering issues
ENV PYTHONUNBUFFERED=1

# Install system dependencies (for pandas, openpyxl)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data folder if not exists
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run FastAPI using uvicorn
CMD ["uvicorn", "api.api_server:app", "--host", "0.0.0.0", "--port", "8000"]