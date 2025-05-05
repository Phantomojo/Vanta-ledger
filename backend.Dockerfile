# Use official Python image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY ./src ./src

# Expose port
EXPOSE 8500

# Set environment variables
ENV PYTHONPATH=/app/src

# Run the backend server
CMD ["uvicorn", "vanta_ledger.main:app", "--host", "0.0.0.0", "--port", "8500"]
