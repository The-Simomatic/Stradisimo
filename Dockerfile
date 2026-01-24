FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

# Mesop écoute par défaut sur 0.0.0.0, pas besoin de --host
CMD ["sh", "-c", "mesop app.py -- --port=$PORT"]
