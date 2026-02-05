import mesop as me
import styles as st
from state import State 
import supabase_db as db
import re
import strava_utils as su
from config import STRAVA_REDIRECT_URI

# ==================================================
# 1. UTILITAIRES DE VALIDATION
# ==================================================

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Vérifie les critères de sécurité du mot de passe."""
    if not password:
        return False, "Veuillez saisir un mot de passe."
    if len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères."
    if not re.search(r"[A-Z]", password):
        return False, "Il faut au moins une majuscule."
    if not re.search(r"\d", password):
        return False, "Il faut au moins un chiffre."
    return True, ""

# ==================================================
# 2. GESTIONNAIRES D'ÉVÉNEMENTS (LOGIQUE)
# ==================================================

def on_email_blur(e: me.InputEvent):
    me.state(State).email = e.value

def on_password_blur(e: me.InputEvent):
    me.state(State).password = e.value

def on_password_confirm_blur(e: me.InputEvent):
    me.state(State).password_confirm = e.value

def toggle_password_visibility(e: me.ClickEvent):
    s = me.state(State)
    s.show_password_text = not s.show_password_text

def on_cgu_change(e: me.CheckboxChangeEvent):
    me.state(State).accept_cgu = e.checked

def toggle_auth_mode(e: me.ClickEvent):
    """Bascule entre Connexion et Inscription."""
    s = me.state(State)
    s.show_signup = not s.show_signup
    s.error_message = ""
    s.success_message = ""
    s.password = ""
    s.password_confirm = ""

def on_view_cgu(e: me.ClickEvent):
    """Redirige vers la page CGU et valide la consultation."""
    s = me.state(State)
    s.has_opened_cgu = True # Marqueur de consultation
    s.current_page = "cgu"

# --- ACTIONS DB ---

def on_forgot_password_click(e: me.ClickEvent):
    s = me.state(State)
    email = s.email.strip()
    if not email or "@" not in email:
        s.error_message = "Saisissez votre email pour la récupération."
        return
    s.is_loading = True
    success, message = db.reset_password(email)
    s.is_loading = False
    if success:
        s.success_message = "Lien de récupération envoyé par email !"
    else:
        s.error_message = message

def on_signup_click(e: me.ClickEvent):
    s = me.state(State)
    is_strong, strength_msg = validate_password_strength(s.password)
    
    if s.password != s.password_confirm:
        s.error_message = "Les mots de passe ne correspondent pas."
        return
    if not is_strong:
        s.error_message = strength_msg
        return
    if not s.accept_cgu:
        s.error_message = "Veuillez cocher l'acceptation des CGU."
        return
    if not getattr(s, "has_opened_cgu", False):
        s.error_message = "Veuillez consulter les CGU avant de valider."
        return
        
    s.is_loading = True
    result = db.signup_user(s.email, s.password)
    s.is_loading = False
    
    if result["error"]:
        s.error_message = f"Erreur : {result['error']}"
    else:
        s.success_message = "Compte créé ! Vérifiez vos emails."
        s.show_signup = False # Retour au login

def on_strava_connect_click(e: me.ClickEvent):
    """Lance le flux d'autorisation Strava."""
    # Génère l'URL d'autorisation avec ton client_id et redirect_uri
    url = su.get_strava_auth_url(STRAVA_REDIRECT_URI)
    # Redirige l'utilisateur vers Strava
    me.navigate(url)


# ==================================================
# 3. COMPOSANTS D'INTERFACE (UI)
# ==================================================

def render_password_hints(s: State):
    """Affiche les critères de sécurité sous les champs."""
    has_maj = bool(re.search(r"[A-Z]", s.password)) if s.password else False
    has_digit = bool(re.search(r"\d", s.password)) if s.password else False
    has_len = len(s.password) >= 6 if s.password else False
    
    with me.box(style=me.Style(margin=me.Margin(top=5, bottom=10), width="100%")):
        me.text("6 caractères, 1 Majuscule, 1 Chiffre",
            style=me.Style(
                font_size="0.7rem", 
                color=st.COLOR_PRIMARY if (has_maj and has_digit and has_len) else st.COLOR_TEXT, 
                opacity=0.7, 
                font_style="italic"
            )
        )

