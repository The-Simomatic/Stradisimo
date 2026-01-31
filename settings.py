import mesop as me
import styles as st
from state import State

# --- GESTIONNAIRES DE CLIC ---

def on_profile_click(e: me.ClickEvent):
    s = me.state(State)
    s.current_page = "profile_edit"

def on_password_click(e: me.ClickEvent):
    s = me.state(State)
    s.success_message = ""
    s.error_message = ""
    s.current_page = "password_edit"

def on_strava_click(e: me.ClickEvent):
    print("Connexion Strava demandée")

# --- COMPOSANT RÉUTILISABLE POUR LES TUILES ---

def render_menu_item(icon: str, label: str, on_click, sub_label: str = ""):
    """Crée une carte cliquable stylisée."""
    with me.box(on_click=on_click, style=st.SETTINGS_CARD_STYLE):
        me.icon(icon=icon, style=me.Style(margin=me.Margin(right=16), color=st.COLOR_PRIMARY))
        
        with me.box(style=me.Style(flex_grow=1)):
            me.text(label, style=st.SETTINGS_CARD_TITLE)
            if sub_label:
                me.text(sub_label, style=st.SETTINGS_CARD_SUBTITLE)
        
        me.icon(icon="chevron_right", style=me.Style(color="rgba(229, 229, 229, 0.3)"))

# --- ÉCRAN PRINCIPAL ---

def settings_screen(s: State):
    """Écran des paramètres épuré (sans bouton retour redondant)."""
    with me.box(style=st.CONTENT_CONTAINER):
        
        # 1. Titre de la page (Directement en haut)
        me.text("PARAMÈTRES", style=st.PAGE_TITLE_STYLE)
        
        # Conteneur des menus
        with me.box(style=me.Style(display="flex", flex_direction="column", width="100%", max_width=500)):
            
            # --- SECTION MON COMPTE ---
            me.text("MON COMPTE", style=st.PAGE_SUBTITLE)
            
            render_menu_item(
                icon="person", 
                label="Profil", 
                on_click=on_profile_click,
                sub_label="Modifier vos informations personnelles"
            )
            
            render_menu_item(
                icon="lock", 
                label="Mot de passe", 
                on_click=on_password_click,
                sub_label="Réinitialiser votre mode de connexion"
            )
            
            # --- SECTION APPLICATIONS ---
            me.text("APPLICATIONS", style=st.PAGE_SUBTITLE)
            
            render_menu_item(
                icon="directions_run", 
                label="Strava", 
                on_click=on_strava_click,
                sub_label="Gérer la synchronisation"
            )

            # --- SECTION LÉGAL ---
            me.text("LÉGAL", style=st.PAGE_SUBTITLE)
            
            render_menu_item(
                icon="description", 
                label="CGU", 
                on_click=lambda e: setattr(s, "current_page", "cgu"),
                sub_label="Conditions Générales d'Utilisation"
            )