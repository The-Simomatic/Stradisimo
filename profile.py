import mesop as me
import styles as st
from state import State
import supabase_db as db

def render_profile_setup(s: State):
    """Écran de configuration du profil (Initial ou Edition)."""
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        
        # --- BOUTON RETOUR (Lien Turquoise) ---
        if not s.is_completing_profile:
            with me.box(
                on_click=lambda e: setattr(s, "current_page", "settings"),
                style=st.BACK_BUTTON_CONTAINER  # Utilise le style centralisé
            ):
                me.icon(icon="arrow_back", style=me.Style(color=st.COLOR_PRIMARY))
                me.text("Retour aux réglages", style=st.BACK_BUTTON_TEXT)
        # Titre adaptatif
        titre = "CONFIGURER MON PROFIL" if s.is_completing_profile else "MODIFIER MON PROFIL"
        me.text(titre, style=st.LOGIN_TITLE_STYLE)
        
        if s.is_completing_profile:
            me.text("Certaines informations sont requises pour continuer.", 
                    style=me.Style(font_size="0.85rem", margin=me.Margin(bottom=20), color="#666"))

        # --- LE PIÈGE À NAVIGATEUR (HONEYPOT) ---
        with me.box(style=me.Style(display="none", height=0, width=0, overflow="hidden")):
            me.input(label="username")
            me.input(label="password", type="password")

        # --- CHAMPS OBLIGATOIRES ---
        me.input(
            label="Prénom*", 
            value=s.prenom, 
            on_blur=on_prenom_blur, 
            style=st.INPUT_STYLE,
            type="text" 
        )
        
        me.input(
            label="Nom*", 
            value=s.nom, 
            on_blur=on_nom_blur, 
            style=st.INPUT_STYLE,
            type="text"
        )
        
        me.input(
            label="Date de naissance*", 
            type="date", 
            value=s.date_n, 
            on_input=on_date_n_input, 
            style=st.INPUT_STYLE
        )
        
        # --- CHAMPS OPTIONNELS (Ligne Poids & Sexe avec Wrap) ---
        with me.box(style=me.Style(
            display="flex", 
            flex_direction="row", 
            flex_wrap="wrap", 
            gap=10, 
            width="100%",
            margin=me.Margin(bottom=10)
        )):
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.input(
                    label="Poids (kg)", 
                    type="number", 
                    value=s.poids, 
                    on_blur=on_poids_blur, 
                    style=me.Style(width="100%")
                )
            
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.select(
                    label="Sexe", 
                    value=s.sexe,
                    options=[
                        me.SelectOption(label="Homme", value="H"),
                        me.SelectOption(label="Femme", value="F"),
                        me.SelectOption(label="Autre", value="Autre")
                    ], 
                    on_selection_change=on_sexe_change, 
                    style=me.Style(width="100%")
                )

        me.select(
            label="Niveau sportif", 
            value=s.niveau,
            options=[
                me.SelectOption(label="Débutant", value="Débutant"),
                me.SelectOption(label="Intermédiaire", value="Intermédiaire"),
                me.SelectOption(label="Expert", value="Expert"),
                me.SelectOption(label="Compétiteur", value="Compétiteur")
            ], 
            on_selection_change=on_niveau_change, 
            style=me.Style(width="100%", margin=me.Margin(bottom=10))
        )

        me.input(
            label="Sport préféré", 
            value=s.sport_pref, 
            on_blur=on_sport_pref_blur, 
            style=st.INPUT_STYLE
        )

        # --- BOUTON DE VALIDATION ---
        with me.box(style=me.Style(margin=me.Margin(top=20), display="flex", flex_direction="column", align_items="center")):
            if s.is_loading:
                me.progress_spinner()
            else:
                label_btn = "ENREGISTRER ET CONTINUER" if s.is_completing_profile else "METTRE À JOUR"
                me.button(label_btn, type="flat", on_click=on_save_profile_click, style=st.LOGIN_BUTTON_STYLE)

        if s.error_message:
            me.text(s.error_message, style=st.ERROR_TEXT_STYLE)

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

def on_prenom_blur(e: me.InputEvent):
    s = me.state(State)
    s.prenom = e.value

def on_nom_blur(e: me.InputEvent):
    s = me.state(State)
    s.nom = e.value

def on_date_n_input(e: me.InputEvent):
    s = me.state(State)
    s.date_n = e.value

def on_poids_blur(e: me.InputEvent):
    s = me.state(State)
    s.poids = e.value

def on_sexe_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.sexe = e.value

def on_niveau_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.niveau = e.value

def on_sport_pref_blur(e: me.InputEvent):
    s = me.state(State)
    s.sport_pref = e.value

def on_save_profile_click(e: me.ClickEvent):
    s = me.state(State)
    
    if not s.prenom or not s.nom or not s.date_n:
        s.error_message = "Le prénom, le nom et la date de naissance sont obligatoires."
        return

    s.is_loading = True
    
    profile_data = {
        "prenom": s.prenom,
        "nom": s.nom,
        "date_n": s.date_n,
        "poids": float(s.poids) if s.poids and s.poids != "0" else None,
        "sexe": s.sexe,
        "niveau": s.niveau,
        "sport_pref": s.sport_pref
    }
    
    success, message = db.update_profile(s.user_id, profile_data)
    s.is_loading = False
    
    if success:
        s.error_message = ""
        if s.is_completing_profile:
            s.is_completing_profile = False
            s.current_page = "dashboard"
        else:
            s.current_page = "settings"
        me.navigate("/")
    else:
        s.error_message = f"Erreur : {message}"