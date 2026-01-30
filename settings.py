import mesop as me
import styles as st
import supabase_db as db
from state import State # <--- AJOUTE CETTE LIGNE pour enlever le souligné jaune
from profile import render_profile_setup 

def settings_screen(s: State): 
    with me.box(style=me.Style(width="100%", max_width=600, margin=me.Margin.symmetric(horizontal="auto", vertical=20))):
        me.text("PARAMÈTRES", style=st.LOGIN_TITLE_STYLE)
        
        # --- RUBRIQUE 1 : PROFIL ---
        with me.expansion_panel(label="👤 Modifier mon profil"):
            render_profile_setup(s)

        # --- RUBRIQUE 2 : SÉCURITÉ ---
        with me.expansion_panel(label="🔐 Sécurité & Mot de passe"):
            me.text("Souhaitez-vous modifier votre mot de passe ?")
            me.button(
                "RECEVOIR UN LIEN DE RÉINITIALISATION", 
                type="stroked", 
                on_click=on_request_reset_click
            )

        # --- RUBRIQUE 3 : IMPORTATION ---
        with me.expansion_panel(label="📥 Importation de données"):
            me.button("IMPORTER DEPUIS STRAVA (BIENTÔT)", disabled=True)

        # --- RUBRIQUE 4 : CONNEXIONS ---
        with me.expansion_panel(label="🔗 Services connectés"):
            me.button("CONNEXION STRAVA (BIENTÔT)", disabled=True, style=me.Style(background="#FC6100", color="white"))

# --- GESTIONNAIRE D'ÉVÉNEMENT ---

def on_request_reset_click(e: me.ClickEvent):
    """Déclenche l'envoi d'un mail de reset pour l'utilisateur connecté."""
    s = me.state(State) # Maintenant Python reconnaît 'State' [cite: 2026-01-22]
    if s.email:
        success, message = db.reset_password(s.email)
        s.error_message = message