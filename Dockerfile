# 1. On part d'une version de Python toute prête
FROM python:3.11-slim

# 2. On définit le dossier où l'app va vivre dans le serveur
WORKDIR /app

# 3. On copie d'abord le fichier des dépendances
COPY requirements.txt .

# 4. On installe toutes les bibliothèques (Pandas, Mesop, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. On copie tout le reste de ton code dans le serveur
COPY . .

# 6. On dit au serveur que l'app écoute sur le port 8080 (standard Cloud Run)
EXPOSE 8080

# 7. La commande pour lancer l'app Mesop
# (Remplace app.py par ton fichier principal si c'est main.py)
CMD ["mesop", "app.py", "--port=8080"]