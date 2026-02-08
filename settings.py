import mesop as me
import styles as st
from state import State
import urllib.parse
import os
import strava_utils as su
import supabase_db as db
import json

# --- LOGIQUE STRAVA ---

def get_strava_auth_url():
    client_id = os.getenv("STRAVA_CLIENT_ID", "")
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:32123")
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read,activity:read_all",
        "approval_prompt": "force"
    }
    return f"https://www.strava.com/oauth/authorize?{urllib.parse.urlencode(params)}"

def on_strava_connect_click(e: me.ClickEvent):
    me.navigate(get_strava_auth_url())

def on_start_full_import_click(e: me.ClickEvent):
    """Lance l'importation de tout l'historique."""
    s = me.state(State)
    s.is_loading = True
    
    # Appel de la fonction d'importation massive (peut prendre du temps)
    count = su.import_complete_history(s.user_id, s)
    
    # Rechargement immédiat des données pour l'affichage
    activities = db.get_latest_activities(s.user_id)
    s.recent_activities_json = json.dumps(activities)
    
    s.is_loading = False
    if count > 0:
        s.success_message = f"Succès ! {count} activités importées."
    else:
        s.success_message = "Import terminé (aucune nouvelle activité trouvée)."
        
    # Retour au menu Strava
    s.active_sub_menu = "strava_main"

def on_disconnect_strava(e: me.ClickEvent):
    """Supprime les accès Strava en base et réinitialise l'état."""
    s = me.state(State)
    
    # 1. Nettoyage en base de données
    data_to_clear = {
        "strava_access_token": None,
        "strava_refresh_token": None,
        "strava_expires_at": None,
        "strava_athlete_id": None
    }
    db.update_profile(s.user_id, data_to_clear)
    
    # 2. Mise à jour du State
    s.strava_access_token = ""
    s.strava_refresh_token = ""
    s.is_strava_linked = False
    s.success_message = "Compte Strava déconnecté avec succès."

# --- NAVIGATION ---

def on_page_change(e: me.ClickEvent):
    s = me.state(State)
    s.current_page = e.key

def set_sub_menu(e: me.ClickEvent):
    """Définit quel sous-menu afficher."""
    s = me.state(State)
    s.active_sub_menu = e.key 

def reset_menu(e: me.ClickEvent):
    """Revient au menu précédent."""
    s = me.state(State)
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
    """Affiche un élément de menu cliquable."""
    # Si on_click est None, on ne met pas d'action (utile pour l'affichage statique)
    click_handler = on_click if on_click else lambda e: None
    
    with me.box(key=key, on_click=click_handler, style=st.SETTINGS_CARD_STYLE):
        me.icon(icon=icon, style=me.Style(margin=me.Margin(right=16), color=st.COLOR_PRIMARY))
        with me.box(style=me.Style(flex_grow=1)):
            me.text(label, style=st.SETTINGS_CARD_TITLE)
            if sub_label:
                me.text(sub_label, style=st.SETTINGS_CARD_SUBTITLE)
        
        # Affiche la flèche seulement si c'est cliquable
        if on_click:
            me.icon(icon="chevron_right", style=me.Style(color="rgba(229, 229, 229, 0.3)"))

# --- ÉCRAN PRINCIPAL ---

def settings_screen(s: State):
    with me.box(style=me.Style(width="100%", display="block")):
        
        active_menu = getattr(s, "active_sub_menu", "")

        # --- CASE 1 : SOUS-MENU IMPORT ---
        if active_menu == "import_history":
            with me.box(key="menu_import", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("IMPORTATION HISTORIQUE", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    render_back_button("Retour à Strava")
                    me.box(style=me.Style(height=20))
                    
                    me.text("Souhaitez-vous récupérer toutes vos activités passées ?", style=st.SETTINGS_CARD_SUBTITLE)
                    
                    if s.is_loading:
                        with me.box(style=me.Style(padding=me.Padding.all(20), display="flex", flex_direction="column", align_items="center")):
                            me.progress_spinner()
                            me.text("Importation en cours... Veuillez patienter", style=me.Style(margin=me.Margin(top=10)))
                    else:
                        render_menu_item(
                            icon="download", 
                            label="Lancer l'importation complète", 
                            key="start_sync", 
                            on_click=on_start_full_import_click, # <-- Appel de la fonction ici
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
                    
                    if not is_linked:
                        # Option A : Le compte n'est pas lié -> On propose la connexion
                        render_menu_item(
                            key="strava_auth",
                            icon="link",
                            label="Lier mon compte Strava",
                            on_click=on_strava_connect_click,
                            sub_label="Autoriser la synchronisation de vos activités"
                        )
                    else:
                        # Option B : Le compte est déjà lié -> On affiche le statut et l'option de déconnexion
                        render_menu_item(
                            key="strava_linked_status",
                            icon="check_circle",
                            label="Compte Strava lié ✅",
                            on_click=None, # Statut seul, pas de clic
                            sub_label="Votre compte est synchronisé"
                        )

                        # Bouton pour DÉCONNECTER (Indispensable pour tes tests ou changer de compte)
                        render_menu_item(
                            key="strava_unauth",
                            icon="link_off",
                            label="Déconnecter Strava",
                            on_click=on_disconnect_strava, # Assure-toi d'avoir ajouté cette fonction (voir ci-dessous)
                            sub_label="Supprimer l'accès et réinitialiser la liaison"
                        )

                        me.box(style=me.Style(height=10))
                        
                        # Bouton Importer (visible seulement si lié)
                        render_menu_item(
                            key="import_history",
                            icon="auto_awesome",
                            label="Importer l'historique complet",
                            sub_label="Récupérer toutes vos anciennes activités",
                            on_click=set_sub_menu
                        )

        # --- CASE 3 : MENU PRINCIPAL ---
        else:
            with me.box(key="menu_main", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("PARAMÈTRES", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    
                    # Feedback utilisateur
                    if s.success_message:
                        me.text(s.success_message, style=st.SUCCESS_TEXT_STYLE)
                        # On vide le message après affichage pour éviter qu'il reste
                        s.success_message = ""

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