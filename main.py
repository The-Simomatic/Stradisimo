import mesop as me
import styles as st
import components as cp
from state import State
from auth import render_login, render_signup, render_password_reset # <-- Nouvel import
from dashboard import dashboard_screen
from planning import planning_screen
from cv_sportif import cv_screen
from settings import settings_screen
from cgu import cgu_screen  

# --- LOGIQUE BASE DE DONNÉES ---
import supabase_db as db

# --- UTILITAIRES ---

def update_state_from_profile(s: State, profile: dict):
    """Met à jour les variables d'état à partir des données Supabase."""
    if profile:
        s.poids = str(profile.get("poids", "0"))
        s.sport = profile.get("sport") or "Non renseigné"
        s.niveau = profile.get("niveau") or "Débutant"

# --- LOGIQUE D'AUTHENTIFICATION ---

def handle_login(e: me.ClickEvent):
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
        profile, profile_error = db.get_user_profile(user.id)
        if profile:
            update_state_from_profile(s, profile)
            s.is_logged_in = True
            s.error_message = ""
        else:
            s.error_message = "Profil introuvable en base de données."
    
    s.is_loading = False 

def handle_logout(e: me.ClickEvent):
    """Réinitialise l'état lors de la déconnexion."""
    s = me.state(State)
    s.is_logged_in = False
    s.current_page = "dashboard"
    s.email = ""
    s.password = ""
    s.error_message = ""
    s.show_signup = False

# --- PAGE PRINCIPALE ---

@me.page(path="/", title="Stradisimo", stylesheets=[st.FONTS_URL])
def main():
    s = me.state(State)
    
    # --- INTERCEPTION DES PARAMÈTRES D'URL ---
    # Permet de détecter si l'utilisateur vient du mail de récupération
    params = me.query_params()
    is_recovery_mode = params.get("type") == "recovery"
    
    with me.box(style=st.MAIN_BOX_STYLE):
        # 1. HEADER COMMUN
        cp.render_header(s, on_logout=handle_logout)
        
        # 2. ESPACEMENT SOUS HEADER
        with me.box(style=me.Style(height=4, width="100%", margin=me.Margin.symmetric(vertical=10))):
            pass 

        # --- LOGIQUE DE NAVIGATION PRIORITAIRE ---
        
        # A. Cas de la page CGU (Accessible à tous)
        if s.current_page == "cgu":
            cgu_screen(s)

        # B. Cas RECOVERY (Lien mot de passe oublié)
        elif is_recovery_mode:
            render_password_reset(s)

        # C. Cas Utilisateur NON CONNECTÉ
        elif not s.is_logged_in:
            if s.show_signup:
                render_signup(s)
            else:
                render_login(s, on_login=handle_login)

        # D. Cas Utilisateur CONNECTÉ
        else:
            # 3. BARRE DE NAVIGATION
            cp.render_navbar(s)

            # 4. ZONE DE CONTENU DYNAMIQUE
            with me.box(style=me.Style(
                width="100%", 
                margin=me.Margin.symmetric(vertical=20),
                display="flex",
                flex_direction="column",
                align_items="center",
                justify_content="center"
            )):
                if s.current_page == "dashboard":
                    dashboard_screen(s)
                elif s.current_page == "planning":
                    planning_screen(s)
                elif s.current_page == "cv":
                    cv_screen(s)
                elif s.current_page == "settings":
                    settings_screen(s)

        # 5. PIED DE PAGE 
        with me.box(style=me.Style(height=40)):
            pass