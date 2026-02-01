import mesop as me
import styles as st
from state import State
import supabase_db as db

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

def on_password_blur(e: me.InputEvent):
    s = me.state(State)
    s.password = e.value

def on_confirm_blur(e: me.InputEvent):
    s = me.state(State)
    s.password_confirm = e.value

def toggle_visibility(e: me.ClickEvent):
    s = me.state(State)
    s.show_password_text = not s.show_password_text

def on_submit(e: me.ClickEvent):
    """Fonction déclenchée par le bouton METTRE À JOUR."""
    s = me.state(State)
    
    # Validation minimale
    if not s.password:
        s.error_message = "Le mot de passe ne peut pas être vide."
        return

    if s.password != s.password_confirm:
        s.error_message = "Les mots de passe ne correspondent pas."
        return

    s.is_loading = True
    s.error_message = ""
    
    # Appel à la DB
    success, message = db.update_user_password(s.password)
    s.is_loading = False
    
    if success:
        s.error_message = "Succès ! Mot de passe mis à jour."
        s.password = ""
        s.password_confirm = ""
        # On redirige vers le dashboard après un court délai ou directement
        s.current_page = "dashboard"
        me.navigate("/")
    else:
        s.error_message = f"Erreur : {message}"

# --- COMPOSANT D'INTERFACE ---

def password_reset_screen(s: State):
    """Écran de saisie du nouveau mot de passe avec Header et Formulaire."""
    with me.box(style=st.CONTENT_CONTAINER):
        
        # --- TON HEADER PERSONNALISÉ ---
        me.text("SÉCURITÉ", style=st.PAGE_TITLE_STYLE)
        me.text("Réinitialisation de votre accès", style=st.PAGE_SUBTITLE)

        # Conteneur du formulaire (centré)
        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", width="100%")):
            
            with me.box(style=st.LOGIN_FORM_CONTAINER):
                me.text("MODIFIER LE MOT DE PASSE", style=st.LOGIN_TITLE_STYLE)
                
                # Champ 1 : Nouveau mot de passe
                with me.box(style=me.Style(width="100%", position="relative", margin=me.Margin(bottom=10))):
                    me.input(
                        key="new_pwd",
                        label="Nouveau mot de passe",
                        type="text" if s.show_password_text else "password",
                        on_blur=on_password_blur,
                        style=st.INPUT_STYLE
                    )
                    with me.content_button(type="icon", on_click=toggle_visibility, 
                                           style=me.Style(position="absolute", right=4, top=12, z_index=10)):
                        me.icon(icon="visibility" if not s.show_password_text else "visibility_off")

                # Champ 2 : Confirmation
                with me.box(style=me.Style(width="100%", position="relative", margin=me.Margin(bottom=10))):
                    me.input(
                        key="conf_pwd",
                        label="Confirmez le mot de passe",
                        type="text" if s.show_password_text else "password",
                        on_blur=on_confirm_blur,
                        style=st.INPUT_STYLE
                    )

                # Instructions de sécurité
                with me.box(style=me.Style(margin=me.Margin(top=5, bottom=15))):
                    me.text("6 caractères min, 1 Majuscule, 1 Chiffre", 
                            style=me.Style(font_size="0.75rem", opacity=0.6, font_style="italic", color=st.COLOR_TEXT))

                # Bouton de validation
                with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", margin=me.Margin(top=20))):
                    if s.is_loading:
                        me.progress_spinner()
                    else:
                        me.button(
                            "METTRE À JOUR",
                            on_click=on_submit,
                            style=st.LOGIN_BUTTON_STYLE,
                            type="flat"
                        )

                # Message d'erreur ou de succès
                if s.error_message:
                    is_success = "succès" in s.error_message.lower() or "mis à jour" in s.error_message.lower()
                    me.text(s.error_message, 
                            style=st.SUCCESS_TEXT_STYLE if is_success else st.ERROR_TEXT_STYLE)