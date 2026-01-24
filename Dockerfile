FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

# IMPORTANT: utiliser la vraie commande Mesop
CMD ["sh", "-c", "mesop run app.py --host=0.0.0.0 --port=$PORT"]