# --- ÉCRAN CONNEXION ---
def render_login(s: State, on_login):
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("CONNEXION", style=st.LOGIN_TITLE_STYLE)
        
        # Email
        me.input(label="Email", on_blur=on_email_blur, style=st.INPUT_STYLE)
        
        # Password
        with me.box(style=me.Style(width="100%", position="relative")):
            me.input(
                label="Mot de passe",
                type="text" if s.show_password_text else "password",
                on_blur=on_password_blur,
                style=st.INPUT_STYLE
            )
            with me.content_button(type="icon", on_click=toggle_password_visibility, 
                                   style=me.Style(position="absolute", right=4, top=12, z_index=10)):
                me.icon(icon="visibility" if not s.show_password_text else "visibility_off")
        
        # Forgot Password
        with me.box(on_click=on_forgot_password_click, style=me.Style(display="flex", justify_content="flex-end", cursor="pointer")):
            me.text("Mot de passe oublié ?", style=st.LINK_STYLE)
        
        # Button Login
        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", margin=me.Margin(top=20))):
            if s.is_loading:
                me.progress_spinner()
            else:
                me.button("ENTRER", type="flat", on_click=on_login, style=st.LOGIN_BUTTON_STYLE)
        
        # Switch to Signup
        with me.box(on_click=toggle_auth_mode, style=me.Style(margin=me.Margin(top=15), cursor="pointer", text_align="center")):
            me.text("Pas de compte ? Créer un profil", style=st.LINK_STYLE)
        
        # Feedbacks
        if s.error_message: me.text(s.error_message, style=st.ERROR_TEXT_STYLE)
        if s.success_message: me.text(s.success_message, style=st.SUCCESS_TEXT_STYLE)

# --- ÉCRAN INSCRIPTION ---
def render_signup(s: State):
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("CRÉATION DE COMPTE", style=st.LOGIN_TITLE_STYLE)
        
        me.input(label="Email", type="email", on_blur=on_email_blur, style=st.INPUT_STYLE)
        
        with me.box(style=me.Style(width="100%", position="relative")):
            me.input(label="Mot de passe", type="text" if s.show_password_text else "password", 
                     on_blur=on_password_blur, style=st.INPUT_STYLE)
            with me.content_button(type="icon", on_click=toggle_password_visibility, 
                                   style=me.Style(position="absolute", right=4, top=12, z_index=10)):
                me.icon(icon="visibility" if not s.show_password_text else "visibility_off")
        
        me.input(label="Confirmer le mot de passe", type="text" if s.show_password_text else "password", 
                 on_blur=on_password_confirm_blur, style=st.INPUT_STYLE)

        render_password_hints(s)
        
        # CGU Section
        with me.box(style=me.Style(margin=me.Margin(top=10), display="flex", align_items="center", gap=5, flex_wrap="wrap")):
            me.checkbox(label="", on_change=on_cgu_change)
            me.text("J'accepte les ", style=me.Style(font_size="0.8rem"))
            with me.box(on_click=on_view_cgu, style=me.Style(cursor="pointer")):
                me.text("CGU", style=me.Style(font_size="0.8rem", color=st.COLOR_ACCENT, text_decoration="underline", font_weight="bold"))
        
        # Button Signup
        with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", margin=me.Margin(top=20))):
            if s.is_loading:
                me.progress_spinner()
            else:
                me.button("S'INSCRIRE", type="flat", on_click=on_signup_click, style=st.LOGIN_BUTTON_STYLE)
        
        # Back to Login
        with me.box(on_click=toggle_auth_mode, style=me.Style(margin=me.Margin(top=15), cursor="pointer", text_align="center")):
            me.text("Déjà un compte ? Se connecter", style=st.LINK_STYLE)
            
        if s.error_message: me.text(s.error_message, style=st.ERROR_TEXT_STYLE)