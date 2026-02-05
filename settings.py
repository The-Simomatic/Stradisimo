import mesop as me
import styles as st
from state import State
import urllib.parse
import os

# --- LOGIQUE STRAVA ---

def get_strava_auth_url():
    client_id = os.getenv("STRAVA_CLIENT_ID", "")
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:32123")
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read,activity:read_all",
        "approval_prompt": "auto"
    }
    return f"https://www.strava.com/oauth/authorize?{urllib.parse.urlencode(params)}"

def on_strava_connect_click(e: me.ClickEvent):
    me.navigate(get_strava_auth_url())

# --- NAVIGATION ---

def on_page_change(e: me.ClickEvent):
    s = me.state(State)
    s.current_page = e.key

def set_sub_menu(e: me.ClickEvent):
    """Définit quel sous-menu afficher."""
    s = me.state(State)
    # On s'assure que la variable existe dans State avant d'assigner
    s.active_sub_menu = e.key 

def reset_menu(e: me.ClickEvent):
    """Revient au menu précédent."""
    s = me.state(State)
    # Si on est dans l'import, on revient à Strava, sinon au menu principal
    if s.active_sub_menu == "import_history":
        s.active_sub_menu = "strava_main"
    else:
        s.active_sub_menu = ""

# --- COMPOSANTS ---

def render_back_button(label="Retour"):
    with me.box(on_click=reset_menu, style=st.BACK_BUTTON_CONTAINER):
        me.icon("arrow_back", style=me.Style(color=st.COLOR_PRIMARY, margin=me.Margin(right=8)))
        me.text(label, style=st.BACK_BUTTON_TEXT)

def render_menu_item(icon: str, label: str, key: str, on_click=on_page_change, sub_label: str = ""):
    with me.box(key=key, on_click=on_click, style=st.SETTINGS_CARD_STYLE):
        me.icon(icon=icon, style=me.Style(margin=me.Margin(right=16), color=st.COLOR_PRIMARY))
        with me.box(style=me.Style(flex_grow=1)):
            me.text(label, style=st.SETTINGS_CARD_TITLE)
            if sub_label:
                me.text(sub_label, style=st.SETTINGS_CARD_SUBTITLE)
        me.icon(icon="chevron_right", style=me.Style(color="rgba(229, 229, 229, 0.3)"))

# --- ÉCRAN PRINCIPAL ---

def settings_screen(s: State):
    # Boîte parente de l'écran entier
    with me.box(style=me.Style(width="100%", display="block")):
        
        # On récupère l'état du menu (valeur par défaut "" si absent)
        active_menu = getattr(s, "active_sub_menu", "")

        # --- CASE 1 : SOUS-MENU IMPORT ---
        if active_menu == "import_history":
            with me.box(key="menu_import", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("IMPORTATION HISTORIQUE", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    render_back_button("Retour à Strava")
                    me.box(style=me.Style(height=20))
                    me.text("Souhaitez-vous récupérer toutes vos activités passées ?", style=st.SETTINGS_CARD_SUBTITLE)
                    render_menu_item(
                        icon="history", 
                        label="Lancer l'importation complète", 
                        key="start_sync", 
                        sub_label="Cette opération peut prendre quelques minutes"
                    )

        # --- CASE 2 : SOUS-MENU STRAVA ---
        elif active_menu == "strava_main":
            with me.box(key="menu_strava", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("APPLICATIONS CONNECTÉES", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    render_back_button("Retour aux paramètres")
                    me.box(style=me.Style(height=20))
                    
                    is_linked = getattr(s, "is_strava_linked", False)
                    render_menu_item(
                        key="strava_auth",
                        icon="link",
                        label="Lier mon compte Strava" if not is_linked else "Compte Strava lié",
                        on_click=on_strava_connect_click,
                        sub_label="Autoriser la synchronisation"
                    )
                    
                    render_menu_item(
                        key="import_history",
                        icon="auto_awesome",
                        label="Importer toutes mes activités",
                        sub_label="Synchronisation de l'historique complet",
                        on_click=set_sub_menu
                    )

        # --- CASE 3 : MENU PRINCIPAL ---
        else:
            with me.box(key="menu_main", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("PARAMÈTRES", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    me.text("MON COMPTE", style=st.PAGE_SUBTITLE)
                    render_menu_item(key="profile_edit", icon="person", label="Profil")
                    
                    me.text("APPLICATIONS CONNECTÉES", style=st.PAGE_SUBTITLE)
                    render_menu_item(
                        key="strava_main", 
                        icon="settings_input_component", 
                        label="Strava", 
                        on_click=set_sub_menu,
                        sub_label="Gérer la connexion Strava"
                    )
                    
                    me.text("LÉGAL", style=st.PAGE_SUBTITLE)
                    render_menu_item(key="cgu", icon="description", label="CGU")