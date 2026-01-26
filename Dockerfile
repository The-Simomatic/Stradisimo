# --- IMAGE DE BASE ---
FROM python:3.11-slim

# --- TRAVAIL DANS /app ---
WORKDIR /app

# --- COPIE ET INSTALLATION DES DÉPENDANCES ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- COPIE DU CODE ---
COPY . .

# --- PORT EXPOSE POUR CLOUD RUN ---
# Cloud Run injecte PORT=8080 automatiquement
EXPOSE 8080

# --- COMMANDE DE LANCEMENT ---
# On utilise le CLI Mesop pour lancer l'app
# Cloud Run utilisera le PORT défini dans l'environnement
CMD ["python", "-m", "mesop", "run", "app.py", "--host", "0.0.0.0", "--port", "8080"]
