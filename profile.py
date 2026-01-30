import mesop as me
import styles as st
from state import State
import supabase_db as db

def render_profile_setup(s: State):
    """Écran de configuration initiale du profil (Obligatoire)."""
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        me.text("CONFIGURER MON PROFIL", style=st.LOGIN_TITLE_STYLE)
        me.text("Certaines informations sont requises pour continuer.", 
                style=me.Style(font_size="0.85rem", margin=me.Margin(bottom=20), color="#666"))

        # --- CHAMPS OBLIGATOIRES ---
        me.input(label="Prénom*", value=s.prenom, on_blur=on_prenom_blur, style=st.INPUT_STYLE)
        me.input(label="Nom*", value=s.nom, on_blur=on_nom_blur, style=st.INPUT_STYLE)
        me.input(label="Date de naissance*", type="date", on_blur=on_date_n_blur, style=st.INPUT_STYLE)
        
        # --- CHAMPS OPTIONNELS ---
        with me.box(style=me.Style(display="flex", gap=10, width="100%")):
            me.input(label="Poids (kg)", type="number", on_blur=on_poids_blur, style=st.INPUT_STYLE)
            me.select(label="Sexe", options=[
                me.SelectOption(label="Homme", value="H"),
                me.SelectOption(label="Femme", value="F"),
                me.SelectOption(label="Autre", value="Autre")
            ], on_selection_change=on_sexe_change, style=me.Style(width="100%"))

        me.select(label="Niveau sportif", options=[
            me.SelectOption(label="Débutant", value="Débutant"),
            me.SelectOption(label="Intermédiaire", value="Intermédiaire"),
            me.SelectOption(label="Expert", value="Expert"),
            me.SelectOption(label="Compétiteur", value="Compétiteur")
        ], on_selection_change=on_niveau_change, style=me.Style(width="100%"))

        me.input(label="Sport préféré", on_blur=on_sport_pref_blur, style=st.INPUT_STYLE)

        # --- BOUTON DE VALIDATION ---
        with me.box(style=me.Style(margin=me.Margin(top=20), display="flex", flex_direction="column", align_items="center")):
            if s.is_loading:
                me.progress_spinner()
            else:
                me.button("ENREGISTRER ET CONTINUER", type="flat", on_click=on_save_profile_click, style=st.LOGIN_BUTTON_STYLE)

        if s.error_message:
            me.text(s.error_message, style=st.ERROR_TEXT_STYLE)

# --- GESTIONNAIRES D'ÉVÉNEMENTS ---

def on_prenom_blur(e: me.InputEvent):
    s = me.state(State)
    s.prenom = e.value

def on_nom_blur(e: me.InputEvent):
    s = me.state(State)
    s.nom = e.value

def on_date_n_blur(e: me.InputEvent):
    s = me.state(State)
    s.date_n = e.value

def on_poids_blur(e: me.InputEvent):
    s = me.state(State)
    try:
        s.poids = e.value
    except:
        pass

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
    
    # Validation des champs obligatoires [cite: 2026-01-22]
    if not s.prenom or not s.nom or not s.date_n:
        s.error_message = "Le prénom, le nom et la date de naissance sont obligatoires."
        return

    s.is_loading = True
    
    # Préparation des données pour Supabase [cite: 2026-01-22]
    profile_data = {
        "prenom": s.prenom,
        "nom": s.nom,
        "date_n": s.date_n,
        "poids": float(s.poids) if s.poids else None,
        "sexe": s.sexe,
        "niveau": s.niveau,
        "sport_pref": s.sport_pref
    }
    
    success, message = db.update_profile(s.user_id, profile_data)
    s.is_loading = False
    
    if success:
        s.error_message = ""
        # On force un rechargement vers le dashboard
        s.current_page = "dashboard"
        me.navigate("/")
    else:
        s.error_message = f"Erreur : {message}"