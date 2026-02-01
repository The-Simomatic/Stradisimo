import mesop as me
import styles as st
import components as cp
from state import State
from auth import render_login, render_signup, render_password_reset
from dashboard import dashboard_screen
from planning import planning_screen
from cv_sportif import cv_screen
from settings import settings_screen
from cgu import cgu_screen  
from profile import render_profile_setup 
from password_reset import password_reset_screen

# --- LOGIQUE BASE DE DONNÉES ---
import supabase_db as db

# --- UTILITAIRES ---

def update_state_from_profile(s: State, profile: dict):
    """Met à jour les variables d'état à partir des données Supabase."""
    if profile:
        s.prenom = profile.get("prenom") or ""
        s.nom = profile.get("nom") or ""
        s.poids = str(profile.get("poids", ""))
        s.niveau = profile.get("niveau") or "Débutant"
        s.date_n = profile.get("date_n") or ""
        s.sexe = profile.get("sexe") or ""
        s.sport_pref = profile.get("sport_pref") or ""
        try:
            s.vma = float(profile.get("vma") or 0.0)
        except (ValueError, TypeError):
            s.vma = 0.0

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

def handle_login(e: me.ClickEvent):
    """Gère la connexion, initialise le State privé et redirige."""
    s = me.state(State)
    
    if not s.email or not s.password:
        s.error_message = "Veuillez remplir tous les champs."
        return

    s.is_loading = True 
    s.error_message = "" 
    
    result = db.login_user(s.email, s.password)
    
    if result["error"]:
        s.error_message = result["error"]
        s.is_loading = False
        return

    user = result["user"]
    if user:
        # On stocke les infos uniquement dans le State isolé par Mesop
        s.user_id = user.id
        s.email = user.email
        s.password = "" 
        
        # Récupération du profil via l'ID sécurisé
        profile, _ = db.get_user_profile(user.id)
        if profile:
            update_state_from_profile(s, profile)
        
        s.is_logged_in = True
        
        if not s.prenom or not s.nom:
            s.is_completing_profile = True
            s.current_page = "profile_edit"
        else:
            s.is_completing_profile = False
            s.current_page = "dashboard"
            
    s.is_loading = False 

def handle_logout(e: me.ClickEvent):
    """Nettoyage complet du State pour éviter toute fuite de données."""
    s = me.state(State)
    db.supabase.auth.sign_out()
    
    # Reset de toutes les variables sensibles
    s.is_logged_in = False
    s.user_id = ""
    s.email = ""
    s.prenom = ""
    s.nom = ""
    s.current_page = "login"
    s.error_message = ""
    s.show_signup = False

# --- CONFIGURATION DE LA PAGE PRINCIPALE ---

@me.page(
    path="/", 
    title="Stradisimo - Entraînement Vélo et Course à Pied", 
    stylesheets=[st.FONTS_URL]
)
def main():
    s = me.state(State)
    
    # --- GESTION RECOVERY (Mot de passe oublié) ---
    params = me.query_params
    token = params.get("token")
    # On harmonise le nom ici
    is_recovery_mode = params.get("type") == "recovery"

    if is_recovery_mode and token and s.current_page != "password_edit":
        success, res = db.verify_recovery_token(token)
        if success:
            s.is_logged_in = True
            s.user_id = res.user.id
            s.email = res.user.email
            s.current_page = "password_edit"
        else:
            s.error_message = "Lien de récupération invalide ou expiré."
            s.current_page = "login"

    with me.box(style=st.MAIN_BOX_STYLE):
        cp.render_header(s, on_logout=handle_logout)
        
        # Séparateur turquoise subtil
        with me.box(style=me.Style(height=1, width="100%", background="rgba(40, 165, 168, 0.3)", margin=me.Margin(bottom=30))):
            pass

        # --- NAVIGATION ---
        if s.current_page == "cgu":
            cgu_screen(s)
        # Priorité à l'écran de reset si le state le demande
        elif s.current_page == "password_edit":
            password_reset_screen(s)
        # Si on n'est pas connecté, login ou signup
        elif not s.is_logged_in:
            if s.show_signup:
                render_signup(s)
            else:
                render_login(s, on_login=handle_login)
        # Si connecté mais profil incomplet
        elif s.is_logged_in and (s.is_completing_profile or not s.prenom or not s.nom):
            render_profile_setup(s)
        # Sinon, accès aux pages internes
        else:
            cp.render_navbar(s)
            
            valid_pages = ["dashboard", "planning", "cv", "settings", "profile_edit"]
            if s.current_page not in valid_pages:
                s.current_page = "dashboard"

            with me.box(style=me.Style(width="100%", max_width=800, margin=me.Margin.symmetric(vertical=10), display="flex", flex_direction="column", align_items="center")):
                if s.is_loading:
                    me.progress_spinner(style=me.Style(margin=me.Margin(bottom=20)))

                if s.current_page == "dashboard":
                    dashboard_screen(s)
                elif s.current_page == "planning":
                    planning_screen(s)
                elif s.current_page == "cv":
                    cv_screen(s)
                elif s.current_page == "settings":
                    settings_screen(s)
                elif s.current_page == "profile_edit":
                    render_profile_setup(s)