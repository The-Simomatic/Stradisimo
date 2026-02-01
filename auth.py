import mesop as me
import styles as st
from state import State 
import supabase_db as db
import re

# --- UTILITAIRES DE VALIDATION ---

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Vérifie : 6 caractères min, 1 majuscule, 1 chiffre."""
    if len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères."
    if not re.search(r"[A-Z]", password):
        return False, "Le mot de passe doit contenir au moins une majuscule."
    if not re.search(r"\d", password):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    return True, ""

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

def on_email_input(e: me.InputEvent):
    s = me.state(State)
    s.email = e.value

def on_password_input(e: me.InputEvent):
    s = me.state(State)
    s.password = e.value

def on_password_confirm_input(e: me.InputEvent):
    s = me.state(State)
    s.password_confirm = e.value

def toggle_password_visibility(e: me.ClickEvent):
    s = me.state(State)
    s.show_password_text = not s.show_password_text

def on_cgu_change(e: me.CheckboxChangeEvent):
    s = me.state(State)
    s.accept_cgu = e.checked

def on_forgot_password_click(e: me.ClickEvent):
    s = me.state(State)
    email_to_use = s.email.strip()
    if not email_to_use or "@" not in email_to_use:
        s.error_message = "Saisissez votre email ci-dessus pour la récupération."
        return
    s.is_loading = True
    success, message = db.reset_password(email_to_use)
    s.error_message = message
    s.is_loading = False

def on_update_password_click(e: me.ClickEvent):
    s = me.state(State)
    is_valid, error_msg = validate_password_strength(s.password)
    if not is_valid:
        s.error_message = error_msg
        return
    s.is_loading = True
    success, message = db.update_user_password(s.password)
    s.is_loading = False
    if success:
        s.error_message = "Succès ! Mot de passe modifié."
        me.navigate("/") 
    else:
        s.error_message = f"Erreur : {message}"

def toggle_auth_mode(e: me.ClickEvent):
    s = me.state(State)
    s.show_signup = not s.show_signup
    s.error_message = ""
    s.password = ""
    s.password_confirm = ""
    s.show_password_text = False

def on_signup_click(e: me.ClickEvent):
    s = me.state(State)
    is_strong, _ = validate_password_strength(s.password)
    if s.password != s.password_confirm or not is_strong or not s.accept_cgu:
        return
    s.is_loading = True
    result = db.signup_user(s.email, s.password)
    s.is_loading = False
    if result["error"]:
        s.error_message = f"Erreur : {result['error']}"
    else:
        s.error_message = "Compte créé ! Vérifiez vos emails."
        s.show_signup = False

def on_view_cgu(e: me.ClickEvent):
    s = me.state(State)
    s.current_page = "cgu"

# --- COMPOSANTS D'INTERFACE ---

def render_password_hints(s: State):
    has_maj = bool(re.search(r"[A-Z]", s.password))
    has_digit = bool(re.search(r"\d", s.password))
    has_len = len(s.password) >= 6
    is_all_ok = has_maj and has_digit and has_len
    text_color = st.COLOR_PRIMARY if is_all_ok else st.COLOR_TEXT
    with me.box(style=me.Style(margin=me.Margin(top=5, bottom=10), width="100%")):
        me.text("Critères : 6 caractères, 1 Majuscule, 1 Chiffre",
            style=me.Style(font_size="0.75rem", color=text_color, opacity=0.8, font_style="italic"))

def render_login(s: State, on_login):
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("CONNEXION", style=st.LOGIN_TITLE_STYLE)
        
        # Email avec style unifié
        with me.box(style=me.Style(width="100%", margin=me.Margin(bottom=10))):
            me.input(key="login_email", label="Email", on_input=on_email_input, style=st.INPUT_STYLE)
        
        # Mot de passe avec OEIL et style unifié
        with me.box(style=me.Style(width="100%", position="relative", margin=me.Margin(bottom=5))):
            me.input(
                label="Mot de passe",
                type="text" if s.show_password_text else "password",
                on_input=on_password_input,
                style=st.INPUT_STYLE
            )
            with me.content_button(type="icon", on_click=toggle_password_visibility, 
                                   style=me.Style(position="absolute", right=4, top=12, z_index=10)):
                me.icon(icon="visibility" if not s.show_password_text else "visibility_off")
        
        with me.box(on_click=on_forgot_password_click, style=me.Style(display="flex", justify_content="flex-end", width="100%", cursor="pointer")):
            me.text("Mot de passe oublié ?", style=st.LINK_STYLE)

        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", width="100%", margin=me.Margin(top=20))):
            if s.is_loading:
                me.progress_spinner()
            else:
                me.button("ENTRER", type="flat", on_click=on_login, style=st.LOGIN_BUTTON_STYLE)

        with me.box(on_click=toggle_auth_mode, style=me.Style(margin=me.Margin(top=15), cursor="pointer")):
            me.text("Pas de compte ? Créer un profil", style=st.LINK_STYLE)

        if s.error_message:
            is_success = "envoyé" in s.error_message.lower()
            me.text(s.error_message, style=st.SUCCESS_TEXT_STYLE if is_success else st.ERROR_TEXT_STYLE)

def render_signup(s: State):
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("CRÉATION DE COMPTE", style=st.LOGIN_TITLE_STYLE)
        
        # Email avec style unifié
        with me.box(style=me.Style(width="100%", margin=me.Margin(bottom=10))):
            me.input(key="signup_email", label="Email", type="email", on_input=on_email_input, style=st.INPUT_STYLE)
        
        # Mot de passe (1) avec style unifié
        with me.box(style=me.Style(width="100%", position="relative", margin=me.Margin(bottom=10))):
            me.input(
                label="Mot de passe",
                type="text" if s.show_password_text else "password",
                on_input=on_password_input,
                style=st.INPUT_STYLE
            )
            with me.content_button(type="icon", on_click=toggle_password_visibility, 
                                   style=me.Style(position="absolute", right=4, top=12, z_index=10)):
                me.icon(icon="visibility" if not s.show_password_text else "visibility_off")
        
        # Mot de passe (2) avec style unifié
        with me.box(style=me.Style(width="100%", position="relative", margin=me.Margin(bottom=5))):
            me.input(
                label="Confirmer le mot de passe",
                type="text" if s.show_password_text else "password",
                on_input=on_password_confirm_input,
                style=st.INPUT_STYLE
            )
            with me.content_button(type="icon", on_click=toggle_password_visibility, 
                                   style=me.Style(position="absolute", right=4, top=12, z_index=10)):
                me.icon(icon="visibility" if not s.show_password_text else "visibility_off")
        
        match = s.password == s.password_confirm
        if s.password_confirm and not match:
            me.text("Les mots de passe ne correspondent pas", 
                    style=me.Style(color="#ff5252", font_size="0.75rem", margin=me.Margin(top=5)))

        render_password_hints(s)

        # CGU
        with me.box(style=me.Style(margin=me.Margin(top=10), display="flex", align_items="center", gap=10)):
            me.checkbox(label="", on_change=on_cgu_change)
            me.text("J'accepte les ", style=me.Style(font_size="0.8rem", color=st.COLOR_TEXT))
            with me.box(on_click=on_view_cgu, style=me.Style(cursor="pointer")):
                me.text("CGU", style=me.Style(font_size="0.8rem", color=st.COLOR_PRIMARY, text_decoration="underline"))

        is_pwd_strong, _ = validate_password_strength(s.password)
        is_disabled = not s.accept_cgu or not match or not is_pwd_strong
        
        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", margin=me.Margin(top=20))):
            if s.is_loading:
                me.progress_spinner()
            else:
                me.button(
                    "S'INSCRIRE", 
                    type="flat", 
                    on_click=on_signup_click, 
                    disabled=is_disabled,
                    style=st.LOGIN_BUTTON_STYLE if not is_disabled else st.LOGIN_BUTTON_DISABLED_STYLE
                )

        with me.box(on_click=toggle_auth_mode, style=me.Style(margin=me.Margin(top=15), cursor="pointer")):
            me.text("Déjà un compte ? Se connecter", style=st.LINK_STYLE)

        if s.error_message:
            me.text(s.error_message, style=st.ERROR_TEXT_STYLE)

def render_password_reset(s: State):
    user_email = s.email
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("NOUVEAU MOT DE PASSE", style=st.LOGIN_TITLE_STYLE)
        if user_email:
             me.text(f"Réinitialisation pour : {user_email}", 
                   style=me.Style(font_size="0.85rem", color=st.COLOR_PRIMARY, margin=me.Margin(bottom=15)))
        
        # Nouveau MDP avec style unifié
        with me.box(style=me.Style(width="100%", position="relative", margin=me.Margin(bottom=5))):
            me.input(
                label="Nouveau mot de passe",
                type="text" if s.show_password_text else "password",
                on_input=on_password_input,
                style=st.INPUT_STYLE
            )
            with me.content_button(type="icon", on_click=toggle_password_visibility, 
                                   style=me.Style(position="absolute", right=4, top=12, z_index=10)):
                me.icon(icon="visibility" if not s.show_password_text else "visibility_off")
        
        render_password_hints(s)
        
        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", width="100%", margin=me.Margin(top=20))):
            if s.is_loading:
                me.progress_spinner()
            else:
                is_pwd_strong, _ = validate_password_strength(s.password)
                me.button(
                    "METTRE À JOUR", 
                    type="flat", 
                    on_click=on_update_password_click, 
                    disabled=not is_pwd_strong,
                    style=st.LOGIN_BUTTON_STYLE if is_pwd_strong else st.LOGIN_BUTTON_DISABLED_STYLE
                )
        
        with me.box(on_click=lambda e: me.navigate("/"), style=me.Style(margin=me.Margin(top=15), cursor="pointer")):
            me.text("Annuler", style=st.LINK_STYLE)

        if s.error_message:
            is_success = "succès" in s.error_message.lower()
            me.text(s.error_message, style=st.SUCCESS_TEXT_STYLE if is_success else st.ERROR_TEXT_STYLE)