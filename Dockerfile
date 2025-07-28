# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Start FastAPI server
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
