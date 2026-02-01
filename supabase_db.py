from supabase import create_client, Client
from datetime import datetime
import config as cfg

# --- INITIALISATION ---
# Ce client reste global pour les opérations de base ou publiques
supabase: Client = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)

# --- AUTHENTIFICATION ---

def login_user(email, password):
    """Tente de connecter l'utilisateur via Supabase Auth."""
    try:
        # On utilise le client global uniquement pour l'action de login
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
    """Envoie un e-mail de réinitialisation de mot de passe."""
    try:
        supabase.auth.reset_password_for_email(email)
        return True, "Un lien de récupération a été envoyé sur votre boîte mail."
    except Exception as e:
        return False, f"Erreur : {str(e)}"

def verify_recovery_token(token):
    """Échange le token reçu par mail contre une session active."""
    try:
        response = supabase.auth.verify_otp({"token": token, "type": "recovery"})
        # IMPORTANT : On définit la session sur le client global pour que 
        # l'appel suivant 'update_user' soit autorisé.
        supabase.postgrest.auth(response.session.access_token) 
        return True, response
    except Exception as e:
        return False, str(e)

def update_user_password(new_password):
    """Met à jour le mot de passe de l'utilisateur."""
    try:
        # ATTENTION : Cette action nécessite que le client global 
        # ait la session active du demandeur.
        supabase.auth.update_user({"password": new_password})
        return True, "Votre mot de passe a été mis à jour avec succès."
    except Exception as e:
        return False, f"Erreur lors de la mise à jour : {str(e)}"

# --- GESTION DU PROFIL (DATABASE) ---

def get_user_profile(user_id):
    """
    Récupère les données du profil de manière isolée via l'ID.
    """
    try:
        # On utilise explicitement le user_id passé par le State de Mesop
        # pour filtrer la table, sans faire confiance à la session du client global.
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0], None
        return None, "Aucun profil trouvé."
    except Exception as e:
        return None, str(e)

def update_profile(user_id, data):
    """
    Crée ou met à jour le profil dans la table 'profiles'.
    """
    try:
        payload = {
            "id": user_id,
            "updated_at": datetime.now().isoformat(),
            **data
        }
        # Upsert basé sur l'ID fourni par le State utilisateur
        supabase.table("profiles").upsert(payload).execute()
        return True, "Profil mis à jour avec succès."
    except Exception as e:
        return False, f"Erreur base de données : {str(e)}"