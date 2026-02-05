import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- CONFIGURATION STRAVA ---
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

# --- GESTION DYNAMIQUE DE L'URL DE REDIRECTION ---
# Si tu es sur ton PC, il prendra localhost:32123
# Si tu es sur le serveur, il faudra configurer STRAVA_REDIRECT_URI=https://stradisimo.fr
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:32123")