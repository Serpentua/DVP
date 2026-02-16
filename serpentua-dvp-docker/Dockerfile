FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for PyMySQL/cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8443

ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8443

CMD ["python", "runserver.py"]
