FROM python:3.11-slim
WORKDIR /app

# System deps (faster builds + reliable wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Entry point: send support emails (no browser)
CMD ["python","-u","support_only.py"]
