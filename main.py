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

        # --- AJOUT : Charger les activités lors du chargement du profil ---
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

# ... (tes imports restent identiques)

def handle_strava_callback(s: State):
    """Capture le code OAuth au retour de Strava et initialise la connexion."""
    # On utilise me.query_params() comme une fonction si nécessaire selon la version, 
    # mais ton accès direct semble correct pour ta version.
    qp = me.query_params
    code = qp.get("code")
    
    if code and s.is_logged_in and not getattr(s, "is_loading", False):
        s.is_loading = True
        
        token_data = su.exchange_code_for_token(code)
        
        if token_data and 'access_token' in token_data:
            # 1. Sauvegarde en Base
            data_to_save = {
                "strava_access_token": token_data['access_token'],
                "strava_refresh_token": token_data['refresh_token'],
                "strava_expires_at": token_data['expires_at'],
                "strava_athlete_id": str(token_data['athlete']['id'])
            }
            db.update_profile(s.user_id, data_to_save)
            
            # 2. Mise à jour du State
            s.strava_access_token = token_data['access_token']
            s.strava_refresh_token = token_data['refresh_token']
            s.is_strava_linked = True
            
            # 3. Première Synchro Immédiate
            su.sync_latest_activities(s.user_id, s)
            
            # 4. Refresh des données locales
            activities = db.get_latest_activities(s.user_id)
            s.recent_activities_json = json.dumps(activities)
            
            s.success_message = "Compte Strava connecté avec succès !"
            s.is_loading = False
            
            # 5. REDIRECTION CRITIQUE : on nettoie l'URL pour enlever le ?code=
            # On redirige vers les réglages pour que l'utilisateur voie le succès
            s.current_page = "settings"
            s.active_sub_menu = "strava_main"
            me.navigate("/") 
        else:
            s.error_message = "Échec de la connexion Strava : code invalide ou expiré."
            s.is_loading = False

# --- CONFIGURATION DE LA PAGE PRINCIPALE ---

@me.page(
    path="/", 
    title="Stradisimo - Entraînement Vélo et Course à Pied", 
    stylesheets=[st.FONTS_URL]
)
def main():
    s = me.state(State)
    
    # 1. Gestion des callbacks d'URL (Priorité haute)
    handle_recovery_logic(s)
    handle_strava_callback(s)

    # 2. Synchronisation Intelligente
    # On ne synchronise que si l'utilisateur est sur le Dashboard et qu'il est lié
    if s.is_logged_in and getattr(s, "is_strava_linked", False) and s.current_page == "dashboard":
        # On vérifie le token en arrière-plan
        su.refresh_strava_token_if_needed(s.user_id, s)
        
        # On ne lance la synchro que si elle n'a pas été faite récemment (ex: > 15 min)
        # Cette logique de "if_needed" doit idéalement être dans strava_utils.py
        su.sync_latest_activities(s.user_id, s)
        
        # Mise à jour du JSON pour les graphiques
        activities = db.get_latest_activities(s.user_id)
        if activities:
            s.recent_activities_json = json.dumps(activities)

    # 3. Rendu de l'interface (Inchangé)
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
                    with me.box(style=me.Style(display="flex", justify_content="center", width="100%")):
                        me.progress_spinner()
                
                PAGES_INTERNES[s.current_page](s)