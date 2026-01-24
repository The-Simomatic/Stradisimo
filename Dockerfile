FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run injecte automatiquement la variable PORT
ENV PORT=8080

# --prod est crucial pour écouter sur 0.0.0.0 (toutes les interfaces réseau)
CMD ["mesop", "run", "app.py", "--prod", "--port=8080"]