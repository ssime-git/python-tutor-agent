FROM python:3.10-slim

WORKDIR /app

# Install required libraries
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Create directory for temporary files
RUN mkdir -p /tmp/executions

# Copy the service code
COPY app.py .

# Expose the service port
EXPOSE 8080

# Run the FastAPI service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]