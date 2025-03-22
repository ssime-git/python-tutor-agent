FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# install with uv without venv
RUN pip install uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

COPY app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]