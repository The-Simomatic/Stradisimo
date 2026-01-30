import mesop as me
import styles as st
import supabase_db as db
from state import State
from profile import render_profile_setup 

def settings_screen(s: State): 
    with me.box(style=me.Style(width="100%", max_width=600, margin=me.Margin.symmetric(horizontal="auto", vertical=20))):
        me.text("PARAMÈTRES", style=st.LOGIN_TITLE_STYLE)
        
        # --- RUBRIQUE 1 : PROFIL ---
        # Remplace label par title ici
        with me.expansion_panel(title="👤 Modifier mon profil"):
            render_profile_setup(s)

        # --- RUBRIQUE 2 : SÉCURITÉ ---
        # Et ici aussi
        with me.expansion_panel(title="🔐 Sécurité & Mot de passe"):
            me.text("Souhaitez-vous modifier votre mot de passe ?", style=me.Style(margin=me.Margin(bottom=15)))
            me.button(
                "RECEVOIR UN LIEN DE RÉINITIALISATION", 
                type="stroked", 
                on_click=on_request_reset_click
            )

        # --- RUBRIQUE 3 : IMPORTATION ---
        with me.expansion_panel(title="📥 Importation de données"):
            me.text("Importer toutes les activités Strava", style=me.Style(font_weight="bold"))
            me.button("IMPORTER (BIENTÔT)", disabled=True)

        # --- RUBRIQUE 4 : CONNEXIONS ---
        with me.expansion_panel(title="🔗 Services connectés"):
            me.button("SE CONNECTER À STRAVA", type="flat", disabled=True, style=me.Style(background="#FC6100", color="white"))

def on_request_reset_click(e: me.ClickEvent):
    s = me.state(State)
    if s.email:
        success, message = db.reset_password(s.email)
        s.error_message = message