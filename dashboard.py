import mesop as me
import styles as st
from state import State

# --- ACTIONS ---

def on_vma_slider_change(e: me.SliderValueChangeEvent):
    s = me.state(State)
    s.vma = float(e.value)

def on_vma_increment(e: me.ClickEvent):
    s = me.state(State)
    if s.vma < 22:
        s.vma = round(s.vma + 0.5, 1)

def on_vma_decrement(e: me.ClickEvent):
    s = me.state(State)
    if s.vma > 8:
        s.vma = round(s.vma - 0.5, 1)

def on_generate_workout(e: me.ClickEvent):
    # Logique future pour l'IA ou les séances
    pass

# --- FONCTIONS UTILITAIRES ET COMPOSANTS ---

def calculate_pace(vma: float, percent: float) -> str:
    """Calcule l'allure en mm:ss au km"""
    if vma <= 0: return "00:00"
    speed = vma * percent
    pace_float = 60 / speed
    minutes = int(pace_float)
    seconds = int((pace_float - minutes) * 60)
    return f"{minutes}:{seconds:02d}"

def render_vma_button(icon: str, on_click):
    """Bouton icône personnalisé car me.icon_button n'existe pas."""
    with me.content_button(type="icon", on_click=on_click):
        me.icon(icon=icon, style=me.Style(color=st.COLOR_PRIMARY))

def render_pace_card(label: str, pace: str):
    """Card agrandie pour les allures"""
    with me.box(style=me.Style(
        background="rgba(40, 165, 168, 0.1)",
        padding=me.Padding.symmetric(vertical=15, horizontal=5), # Plus de hauteur
        border_radius=15,
        width="31%", # Un peu plus large
        min_width="110px",
        text_align="center",
        border=me.Border.all(me.BorderSide(width=1, color="rgba(40, 165, 168, 0.2)"))
    )):
        me.text(label, style=me.Style(font_size="0.65rem", color=st.COLOR_PRIMARY, font_weight="700"))
        me.text(pace, style=me.Style(font_size="1.3rem", color=st.COLOR_TEXT, font_weight="900", margin=me.Margin(top=5)))

def render_dashboard_subtitle(title: str):
    me.text(title, style=me.Style(
        color=st.COLOR_PRIMARY,
        font_family="Inter, sans-serif",
        font_size="1.1rem",
        font_weight="600",
        text_align="left",
        width="100%",
        margin=me.Margin(top=30, bottom=15)
    ))

def render_metric_card(label: str, value: str, icon_name: str):
    # --- LOGIQUE DYNAMIQUE DE TAILLE ---
    # On définit une taille de base (1.3rem ou 1.4rem selon tes préférences)
    size = "1.3rem" 
    val_str = str(value).upper()
    
    # Ajustement selon la longueur du texte
    if len(val_str) > 10:
        size = "0.95rem"  # Très réduit pour les mots comme "INTERMÉDIAIRE"
    elif len(val_str) > 8:
        size = "1.1rem"   # Réduction modérée

    with me.box(style=st.METRIC_CARD_STYLE):
        # En-tête : Libellé + Icône
        with me.box(style=me.Style(display="flex", justify_content="space-between", align_items="center")):
            me.text(label, style=st.CARD_LABEL_STYLE)
            me.icon(icon_name, style=me.Style(color=st.COLOR_PRIMARY, font_size=18))
        
        # Valeur avec style injecté dynamiquement
        me.text(
            val_str, 
            style=me.Style(
                color=st.COLOR_TEXT,
                font_size=size, # <-- C'est ici que la magie opère
                font_weight="800",
                white_space="nowrap",
                overflow="hidden",
                text_overflow="ellipsis" # Sécurité : ajoute "..." si vraiment ça ne loge pas
            )
        )

# --- ÉCRAN PRINCIPAL ---

def dashboard_screen(s: State):
    with me.box(style=st.CONTENT_CONTAINER):
        
        # --- TITRE BIENVENUE ---
        me.text(f"BIENVENUE, {s.prenom.upper() if s.prenom else 'ATHLÈTE'}", 
                style=st.PAGE_TITLE_STYLE)

        # --- SECTION : DONNÉES PERSONNELLES ---
        render_dashboard_subtitle("DONNÉES PERSONNELLES")
        with me.box(style=st.CARDS_CONTAINER_STYLE):
            render_metric_card("SPORT PRÉFÉRÉ", s.sport_pref or "NON DÉFINI", "fitness_center")
            render_metric_card("NIVEAU", s.niveau or "DÉBUTANT", "speed")
            render_metric_card("NAISSANCE", s.date_n or "--/--/----", "event")
            render_metric_card("POIDS", f"{s.poids} KG" if s.poids else "N/A", "monitor_weight")

        # --- SECTION : DERNIÈRES ACTIVITÉS STRAVA ---
        render_dashboard_subtitle("TES DERNIÈRES ACTIVITÉS")
        with me.box(style=st.SETTINGS_CARD_STYLE):
            with me.box(style=me.Style(display="flex", flex_direction="column", width="100%", align_items="center", padding=me.Padding.all(15))):
                me.text("CONNECTEZ STRAVA POUR VISUALISER VOS ACTIVITÉS", 
                        style=st.SETTINGS_CARD_SUBTITLE)
                me.text("Lien Strava en attente", style=st.LINK_STYLE)

        # --- SECTION : RAPPEL DES ALLURES ---
        render_dashboard_subtitle("RAPPEL DES ALLURES")
        with me.box(style=st.SETTINGS_CARD_STYLE):
            with me.box(style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center", padding=me.Padding.all(10))):
                
                vma_val = s.vma if s.vma and s.vma > 0 else 15.0
                
                # 1. SÉLECTION AFFINÉE (Plus petite)
                with me.box(style=me.Style(display="flex", align_items="center", gap=15, margin=me.Margin(bottom=2))):
                    render_vma_button("remove_circle_outline", on_vma_decrement)
                    
                    # Taille réduite à 24px
                    me.text(f"{vma_val:.1f} km/h", style=me.Style(font_size=24, font_weight="bold", color=st.COLOR_PRIMARY))
                    
                    render_vma_button("add_circle_outline", on_vma_increment)

                me.text("RÉGLAGE VMA", style=me.Style(font_size=10, color="#aaa", margin=me.Margin(bottom=10)))
                
                # SLIDER PLUS DISCRET
                with me.box(style=me.Style(width="80%", max_width=350)): # Réduit à 80% de large
                    me.slider(
                        min=8, max=22, step=0.5, value=vma_val,
                        on_value_change=on_vma_slider_change,
                        style=me.Style(width="100%") 
                    )

                me.box(style=me.Style(height=25)) # Espace avant les résultats

                # 2. CARDS ALLURES (Plus grandes)
                with me.box(style=me.Style(
                    display="flex", 
                    flex_wrap="wrap", 
                    gap=8, 
                    width="100%", 
                    justify_content="center"
                )):
                    render_pace_card("ENDURANCE (65%)", calculate_pace(vma_val, 0.65))
                    render_pace_card("SEUIL (85%)", calculate_pace(vma_val, 0.85))
                    render_pace_card("VMA (100%)", calculate_pace(vma_val, 1.0))

        # --- SECTION : RENFORCEMENT ---
        render_dashboard_subtitle("RENFORCEMENT")
        with me.box(style=me.Style(width="100%", display="flex", justify_content="center", margin=me.Margin(top=10))):
            me.button("GÉNÉRER UNE SÉANCE", on_click=on_generate_workout, type="flat", style=st.LOGIN_BUTTON_STYLE)