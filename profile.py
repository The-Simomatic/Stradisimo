import mesop as me
import styles as st
from state import State
import supabase_db as db

def render_profile_setup(s: State):
    """Écran de configuration du profil (Initial ou Edition)."""

    # --- LOGIQUE DE PRÉ-REMPLISSAGE DE LA DATE ---
    # On ne remplit les variables de composants que si une date existe en DB 
    # et que l'utilisateur n'a pas encore touché aux sélecteurs (birth_year vide)
    if s.date_n and "-" in s.date_n and not getattr(s, "birth_year", ""):
        try:
            parts = s.date_n.split("-")
            s.birth_year = parts[0]
            s.birth_month = parts[1]
            s.birth_day = parts[2]
        except Exception:
            pass

    with me.box(style=st.LOGIN_FORM_CONTAINER):
        
        # --- SOLUTION ANTI-AUTOCOMPLÉTION ---
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
            me.text("Ces informations nous aident à personnaliser tes allures.", 
                    style=me.Style(font_size="0.85rem", margin=me.Margin(bottom=20), opacity=0.7, text_align="center"))

        # --- FORMULAIRE ---
        with me.box(style=me.Style(width="100%")):
            me.input(label="Prénom*", key="usr_firstname", value=s.prenom, on_blur=on_prenom_blur, style=st.INPUT_STYLE)
            me.input(label="Nom*", key="usr_lastname", value=s.nom, on_blur=on_nom_blur, style=st.INPUT_STYLE)
            
            # --- SÉLECTION DATE DE NAISSANCE ---
            me.text("Date de naissance*", style=me.Style(font_size="14px", margin=me.Margin(top=10, bottom=5), opacity=0.8))
            
            with me.box(style=me.Style(display="flex", flex_direction="row", gap=5, width="100%", margin=me.Margin(bottom=15))):
                # Jour
                with me.box(style=me.Style(width="32%")):
                    day_options = [me.SelectOption(label="JJ", value="")] + \
                                 [me.SelectOption(label=str(i), value=f"{i:02d}") for i in range(1, 32)]
                    me.select(label="Jour", 
                              value=getattr(s, "birth_day", ""),
                              options=day_options, 
                              on_selection_change=on_day_change, style=st.INPUT_STYLE)
                
                # Mois
                with me.box(style=me.Style(width="34%")):
                    month_names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
                    month_options = [me.SelectOption(label="Mois", value="")] + \
                                   [me.SelectOption(label=m, value=f"{i+1:02d}") for i, m in enumerate(month_names)]
                    me.select(label="Mois", 
                              value=getattr(s, "birth_month", ""),
                              options=month_options, 
                              on_selection_change=on_month_change, style=st.INPUT_STYLE)
                
                # Année
                with me.box(style=me.Style(width="32%")):
                    year_options = [me.SelectOption(label="AAAA", value="")] + \
                                  [me.SelectOption(label=str(i), value=str(i)) for i in range(2025, 1920, -1)]
                    me.select(label="Année", 
                              value=getattr(s, "birth_year", ""),
                              options=year_options, 
                              on_selection_change=on_year_change, style=st.INPUT_STYLE)
        
        # --- LIGNE POIDS / SEXE ---
        with me.box(style=me.Style(display="flex", flex_direction="row", flex_wrap="wrap", gap=10, width="100%")):
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.input(label="Poids (kg)", key="usr_weight", type="number", value=str(s.poids) if s.poids else "", on_blur=on_poids_blur, style=st.INPUT_STYLE)
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.select(
                    label="Sexe", 
                    value=s.sexe,
                    options=[
                        me.SelectOption(label="Sexe...", value=""),
                        me.SelectOption(label="Homme", value="H"),
                        me.SelectOption(label="Femme", value="F"),
                    ], 
                    on_selection_change=on_sexe_change, 
                    style=st.INPUT_STYLE
                )

        # --- LIGNE NIVEAU / VMA ---
        with me.box(style=me.Style(display="flex", flex_direction="row", flex_wrap="wrap", gap=10, width="100%")):
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.select(
                    label="Niveau", 
                    value=s.niveau,
                    options=[
                        me.SelectOption(label="Débutant", value="Débutant"),
                        me.SelectOption(label="Intermédiaire", value="Intermédiaire"),
                        me.SelectOption(label="Confirmé", value="Confirmé"),
                        me.SelectOption(label="Pro", value="Pro")
                    ], 
                    on_selection_change=on_niveau_change, 
                    style=st.INPUT_STYLE
                )
            with me.box(style=me.Style(flex_grow=1, min_width="140px")):
                me.input(label="VMA (km/h)", key="usr_vma", type="number", value=str(s.vma) if s.vma > 0 else "", on_blur=on_vma_blur, style=st.INPUT_STYLE)

        # Choix du Sport
        sport_options = ["Course à pied", "Vélo"]
        current_choice = s.sport_pref if s.sport_pref in sport_options else ("" if not s.sport_pref else "Autre")
        
        me.select(
            label="Sport principal*", 
            value=current_choice,
            options=[
                me.SelectOption(label="Choisir un sport...", value=""),
                me.SelectOption(label="Course à pied", value="Course à pied"),
                me.SelectOption(label="Vélo", value="Vélo"),
                me.SelectOption(label="Autre...", value="Autre")
            ], 
            on_selection_change=on_sport_main_change, 
            style=st.INPUT_STYLE
        )

        if current_choice == "Autre":
            me.input(label="Précisez votre sport*", key="usr_sport_custom", value=s.sport_pref if s.sport_pref != "Autre" else "", on_blur=on_sport_pref_blur, style=st.INPUT_STYLE)

        # Validation
        with me.box(style=me.Style(margin=me.Margin(top=20), display="flex", flex_direction="column", align_items="center")):
            if s.is_loading:
                me.progress_spinner()
            else:
                label_btn = "ENREGISTRER ET CONTINUER" if s.is_completing_profile else "METTRE À JOUR LE PROFIL"
                me.button(label_btn, type="flat", on_click=on_save_profile_click, style=st.LOGIN_BUTTON_STYLE)

        if s.error_message: me.text(s.error_message, style=st.ERROR_TEXT_STYLE)
        if s.success_message: me.text(s.success_message, style=st.SUCCESS_TEXT_STYLE)

