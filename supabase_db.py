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
        # Personnalisation des messages d'erreur courants
        if "Invalid login credentials" in error_msg:
            return {"user": None, "session": None, "error": "Email ou mot de passe incorrect."}
        return {"user": None, "session": None, "error": f"Erreur de connexion : {error_msg}"}

def signup_user(email, password):
    """Crée un nouvel utilisateur et déclenche l'envoi d'un email de validation."""
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
        return True, response
    except Exception as e:
        return False, str(e)

def update_user_password(new_password):
    """Met à jour le mot de passe de l'utilisateur en session (suite à une récupération)."""
    try:
        supabase.auth.update_user({"password": new_password})
        return True, "Votre mot de passe a été mis à jour avec succès."
    except Exception as e:
        return False, f"Erreur lors de la mise à jour : {str(e)}"

# --- GESTION DU PROFIL (DATABASE) ---

def get_current_user_email():
    """Récupère l'email de l'utilisateur actuellement connecté."""
    try:
        user_response = supabase.auth.get_user()
        if user_response and user_response.user:
            return user_response.user.email
        return None
    except Exception:
        return None

def get_user_profile(user_id):
    """
    Récupère les données du profil. 
    Retourne (data, error). Si le profil n'existe pas, data sera None.
    """
    try:
        # .single() peut lever une exception si aucun enregistrement n'est trouvé
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0], None
        return None, "Aucun profil trouvé."
    except Exception as e:
        return None, str(e)

def update_profile(user_id, data):
    """
    Crée ou met à jour le profil dans la table 'profiles'.
    data : dictionnaire contenant prenom, nom, date_n, poids, niveau, sexe, vma, etc.
    """
    try:
        # On utilise le format ISO de Python pour la date de mise à jour
        payload = {
            "id": user_id,
            "updated_at": datetime.now().isoformat(),
            **data
        }
        # upsert gère l'INSERT ou l'UPDATE automatiquement selon la Primary Key (id)
        supabase.table("profiles").upsert(payload).execute()
        return True, "Profil mis à jour avec succès."
    except Exception as e:
        return False, f"Erreur base de données : {str(e)}"