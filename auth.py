import mesop as me
import styles as st
from state import State 
import supabase_db as db

# --- GESTIONNAIRES D'ÉVÉNEMENTS 

def on_email_blur(e: me.InputEvent):
    """Met à jour l'email dans le State global quand on quitte le champ."""
    s = me.state(State)
    s.email = e.value

def on_password_blur(e: me.InputEvent):
    """Met à jour le mot de passe dans le State global quand on quitte le champ."""
    s = me.state(State)
    s.password = e.value

def on_cgu_change(e: me.CheckboxChangeEvent):
    """Met à jour l'acceptation des CGU."""
    s = me.state(State)
    s.accept_cgu = e.checked

def on_forgot_password_click(e: me.ClickEvent):
    """Gère la réinitialisation du mot de passe."""
    s = me.state(State)
    if not s.email:
        s.error_message = "Veuillez saisir votre email pour réinitialiser le mot de passe."
        return
    
    s.is_loading = True
    success, message = db.reset_password(s.email)
    s.error_message = message
    s.is_loading = False

def toggle_auth_mode(e: me.ClickEvent):
    """Bascule entre Connexion et Inscription."""
    s = me.state(State)
    s.show_signup = not s.show_signup
    s.error_message = ""
    s.accept_cgu = False # Reset la case à cocher pour la sécurité

def on_signup_click(e: me.ClickEvent):
    """Gère la création de compte."""
    s = me.state(State)
    if not s.email or not s.password:
        s.error_message = "Veuillez remplir tous les champs."
        return
    
    if not s.accept_cgu:
        s.error_message = "Vous devez accepter les CGU pour vous inscrire."
        return

    s.is_loading = True
    result = db.signup_user(s.email, s.password)
    s.is_loading = False
    
    if result["error"]:
        s.error_message = f"Erreur : {result['error']}"
    else:
        s.error_message = "Compte créé ! Vérifiez vos emails pour confirmer."
        s.show_signup = False # Retour à la connexion après succès

def on_view_cgu(e: me.ClickEvent):
    """Navigue vers la page CGU."""
    s = me.state(State)
    s.current_page = "cgu"

# --- COMPOSANTS D'INTERFACE ---

def render_login(s: State, on_login):
    """Affiche le formulaire de connexion stylisé."""
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("CONNEXION", style=st.LOGIN_TITLE_STYLE)
        
        me.input(
            label="Email", 
            on_blur=on_email_blur, 
            style=st.INPUT_STYLE 
        )
        
        me.input(
            label="Mot de passe", 
            type="password", 
            on_blur=on_password_blur, 
            style=st.INPUT_STYLE 
        )
        
        with me.box(
            on_click=on_forgot_password_click,
            style=me.Style(
                display="flex", 
                justify_content="flex-end", 
                width="100%",
                cursor="pointer",
                opacity=0.5 if s.is_loading else 1.0 
            )
        ):
            me.text("Mot de passe oublié ?", style=st.LINK_STYLE)

        # Bouton ENTRER
        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", width="100%", margin=me.Margin(top=20))):
            if s.is_loading:
                me.progress_spinner()
            else:
                me.button("ENTRER", type="flat", on_click=on_login, style=st.LOGIN_BUTTON_STYLE)

        # Lien vers Inscription
        with me.box(on_click=toggle_auth_mode, style=me.Style(margin=me.Margin(top=15), cursor="pointer")):
            me.text("Pas de compte ? Créer un profil", style=st.LINK_STYLE)

        if s.error_message:
            is_success = "envoyé" in s.error_message.lower() or "succès" in s.error_message.lower()
            me.text(s.error_message, style=st.SUCCESS_TEXT_STYLE if is_success else st.ERROR_TEXT_STYLE)

        me.box(style=me.Style(height=1, width="100%", background="rgba(255,255,255,0.1)", margin=me.Margin(top=30, bottom=15)))

        # Lien informatif CGU
        with me.box(style=me.Style(text_align="center", width="100%")):
            me.text("En vous connectant, vous acceptez nos ", 
                    style=me.Style(color=st.COLOR_TEXT, font_size="0.7rem", opacity=0.6, display="inline"))
            with me.box(on_click=on_view_cgu, style=me.Style(display="inline", cursor="pointer")):
                me.text("CGU", style=me.Style(color=st.COLOR_PRIMARY, font_size="0.7rem", text_decoration="underline", display="inline"))

def render_signup(s: State):
    """Affiche le formulaire de création de compte."""
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("CRÉATION DE COMPTE", style=st.LOGIN_TITLE_STYLE)
        
        me.input(label="Email", type="email", on_blur=on_email_blur, style=st.INPUT_STYLE)
        me.input(label="Mot de passe", type="password", on_blur=on_password_blur, style=st.INPUT_STYLE)

        # Case à cocher CGU Obligatoire
        with me.box(style=me.Style(margin=me.Margin(top=15), display="flex", align_items="center", gap=10)):
            me.checkbox(label="", on_change=on_cgu_change)
            me.text("J'accepte les ", style=me.Style(font_size="0.8rem", color=st.COLOR_TEXT))
            with me.box(on_click=on_view_cgu, style=me.Style(cursor="pointer")):
                me.text("CGU", style=me.Style(font_size="0.8rem", color=st.COLOR_PRIMARY, text_decoration="underline"))

        # Bouton Créer
        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", margin=me.Margin(top=20))):
            if s.is_loading:
                me.progress_spinner()
            else:
                me.button(
                    "S'INSCRIRE", 
                    type="flat", 
                    on_click=on_signup_click, 
                    disabled=not s.accept_cgu,
                    style=st.LOGIN_BUTTON_STYLE if s.accept_cgu else st.LOGIN_BUTTON_DISABLED_STYLE
                )

        me.button("Déjà un compte ? Se connecter", on_click=toggle_auth_mode, style=st.LINK_STYLE)

        if s.error_message:
            me.text(s.error_message, style=st.ERROR_TEXT_STYLE)