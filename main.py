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
from profile import render_profile_setup # Import de la page de profil obligatoire [cite: 2026-01-22]

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
        # C'est ici que l'erreur se produisait : on utilise sport_pref
        s.sport_pref = profile.get("sport_pref") or ""

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

def handle_login(e: me.ClickEvent):
    """Gère la connexion utilisateur et initialise le State [cite: 2026-01-22]."""
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
        # Récupération immédiate du profil après login
        profile, _ = db.get_user_profile(user.id)
        if profile:
            update_state_from_profile(s, profile)
        s.is_logged_in = True
        s.error_message = ""
    
    s.is_loading = False 

def handle_logout(e: me.ClickEvent):
    """Déconnecte l'utilisateur et réinitialise l'application [cite: 2026-01-22]."""
    s = me.state(State)
    db.supabase.auth.sign_out()
    s.is_logged_in = False
    s.user_id = ""
    s.current_page = "dashboard"
    s.email = ""
    s.password = ""
    s.error_message = ""
    s.show_signup = False
    # Nettoyage des données profil
    s.prenom = ""
    s.nom = ""

# --- CONFIGURATION DE LA PAGE PRINCIPALE ---

@me.page(path="/", title="Stradisimo", stylesheets=[st.FONTS_URL])
def main():
    s = me.state(State)
    
    # 1. PERSISTANCE : Reconnexion automatique si une session existe [cite: 2026-01-22]
    if not s.is_logged_in:
        try:
            res = db.supabase.auth.get_user()
            if res and res.user:
                s.is_logged_in = True
                s.user_id = res.user.id
                profile, _ = db.get_user_profile(res.user.id)
                if profile:
                    update_state_from_profile(s, profile)
        except:
            pass

    # 2. RÉCUPÉRATION : Détection du mode reset mot de passe [cite: 2026-01-22]
    params = me.query_params
    token = params.get("token")
    is_recovery_mode = params.get("type") == "recovery"

    # Échange du token contre une session active pour éviter "Auth session missing" [cite: 2026-01-22]
    if is_recovery_mode and token and not s.is_logged_in:
        success, res = db.verify_recovery_token(token)
        if success:
            s.is_logged_in = True
            s.user_id = res.user.id

    with me.box(style=st.MAIN_BOX_STYLE):
        # HEADER (Toujours présent)
        cp.render_header(s, on_logout=handle_logout)
        
        with me.box(style=me.Style(height=4, width="100%", margin=me.Margin.symmetric(vertical=10))):
            pass 

        # --- LOGIQUE DE NAVIGATION ---
        
        # PRIORITÉ A : Consultation des CGU [cite: 2026-01-22]
        if s.current_page == "cgu":
            cgu_screen(s)

        # PRIORITÉ B : Réinitialisation de mot de passe via lien email [cite: 2026-01-22]
        elif is_recovery_mode:
            render_password_reset(s)

        # PRIORITÉ C : Authentification (Utilisateur non connecté) [cite: 2026-01-22]
        elif not s.is_logged_in:
            if s.show_signup:
                render_signup(s)
            else:
                render_login(s, on_login=handle_login)

        # PRIORITÉ D : Configuration de profil OBLIGATOIRE [cite: 2026-01-22]
        # Si connecté mais sans prénom ou nom, on impose l'écran de profil [cite: 2026-01-22]
        elif s.is_logged_in and (not s.prenom or not s.nom):
            render_profile_setup(s)

        # PRIORITÉ E : Accès complet (Connecté et Profil OK) [cite: 2026-01-22]
        else:
            cp.render_navbar(s)

            with me.box(style=me.Style(
                width="100%", 
                margin=me.Margin.symmetric(vertical=20),
                display="flex",
                flex_direction="column",
                align_items="center"
            )):
                if s.current_page == "dashboard":
                    dashboard_screen(s)
                elif s.current_page == "planning":
                    planning_screen(s)
                elif s.current_page == "cv":
                    cv_screen(s)
                elif s.current_page == "settings":
                    settings_screen(s)

        # ESPACE DE FIN DE PAGE
        with me.box(style=me.Style(height=40)):
            pass