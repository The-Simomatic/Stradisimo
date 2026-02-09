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
    """Génère l'URL d'autorisation Strava avec les variables d'environnement."""
    client_id = os.getenv("STRAVA_CLIENT_ID", "").strip()
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:32123").strip()

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read,activity:read_all",
        "approval_prompt": "force"
    }
    return f"https://www.strava.com/oauth/authorize?{urllib.parse.urlencode(params)}"

def on_start_full_import_click(e: me.ClickEvent):
    """Lance l'importation par blocs pour éviter les timeouts Cloud Run."""
    s = me.state(State)
    
    # Sécurité : si l'import est déjà marqué comme fini totalement
    if s.strava_import_next_page == -1:
        s.success_message = "✅ Tout votre historique est déjà importé."
        yield
        return

    s.is_loading = True
    s.error_message = ""
    s.success_message = ""
    yield 

    try:
        # On appelle le générateur (limité à 5 pages par clic)
        import_generator = su.import_complete_history(s.user_id, s, max_pages=5)
        
        last_batch_count = 0
        for count in import_generator:
            last_batch_count = count
            # On rafraîchit l'UI à chaque page de 200 pour garder la connexion vivante
            yield 

        # --- GESTION DES MESSAGES DE FIN DE BLOC ---
        
        if s.strava_import_next_page == -1:
            # Cas 1 : Strava a renvoyé une liste vide, c'est vraiment fini
            s.success_message = f"✅ Importation terminée ! {last_batch_count} nouvelles activités récupérées."
        elif last_batch_count > 0:
            # Cas 2 : On a atteint la limite des 5 pages, il y a probablement une suite
            total_est = (s.strava_import_next_page - 1) * 200
            s.success_message = f"⚡ Bloc de 1000 activités traité (Total approx: {total_est}). Cliquez à nouveau pour importer la suite."
        else:
            # Cas 3 : Rien n'a été importé (déjà à jour)
            s.success_message = "Votre historique semble déjà à jour."

        # Mise à jour du dashboard pour montrer les activités fraîchement importées
        activities = db.get_latest_activities(s.user_id)
        s.recent_activities_json = json.dumps(activities)

    except Exception as ex:
        print(f"Erreur UI Import: {ex}")
        s.error_message = "La connexion a été instable. Vos données sont sauvegardées, cliquez à nouveau pour reprendre l'import."
    
    finally:
        # Le spinner s'arrête quoi qu'il arrive après le bloc de 5 pages
        s.is_loading = False
        yield

def on_disconnect_strava(e: me.ClickEvent):
    """Supprime les accès Strava en base et réinitialise l'état."""
    s = me.state(State)
    
    data_to_clear = {
        "strava_access_token": None,
        "strava_refresh_token": None,
        "strava_expires_at": None,
        "strava_athlete_id": None
    }
    db.update_profile(s.user_id, data_to_clear)
    
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
    click_handler = on_click if on_click else lambda e: None
    
    with me.box(key=key, on_click=click_handler, style=st.SETTINGS_CARD_STYLE):
        me.icon(icon=icon, style=me.Style(margin=me.Margin(right=16), color=st.COLOR_PRIMARY))
        with me.box(style=me.Style(flex_grow=1)):
            me.text(label, style=st.SETTINGS_CARD_TITLE)
            if sub_label:
                me.text(sub_label, style=st.SETTINGS_CARD_SUBTITLE)
        
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
                    
                    # 1. Gestion de l'affichage des erreurs
                    if s.error_message:
                        with me.box(style=me.Style(padding=me.Padding.all(12), background="#fff2f2", border=me.Border.all(me.BorderSide(width=1, color="#ff5252")), border_radius=8, margin=me.Margin(bottom=20))):
                            me.text(s.error_message, style=me.Style(color="#ff5252", font_size=13, font_weight="500"))

                    # 2. Affichage conditionnel (Chargement VS Formulaire)
                    if s.is_loading:
                        with me.box(style=me.Style(padding=me.Padding.all(40), display="flex", flex_direction="column", align_items="center")):
                            me.progress_spinner()
                            me.text("Synchronisation avec Strava en cours...", style=me.Style(margin=me.Margin(top=20), font_weight="500"))
                            me.text("Veuillez ne pas fermer cette page.", style=me.Style(font_size=12, opacity=0.7))
                    else:
                        # On n'affiche la question et le bouton QUE si on ne charge pas
                        me.text("Souhaitez-vous récupérer toutes vos activités passées ?", style=st.SETTINGS_CARD_SUBTITLE)
                        me.box(style=me.Style(height=10))
                        render_menu_item(
                            icon="download", 
                            label="Lancer l'importation complète", 
                            key="start_sync", 
                            on_click=on_start_full_import_click,
                            sub_label="Cela mettra à jour vos données existantes"
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
                        # On génère l'URL complète
                        auth_url = get_strava_auth_url()
                        
                        # On crée le bouton manuellement en HTML pour contourner le bug de navigation
                        with me.box(style=st.SETTINGS_CARD_STYLE):
                            me.icon(icon="link", style=me.Style(margin=me.Margin(right=16), color=st.COLOR_PRIMARY))
                            with me.box(style=me.Style(flex_grow=1)):
                                # Cette balise <a> est intouchable par le routeur Mesop
                                me.html(f"""
                                    <a href="{auth_url}" style="text-decoration: none; color: inherit; display: block; width: 100%;">
                                        <div style="font-family: Roboto, sans-serif;">
                                            <div style="font-size: 16px; font-weight: 500; color: white;">Lier mon compte Strava</div>
                                            <div style="font-size: 12px; color: rgba(255,255,255,0.6); margin-top: 4px;">Autoriser la synchronisation</div>
                                        </div>
                                    </a>
                                """)
                            me.icon(icon="open_in_new", style=me.Style(color="rgba(229, 229, 229, 0.3)"))
                    else:
                        # Le reste ne change pas
                        render_menu_item(
                            key="strava_linked_status",
                            icon="check_circle",
                            label="Compte Strava lié ✅",
                            on_click=None,
                            sub_label="Votre compte est synchronisé"
                        )
                        # ... (garde tes autres boutons déconnecter/importer ici)

                        render_menu_item(
                            key="strava_unauth",
                            icon="link_off",
                            label="Déconnecter Strava",
                            on_click=on_disconnect_strava,
                            sub_label="Supprimer la liaison avec ce compte"
                        )

                        me.box(style=me.Style(height=10))
                        
                        render_menu_item(
                            key="import_history",
                            icon="auto_awesome",
                            label="Importer l'historique complet",
                            sub_label="Récupérer vos anciennes activités",
                            on_click=set_sub_menu
                        )

        # --- CASE 3 : MENU PRINCIPAL ---
        else:
            with me.box(key="menu_main", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("PARAMÈTRES", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    
                    if s.success_message:
                        me.text(s.success_message, style=st.SUCCESS_TEXT_STYLE)
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