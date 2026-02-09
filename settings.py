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

def on_sync_recent_click(e: me.ClickEvent):
    """Synchronise uniquement les activités manquantes depuis la dernière date en DB."""
    s = me.state(State)
    print("🚀 [UI] Clic sur synchronisation rapide")
    s.is_loading = True
    s.success_message = ""
    s.error_message = ""
    yield

    try:
        # On appelle la fonction de synchro différentielle
        count = su.sync_recent_activities(s.user_id, s)
        
        if count > 0:
            s.success_message = f"✅ {count} nouvelles activités ajoutées !"
        else:
            s.success_message = "Votre compte est déjà à jour."
        
        # Rafraîchissement des données pour le dashboard
        activities = db.get_latest_activities(s.user_id)
        s.recent_activities_json = json.dumps(activities)
        print(f"✅ [UI] Synchro rapide terminée: {count} activités.")
    except Exception as ex:
        print(f"❌ [UI] Erreur synchro rapide: {ex}")
        s.error_message = "Erreur lors de la synchronisation des nouvelles activités."
    
    s.is_loading = False
    yield

def on_start_full_import_click(e: me.ClickEvent):
    """Lance l'importation par blocs pour éviter les timeouts Cloud Run."""
    s = me.state(State)
    print(f"🚀 [UI] Clic sur import complet (Page actuelle: {s.strava_import_next_page})")
    
    if s.strava_import_next_page == -1:
        s.success_message = "✅ Tout votre historique est déjà importé."
        yield
        return

    s.is_loading = True
    s.error_message = ""
    s.success_message = ""
    yield 

    try:
        import_generator = su.import_complete_history(s.user_id, s, max_pages=5)
        
        last_batch_count = 0
        for count in import_generator:
            last_batch_count = count
            yield 

        if s.strava_import_next_page == -1:
            s.success_message = f"✅ Importation terminée ! {last_batch_count} nouvelles activités récupérées."
        elif last_batch_count > 0:
            total_est = (s.strava_import_next_page - 1) * 200
            s.success_message = f"⚡ Bloc de {last_batch_count} activités traité (Total approx: {total_est}). Cliquez à nouveau pour importer la suite."
        else:
            s.success_message = "Votre historique semble déjà à jour."

        activities = db.get_latest_activities(s.user_id)
        s.recent_activities_json = json.dumps(activities)
        print("✅ [UI] Fin du bloc d'importation complet.")

    except Exception as ex:
        print(f"❌ [UI] Erreur Import Complet: {ex}")
        s.error_message = "La connexion a été interrompue. Vos données sont sauvegardées, cliquez à nouveau pour reprendre."
    
    finally:
        s.is_loading = False
        yield

