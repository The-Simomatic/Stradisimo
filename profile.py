import mesop as me
import styles as st
from state import State
import supabase_db as db

def render_profile_setup(s: State):
    """Écran de configuration du profil (Initial ou Edition)."""
    with me.box(style=st.LOGIN_FORM_CONTAINER):
        
        # --- SOLUTION ANTI-AUTOCOMPLÉTION (LEURRES) ---
        # Ces champs sont invisibles mais capturent l'autofill du navigateur
        with me.box(style=me.Style(display="none")):
            me.input(label="fake-email", type="email")
            me.input(label="fake-password", type="password")

        # --- BOUTON RETOUR ---
        if not s.is_completing_profile:
            with me.box(
                on_click=lambda e: setattr(s, "current_page", "settings"),
                style=st.BACK_BUTTON_CONTAINER
            ):
                me.icon(icon="arrow_back", style=me.Style(color=st.COLOR_PRIMARY))
                me.text("Retour aux réglages", style=st.BACK_BUTTON_TEXT)

        # Titre adaptatif
        titre = "CONFIGURER MON PROFIL" if s.is_completing_profile else "MODIFIER MON PROFIL"
        me.text(titre, style=st.LOGIN_TITLE_STYLE)
        
        if s.is_completing_profile:
            me.text("Certaines informations sont requises pour continuer.", 
                    style=me.Style(font_size="0.85rem", margin=me.Margin(bottom=20), color="#666"))

        # --- CHAMPS OBLIGATOIRES AVEC KEYS UNIQUES ---
        # L'ajout de '_field' dans la key brouille les pistes des gestionnaires de MDP
        me.input(
            label="Prénom*", 
            key="usr_firstname_field", 
            value=s.prenom, 
            on_input=on_prenom_input, # Passé en on_input pour plus de réactivité
            style=st.INPUT_STYLE
        )
        me.input(
            label="Nom*", 
            key="usr_lastname_field", 
            value=s.nom, 
            on_input=on_nom_input, 
            style=st.INPUT_STYLE
        )
        me.input(
            label="Date de naissance*", 
            key="usr_birth_field",
            type="date", 
            value=s.date_n, 
            on_input=on_date_n_input, 
            style=st.INPUT_STYLE
        )
        
        # --- LIGNE POIDS & SEXE ---
        with me.box(style=me.Style(display="flex", flex_direction="row", flex_wrap="wrap", gap=10, width="100%", margin=me.Margin(bottom=10))):
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.input(
                    label="Poids (kg)", 
                    key="usr_weight_field",
                    type="number", 
                    value=str(s.poids) if s.poids else "", 
                    on_input=on_poids_input, 
                    style=me.Style(width="100%")
                )
            
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.select(
                    label="Sexe", 
                    value=s.sexe,
                    options=[
                        me.SelectOption(label="Choisir...", value=""),
                        me.SelectOption(label="Homme", value="H"),
                        me.SelectOption(label="Femme", value="F"),
                        me.SelectOption(label="Autre", value="Autre")
                    ], 
                    on_selection_change=on_sexe_change, 
                    style=me.Style(width="100%")
                )

        # --- NIVEAU & VMA ---
        with me.box(style=me.Style(display="flex", flex_direction="row", flex_wrap="wrap", gap=10, width="100%", margin=me.Margin(bottom=10))):
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.select(
                    label="Niveau sportif", 
                    value=s.niveau,
                    options=[
                        me.SelectOption(label="Débutant", value="Débutant"),
                        me.SelectOption(label="Intermédiaire", value="Intermédiaire"),
                        me.SelectOption(label="Confirmé", value="Confirmé"),
                        me.SelectOption(label="Pro", value="Pro")
                    ], 
                    on_selection_change=on_niveau_change, 
                    style=me.Style(width="100%")
                )
            
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.input(
                    label="VMA (km/h)", 
                    key="usr_vma_field",
                    type="number", 
                    style=me.Style(width="100%"),
                    value=str(s.vma) if s.vma > 0 else "", 
                    on_input=on_vma_input, 
                )

        # --- CHOIX DU SPORT ---
        sport_options = ["Course à pied", "Vélo"]
        current_sport_choice = s.sport_pref if s.sport_pref in sport_options else ("" if not s.sport_pref else "Autre")
        
        me.select(
            label="Sport principal", 
            value=current_sport_choice,
            options=[
                me.SelectOption(label="Choisir un sport...", value=""),
                me.SelectOption(label="Course à pied", value="Course à pied"),
                me.SelectOption(label="Vélo", value="Vélo"),
                me.SelectOption(label="Autre...", value="Autre")
            ], 
            on_selection_change=on_sport_main_change, 
            style=me.Style(width="100%", margin=me.Margin(top=5))
        )

        if current_sport_choice == "Autre":
            me.input(
                label="Précisez votre sport", 
                key="usr_sport_custom_field",
                value="" if s.sport_pref == "Autre" else s.sport_pref, 
                on_input=on_sport_pref_input, 
                style=st.INPUT_STYLE,
                placeholder="Ex: Natation, Trail, Tennis..."
            )

        # --- BOUTON DE VALIDATION ---
        with me.box(style=me.Style(margin=me.Margin(top=25), display="flex", flex_direction="column", align_items="center")):
            if s.is_loading:
                me.progress_spinner()
            else:
                label_btn = "ENREGISTRER ET CONTINUER" if s.is_completing_profile else "METTRE À JOUR"
                me.button(label_btn, type="flat", on_click=on_save_profile_click, style=st.LOGIN_BUTTON_STYLE)

        if s.error_message:
            me.text(s.error_message, style=st.ERROR_TEXT_STYLE)