# --- GESTIONNAIRES ---

def on_prenom_blur(e: me.InputBlurEvent): 
    me.state(State).prenom = e.value

def on_nom_blur(e: me.InputBlurEvent): 
    me.state(State).nom = e.value

def on_poids_blur(e: me.InputBlurEvent): 
    val = e.value.replace(",", ".")
    try:
        me.state(State).poids = float(val) if val else 0.0
    except:
        me.state(State).poids = 0.0

def on_sexe_change(e: me.SelectSelectionChangeEvent): 
    me.state(State).sexe = e.value

def on_niveau_change(e: me.SelectSelectionChangeEvent): 
    me.state(State).niveau = e.value

def on_vma_blur(e: me.InputBlurEvent):
    s = me.state(State)
    try:
        val = float(e.value.replace(",", ".")) if e.value.strip() else 0.0
        s.vma = round(max(0.0, min(30.0, val)), 1)
    except: pass

def on_sport_main_change(e: me.SelectSelectionChangeEvent):
    me.state(State).sport_pref = e.value

def on_sport_pref_blur(e: me.InputBlurEvent):
    me.state(State).sport_pref = e.value

# --- LOGIQUE DATE DE NAISSANCE ---

def update_date_n(s: State):
    # Reconstruit le format YYYY-MM-DD pour la base de données
    day = getattr(s, "birth_day", "01")
    month = getattr(s, "birth_month", "01")
    year = getattr(s, "birth_year", "2000")
    s.date_n = f"{year}-{month}-{day}"

def on_day_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.birth_day = e.value
    update_date_n(s)

def on_month_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.birth_month = e.value
    update_date_n(s)

def on_year_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.birth_year = e.value
    update_date_n(s)

# --- ACTION SAUVEGARDE ---

def on_save_profile_click(e: me.ClickEvent):
    s = me.state(State)
    if not s.prenom or not s.nom or not s.date_n or not s.sport_pref or s.sport_pref == "Autre":
        s.error_message = "Prénom, Nom, Date de naissance et Sport sont requis (*)."
        return
    
    s.is_loading = True
    s.error_message = ""
    
    profile_data = {
        "prenom": s.prenom, "nom": s.nom, "date_n": s.date_n,
        "poids": float(s.poids) if s.poids else 0.0, 
        "sexe": s.sexe, "niveau": s.niveau, 
        "sport_pref": s.sport_pref, "vma": float(s.vma)
    }
    
    success, message = db.update_profile(s.user_id, profile_data)
    s.is_loading = False
    
    if success:
        s.success_message = "Profil enregistré !"
        s.is_completing_profile = False
        s.current_page = "dashboard"
        me.navigate("/")
    else:
        s.error_message = f"Erreur : {message}"