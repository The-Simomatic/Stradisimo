from supabase import create_client, Client
from datetime import datetime
import config as cfg

# --- INITIALISATION ---
supabase: Client = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)

# --- AUTHENTIFICATION ---

def login_user(email, password):
    """Tente de connecter l'utilisateur via Supabase Auth."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {"user": response.user, "session": response.session, "error": None}
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return {"user": None, "session": None, "error": "Email ou mot de passe incorrect."}
        return {"user": None, "session": None, "error": f"Erreur de connexion : {error_msg}"}

def signup_user(email, password):
    """Crée un nouvel utilisateur."""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return {"user": response.user, "error": None}
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return {"user": None, "error": "Cet email est déjà utilisé."}
        return {"user": None, "error": error_msg}

# --- RÉCUPÉRATION DE COMPTE ---

def reset_password(email):
    """Envoie un e-mail de réinitialisation."""
    try:
        supabase.auth.reset_password_for_email(email)
        return True, "Un lien de récupération a été envoyé sur votre boîte mail."
    except Exception as e:
        return False, f"Erreur : {str(e)}"

def verify_recovery_token(token):
    """Échange le token reçu par mail contre une session active."""
    try:
        response = supabase.auth.verify_otp({"token": token, "type": "recovery"})
        # Définit la session pour les appels authentifiés suivants
        supabase.auth.set_session(response.session.access_token, response.session.refresh_token)
        return True, response
    except Exception as e:
        print(f"DEBUG RECOVERY ERROR: {e}")
        return False, str(e)

def update_user_password(new_password):
    """Met à jour le mot de passe de l'utilisateur."""
    try:
        supabase.auth.update_user({"password": new_password})
        return True, "Votre mot de passe a été mis à jour avec succès."
    except Exception as e:
        return False, f"Erreur lors de la mise à jour : {str(e)}"

# --- GESTION DU PROFIL (DATABASE) ---

def get_user_profile(user_id):
    """Récupère les infos du profil utilisateur."""
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0], None
        return None, "Aucun profil trouvé."
    except Exception as e:
        return None, str(e)

def update_profile(user_id, data):
    """Met à jour ou crée le profil utilisateur (Upsert)."""
    try:
        payload = {
            "id": user_id,
            "updated_at": datetime.now().isoformat(),
            **data
        }
        supabase.table("profiles").upsert(payload).execute()
        return True, "Profil mis à jour."
    except Exception as e:
        return False, f"Erreur base de données : {str(e)}"

# --- GESTION DES ACTIVITÉS STRAVA ---

def upsert_activities(activities_list):
    """
    Insère une liste d'activités ou les met à jour si elles existent déjà.
    Utilise 'strava_id' comme clé de conflit pour éviter les doublons.
    """
    if not activities_list:
        return None
    
    try:
        # L'upsert sur une liste est très efficace chez Supabase (une seule requête)
        response = supabase.table("activities").upsert(
            activities_list, 
            on_conflict="strava_id"
        ).execute()
        return response
    except Exception as e:
        print(f"❌ Erreur Upsert Activités : {e}")
        return None

def get_latest_activities(user_id: str, limit: int = 3):
    try:
        # On demande explicitement le tri descendant sur la date
        response = (
            supabase.table("activities")
            .select("*")
            .eq("user_id", user_id)
            .order("start_date", desc=True) 
            .limit(limit)
            .execute()
        )
        return response.data # Retourne une liste de dicts []
    except Exception as e:
        print(f"Erreur DB: {e}")
        return []