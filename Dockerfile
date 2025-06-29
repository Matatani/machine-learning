FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 50051

CMD ["python", "-u", "main.py"]