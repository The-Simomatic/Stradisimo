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
    """Met à jour les variables d'état à partir des données Supabase avec conversion de types."""
    if profile:
        s.prenom = profile.get("prenom") or ""
        s.nom = profile.get("nom") or ""
        s.poids = str(profile.get("poids", ""))
        s.niveau = profile.get("niveau") or "Débutant"
        s.date_n = profile.get("date_n") or ""
        s.sexe = profile.get("sexe") or ""
        s.sport_pref = profile.get("sport_pref") or ""
        # Conversion sécurisée de la VMA (numeric -> float)
        try:
            s.vma = float(profile.get("vma") or 0.0)
        except (ValueError, TypeError):
            s.vma = 0.0

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

def handle_login(e: me.ClickEvent):
    """Gère la connexion utilisateur, initialise le State et redirige."""
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
        s.user_id = user.id
        s.email = user.email 
        s.password = "" # Sécurité : on vide le password
        
        # Récupération immédiate du profil
        profile, _ = db.get_user_profile(user.id)
        if profile:
            update_state_from_profile(s, profile)
        
        s.is_logged_in = True
        
        # --- LOGIQUE DE REDIRECTION POST-LOGIN ---
        if not s.prenom or not s.nom:
            s.is_completing_profile = True
            s.current_page = "profile_edit"
        else:
            s.is_completing_profile = False
            s.current_page = "dashboard"
            
        s.error_message = ""
    
    s.is_loading = False 

def handle_logout(e: me.ClickEvent):
    """Déconnecte l'utilisateur et réinitialise l'application."""
    s = me.state(State)
    db.supabase.auth.sign_out()
    s.is_logged_in = False
    s.user_id = ""
    s.current_page = "login"
    s.email = ""
    s.password = ""
    s.error_message = ""
    s.show_signup = False
    s.is_completing_profile = False
    s.prenom = ""
    s.nom = ""

# --- CONFIGURATION DE LA PAGE PRINCIPALE ---

@me.page(path="/", title="Stradisimo - Entrainement Vélo et Course à Pied", stylesheets=[st.FONTS_URL])
def main():
    s = me.state(State)
    
    # 1. PERSISTANCE : Reconnexion automatique au rafraîchissement
    if not s.is_logged_in:
        try:
            res = db.supabase.auth.get_user()
            if res and res.user:
                s.is_logged_in = True
                s.user_id = res.user.id
                s.email = res.user.email
                profile, _ = db.get_user_profile(res.user.id)
                if profile:
                    update_state_from_profile(s, profile)
                
                if not s.prenom or not s.nom:
                    s.is_completing_profile = True
        except:
            pass

    # 2. RÉCUPÉRATION : Mode recovery via URL (Mot de passe oublié)
    params = me.query_params
    token = params.get("token")
    is_recovery_mode = params.get("type") == "recovery"

    if is_recovery_mode and token and not s.is_logged_in:
        success, res = db.verify_recovery_token(token)
        if success:
            s.is_logged_in = True
            s.user_id = res.user.id
            s.email = res.user.email
            s.current_page = "password_edit"
            
            # Nettoyage de l'URL pour ancrer la session Supabase
            me.navigate("/")
            return 

    with me.box(style=st.MAIN_BOX_STYLE):
        # HEADER
        cp.render_header(s, on_logout=handle_logout)
        
        # SÉPARATEUR VISUEL (Adapté au thème bleu nuit / turquoise)
        with me.box(style=me.Style(
            height=1,
            width="100%", 
            background="rgba(40, 165, 168, 0.3)", # Turquoise subtil
            margin=me.Margin(bottom=30)
        )):
            pass

        # --- LOGIQUE DE NAVIGATION ---
        
        # A. Consultation CGU (Toujours prioritaire)
        if s.current_page == "cgu":
            cgu_screen(s)

        # B. Mot de passe oublié (Lien email actif)
        elif is_recovery_mode:
            render_password_reset(s)

        # C. Non connecté : Login ou Signup
        elif not s.is_logged_in:
            if s.show_signup:
                render_signup(s)
            else:
                render_login(s, on_login=handle_login)

        # D. Connecté mais Profil Incomplet (VERROU)
        elif s.is_logged_in and (s.is_completing_profile or not s.prenom or not s.nom):
            render_profile_setup(s)

        # E. Accès complet (Dashboard, Planning, etc.)
        else:
            cp.render_navbar(s)

            # Sécurité des routes
            valid_pages = ["dashboard", "planning", "cv", "settings", "profile_edit", "password_edit"]
            if s.current_page not in valid_pages:
                s.current_page = "dashboard"

            with me.box(style=me.Style(
                width="100%", 
                max_width=800,
                margin=me.Margin.symmetric(vertical=10),
                display="flex",
                flex_direction="column",
                align_items="center"
            )):
                # Loader discret si une action est en cours
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
                elif s.current_page == "password_edit":
                    password_reset_screen(s)
                
        # FOOTER
        with me.box(style=me.Style(height=40)):
            pass