import mesop as me
import styles as st
import components as cp
from state import State
from auth import render_login, render_signup
from dashboard import dashboard_screen
from planning import planning_screen
from cv_sportif import cv_screen
from settings import settings_screen
from cgu import cgu_screen  
from profile import render_profile_setup 
from password_reset import password_reset_screen
import strava_utils as su 
import json

# --- LOGIQUE BASE DE DONNÉES ---
import supabase_db as db

# --- CONFIGURATION DU ROUTAGE ---
PAGES_INTERNES = {
    "dashboard": dashboard_screen,
    "planning": planning_screen,
    "cv": cv_screen,
    "settings": settings_screen,
    "profile_edit": render_profile_setup,
}

# --- UTILITAIRES ---

def update_state_from_profile(s: State, profile: dict):
    """Met à jour les variables d'état à partir des données Supabase."""
    if profile:
        s.prenom = profile.get("prenom") or ""
        s.nom = profile.get("nom") or ""
        s.date_n = profile.get("date_n") or ""
        s.poids = profile.get("poids") or 0.0
        s.vma = profile.get("vma") or 0.0
        s.sexe = profile.get("sexe") or ""
        s.sport_pref = profile.get("sport_pref") or ""
        s.niveau = profile.get("niveau") or "Débutant"

        s.strava_refresh_token = profile.get("strava_refresh_token") or ""
        s.strava_access_token = profile.get("strava_access_token") or ""
        
        expires_at = profile.get("strava_expires_at")
        try:
            s.strava_expires_at = int(expires_at) if expires_at else 0
        except:
            s.strava_expires_at = 0
        
        last_sync = profile.get("last_strava_sync")
        s.last_strava_sync = str(last_sync) if last_sync else ""
        s.is_strava_linked = bool(s.strava_refresh_token)

        # --- AJOUT ICI : Charger les activités lors du chargement du profil ---
        activities = db.get_latest_activities(s.user_id)
        s.recent_activities_json = json.dumps(activities)

def handle_recovery_logic(s: State):
    """Gère la détection du token de récupération de mot de passe."""
    params = me.query_params
    token = params.get("token")
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

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

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
        s.user_id = user.id
        s.email = user.email
        s.password = "" 
        
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
    s = me.state(State)
    db.supabase.auth.sign_out()
    s.is_logged_in = False
    s.user_id = ""
    s.email = ""
    s.prenom = ""
    s.nom = ""
    s.recent_activities_json = "[]" # On vide aussi les activités
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
    handle_recovery_logic(s)

    # --- RAFFRAÎCHISSEMENT SILENCIEUX STRAVA ---
    if s.is_logged_in and getattr(s, "is_strava_linked", False) and s.user_id:
        if su.refresh_strava_token_if_needed(s.user_id, s):
            # 1. On synchronise avec Strava vers Supabase
            su.sync_latest_activities(s.user_id, s)
            # 2. AJOUT ICI : On recharge les données de la DB vers le State après synchro
            activities = db.get_latest_activities(s.user_id)
            s.recent_activities_json = json.dumps(activities)

    with me.box(style=st.MAIN_BOX_STYLE):
        cp.render_header(s, on_logout=handle_logout)
        with me.box(style=me.Style(height=1, width="100%", background="rgba(40, 165, 168, 0.3)", margin=me.Margin(bottom=30))):
            pass

        if s.current_page == "cgu":
            cgu_screen(s)
        elif s.current_page == "password_edit":
            password_reset_screen(s)
        elif not s.is_logged_in:
            if s.show_signup:
                render_signup(s)
            else:
                render_login(s, on_login=handle_login)
        elif s.is_logged_in and (s.is_completing_profile or not s.prenom or not s.nom):
            render_profile_setup(s)
        else:
            cp.render_navbar(s)
            if s.current_page not in PAGES_INTERNES:
                s.current_page = "dashboard"

            with me.box(style=st.CONTENT_CONTAINER):
                if s.is_loading:
                    me.progress_spinner(style=me.Style(margin=me.Margin(bottom=20)))
                PAGES_INTERNES[s.current_page](s)