# --- GESTIONNAIRES D'ÉVÉNEMENTS (Optimisés en on_input) ---

def on_prenom_input(e: me.InputEvent):
    me.state(State).prenom = e.value

def on_nom_input(e: me.InputEvent):
    me.state(State).nom = e.value

def on_date_n_input(e: me.InputEvent):
    me.state(State).date_n = e.value

def on_poids_input(e: me.InputEvent):
    val = e.value.replace(",", ".")
    me.state(State).poids = val

def on_sexe_change(e: me.SelectSelectionChangeEvent):
    me.state(State).sexe = e.value

def on_niveau_change(e: me.SelectSelectionChangeEvent):
    me.state(State).niveau = e.value

def on_vma_input(e: me.InputEvent):
    s = me.state(State)
    try:
        if e.value.strip():
            val = float(e.value.replace(",", "."))
            s.vma = round(max(1.0, min(30.0, val)), 1)
        else:
            s.vma = 0.0
    except ValueError:
        pass

def on_sport_main_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.sport_pref = e.value

def on_sport_pref_input(e: me.InputEvent):
    if e.value.strip():
        me.state(State).sport_pref = e.value

def on_save_profile_click(e: me.ClickEvent):
    s = me.state(State)
    
    if not s.prenom or not s.nom or not s.date_n or not s.sport_pref:
        s.error_message = "Veuillez remplir les champs obligatoires (*) et le sport."
        return

    s.is_loading = True
    
    try:
        poids_final = float(str(s.poids).replace(",", ".")) if s.poids else None
    except:
        poids_final = None
        
    vma_final = round(float(s.vma), 1) if s.vma else None

    profile_data = {
        "prenom": s.prenom, 
        "nom": s.nom, 
        "date_n": s.date_n,
        "poids": poids_final,
        "sexe": s.sexe, 
        "niveau": s.niveau, 
        "sport_pref": s.sport_pref,
        "vma": vma_final
    }
    
    success, message = db.update_profile(s.user_id, profile_data)
    s.is_loading = False
    
    if success:
        s.error_message = ""
        s.is_completing_profile = False
        s.current_page = "dashboard"
        me.navigate("/")
    else:
        s.error_message = f"Erreur : {message}"