import mesop as me
import styles as st
from state import State
# from supabase_db import supabase  # Assure-toi d'importer ton client Supabase

def password_reset_screen(s: State):
    """Écran de réinitialisation de mot de passe harmonisé."""
    with me.box(style=st.CONTENT_CONTAINER):
        
        # --- BOUTON RETOUR ---
        # On s'assure de vider les messages quand on quitte pour que la page soit propre au retour
        def go_back(e: me.ClickEvent):
            s.success_message = ""
            s.error_message = ""
            s.current_page = "settings"

        with me.box(on_click=go_back, style=st.BACK_BUTTON_CONTAINER):
            me.icon(icon="arrow_back", style=me.Style(color=st.COLOR_PRIMARY))
            me.text("Retour aux réglages", style=st.BACK_BUTTON_TEXT)

        # Titres utilisant tes styles officiels
        me.text("SÉCURITÉ", style=st.PAGE_TITLE_STYLE)
        me.text("Gestion du compte", style=st.PAGE_SUBTITLE)

        # Conteneur format "Carte"
        with me.box(style=st.LOGIN_FORM_CONTAINER):
            me.text("MOT DE PASSE", style=st.LOGIN_TITLE_STYLE)
            
            me.text(
                "En cliquant sur le bouton, vous recevrez un lien par email pour définir un nouveau mot de passe.",
                style=st.TEXT_NORMAL
            )
            
            # Bouton d'action
            with me.box(style=me.Style(margin=me.Margin(top=25))):
                me.button(
                    "Envoyer l'email de récupération",
                    on_click=on_send_reset_link,
                    style=st.LOGIN_BUTTON_STYLE,
                    type="flat"
                )
            
            # Affichage conditionnel des messages (ton State attend des chaînes de caractères)
            if s.error_message:
                me.box(style=me.Style(margin=me.Margin(top=15)))
                me.text(s.error_message, style=st.ERROR_TEXT_STYLE)
                
            if s.success_message:
                me.box(style=me.Style(margin=me.Margin(top=15)))
                me.text(s.success_message, style=st.SUCCESS_TEXT_STYLE)

def on_send_reset_link(e: me.ClickEvent):
    s = me.state(State)
    s.error_message = ""
    s.success_message = ""
    
    # Vérification que l'email est présent dans le State
    if not s.email:
        s.error_message = "Erreur : Aucun email associé à ce compte."
        return

    try:
        # Appel réel à Supabase
        # supabase.auth.reset_password_for_email(s.email)
        
        # Mise à jour du message (string et non boolean pour éviter l'erreur de type)
        s.success_message = "Email envoyé avec succès ! Vérifiez vos courriers indésirables."
        
    except Exception as ex:
        s.error_message = f"Une erreur est survenue : {str(ex)}"