from supabase import create_client, Client
import config as cfg

# Initialisation du client Supabase
supabase: Client = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)

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

def reset_password(email):
    """Envoie un e-mail de réinitialisation de mot de passe via Supabase."""
    try:
        # Note : Dans Supabase, l'URL de redirection finale se configure 
        # dans le dashboard (Auth > URL Configuration)
        supabase.auth.reset_password_for_email(email)
        return True, "Un lien de récupération a été envoyé sur votre boîte mail."
    except Exception as e:
        error_msg = str(e)
        if "Email not found" in error_msg:
             return False, "Aucun compte n'est associé à cet e-mail."
        return False, f"Erreur : {error_msg}"

def update_user_password(new_password):
    """
    Met à jour le mot de passe. 
    Cette fonction marche quand l'utilisateur est authentifié (via login ou lien de reset).
    """
    try:
        supabase.auth.update_user({
            "password": new_password
        })
        return True, "Votre mot de passe a été mis à jour avec succès."
    except Exception as e:
        return False, f"Erreur lors de la mise à jour : {str(e)}"

def get_user_profile(user_id):
    """Récupère les données du profil utilisateur depuis la table 'profiles'."""
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return response.data, None
    except Exception as e:
        return None, f"Profil introuvable : {str(e)}"