def on_disconnect_strava(e: me.ClickEvent):
    """Supprime les accès Strava en base et réinitialise l'état."""
    s = me.state(State)
    print(f"🔌 [UI] Déconnexion Strava pour {s.user_id}")
    
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
    s.strava_import_next_page = 1 # On reset aussi la pagination
    s.success_message = "Votre compte Strava a été dissocié avec succès. Pour révoquer totalement l'accès, n'oubliez pas de supprimer l'autorisation directement dans vos paramètres Strava."

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
                me.text("IMPORTATION", style=st.PAGE_TITLE_STYLE)
                
                with me.box(style=me.Style(width="100%", max_width=500)):
                    render_back_button("Retour à Strava")
                    me.box(style=me.Style(height=20))
                    
                    # 1. Feedback Erreur
                    if s.error_message:
                        with me.box(style=me.Style(padding=me.Padding.all(12), background="#fff2f2", border=me.Border.all(me.BorderSide(width=1, color="#ff5252")), border_radius=8, margin=me.Margin(bottom=20))):
                            me.text(s.error_message, style=me.Style(color="#ff5252", font_size=13, font_weight="500"))

                    # 2. Feedback Succès
                    if s.success_message:
                        with me.box(style=me.Style(padding=me.Padding.all(12), background="#f2fff2", border=me.Border.all(me.BorderSide(width=1, color="#4caf50")), border_radius=8, margin=me.Margin(bottom=20))):
                            me.text(s.success_message, style=me.Style(color="#4caf50", font_size=13, font_weight="500"))

                    # 3. État de Chargement
                    if s.is_loading:
                        with me.box(style=me.Style(padding=me.Padding.all(40), display="flex", flex_direction="column", align_items="center")):
                            me.progress_spinner()
                            me.text("Synchronisation avec Strava en cours...", style=me.Style(margin=me.Margin(top=20), font_weight="500"))
                            me.text("Veuillez patienter quelques instants.", style=me.Style(font_size=12, opacity=0.7))
                    else:
                        # --- BOUTONS D'ACTION ---

                        # BOUTON 1 : SYNCHRO RÉCENTE (Les manquantes)
                        render_menu_item(
                            icon="sync", 
                            label="Synchroniser les manquantes", 
                            key="sync_recent", 
                            on_click=on_sync_recent_click,
                            sub_label="Récupérer les activités depuis la dernière synchro"
                        )
                        
                        me.box(style=me.Style(height=15))
                        
                        # BOUTON 2 : IMPORT COMPLET (Dynamique par numéros d'activités)
                        if s.strava_import_next_page != -1:
                            if s.strava_import_next_page == 1:
                                import_label = "Lancer l'importation complète"
                                import_sub = "Récupérer tout l'historique Strava"
                            else:
                                # Calcul des numéros : ex Page 6 (start=1001) à Page 10 (end=2000)
                                start_num = ((s.strava_import_next_page - 1) * 200) + 1
                                end_num = start_num + 999 
                                import_label = f"Importer activités {start_num} à {end_num}"
                                import_sub = "Continuer la récupération de votre historique"

                            render_menu_item(
                                icon="download", 
                                label=import_label, 
                                key="start_sync", 
                                on_click=on_start_full_import_click,
                                sub_label=import_sub
                            )
                        else:
                            # État : Historique terminé
                            with me.box(style=me.Style(padding=me.Padding.all(16), display="flex", justify_content="center", align_items="center")):
                                me.icon("verified", style=me.Style(color="#4caf50", margin=me.Margin(right=8)))
                                me.text("Historique complet déjà importé.", style=me.Style(color="#4caf50", font_weight="500"))

        # --- CASE 2 : SOUS-MENU STRAVA ---
        elif active_menu == "strava_main":
            with me.box(key="menu_strava", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("APPLICATIONS CONNECTÉES", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    render_back_button("Retour aux paramètres")
                    me.box(style=me.Style(height=20))
                    
                    is_linked = getattr(s, "is_strava_linked", False)
                    
                    if not is_linked:
                        # --- ÉTAT : NON CONNECTÉ ---
                        auth_url = get_strava_auth_url()
                        with me.box(style=st.SETTINGS_CARD_STYLE):
                            me.icon(icon="link", style=me.Style(margin=me.Margin(right=16), color=st.COLOR_PRIMARY))
                            with me.box(style=me.Style(flex_grow=1)):
                                me.html(f"""
                                    <a href="{auth_url}" style="text-decoration: none; color: inherit; display: block; width: 100%;">
                                        <div style="font-family: Roboto, sans-serif;">
                                            <div style="font-size: 16px; font-weight: 500; color: white;">Connecter Strava</div>
                                            <div style="font-size: 12px; color: rgba(255,255,255,0.6); margin-top: 4px;">Synchronisez vos activités automatiquement</div>
                                        </div>
                                    </a>
                                """)
                            me.icon(icon="open_in_new", style=me.Style(color="rgba(229, 229, 229, 0.3)"))
                    else:
                        # --- ÉTAT : DÉJÀ CONNECTÉ (L'indicateur ✅) ---
                        with me.box(style=st.SETTINGS_CARD_STYLE):
                            me.icon(icon="check_circle", style=me.Style(margin=me.Margin(right=16), color="#4caf50"))
                            with me.box(style=me.Style(flex_grow=1)):
                                me.text("Strava est connecté", style=me.Style(color="#4caf50", font_weight="500"))
                                me.text("Compte lié avec succès", style=st.SETTINGS_CARD_SUBTITLE)
                        
                        me.box(style=me.Style(height=10))

                        # Bouton pour aller vers l'import (Historique / Manquantes)
                        render_menu_item(
                            key="import_history",
                            icon="sync_alt",
                            label="Synchroniser mes activités",
                            sub_label="Historique complet ou nouveautés",
                            on_click=set_sub_menu
                        )
                        
                        me.box(style=me.Style(height=10))

                        # Bouton Déconnexion
                        render_menu_item(
                            key="strava_unauth",
                            icon="link_off",
                            label="Déconnecter Strava",
                            on_click=on_disconnect_strava,
                            sub_label="Supprimer la liaison avec ce compte"
                        )
        # --- CASE 3 : MENU PRINCIPAL ---
        else:
            with me.box(key="menu_main", style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center")):
                me.text("PARAMÈTRES", style=st.PAGE_TITLE_STYLE)
                with me.box(style=me.Style(width="100%", max_width=500)):
                    
                    if s.success_message:
                        me.text(s.success_message, style=st.SUCCESS_TEXT_STYLE)

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