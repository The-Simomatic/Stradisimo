FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# On définit explicitement la variable d'environnement PORT
ENV PORT=8080

# Commande de lancement robuste
# On force l'hôte à 0.0.0.0 pour que Cloud Run puisse voir l'app
CMD ["python", "-m", "mesop", "run", "app.py", "--host", "0.0.0.0", "--port", "8080"]