import mesop as me
import styles as st
from state import State
from datetime import datetime

# ==================================================
# 1. ACTIONS & LOGIQUE
# ==================================================

def on_vma_slider_change(e: me.SliderValueChangeEvent):
    s = me.state(State)
    s.vma = float(e.value)

def on_vma_increment(e: me.ClickEvent):
    s = me.state(State)
    if s.vma < 24: # Augmenté à 24 pour les athlètes de haut niveau
        s.vma = round(s.vma + 0.1, 1) # Incrément plus précis

def on_vma_decrement(e: me.ClickEvent):
    s = me.state(State)
    if s.vma > 8:
        s.vma = round(s.vma - 0.1, 1)

def on_generate_workout(e: me.ClickEvent):
    # Logique future pour l'IA
    pass

# ==================================================
# 2. UTILITAIRES DE CALCUL
# ==================================================

def calculate_pace(vma: float, percent: float) -> str:
    """Calcule l'allure en mm:ss au km."""
    if vma <= 0: return "00:00"
    speed = vma * percent
    pace_float = 60 / speed
    minutes = int(pace_float)
    seconds = int((pace_float - minutes) * 60)
    return f"{minutes}:{seconds:02d}"

def calculate_age(birth_date_str: str) -> str:
    """Calcule l'âge dynamiquement."""
    if not birth_date_str or len(birth_date_str) < 10:
        return "N/A"
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return f"{age} ANS"
    except:
        return "N/A"

# ==================================================
# 3. COMPOSANTS UI RÉUTILISABLES
# ==================================================

def render_metric_card(label: str, value: str, icon_name: str):
    """Card pour les données personnelles avec texte auto-adaptatif."""
    val_str = str(value).upper()
    size = "1.3rem"
    if len(val_str) > 10: size = "0.9rem"
    elif len(val_str) > 8: size = "1.1rem"

    with me.box(style=st.METRIC_CARD_STYLE):
        with me.box(style=me.Style(display="flex", justify_content="space-between")):
            me.text(label, style=st.CARD_LABEL_STYLE)
            me.icon(icon_name, style=me.Style(color=st.COLOR_PRIMARY, font_size=18))
        
        me.text(val_str, style=me.Style(
            color=st.COLOR_TEXT, font_size=size, font_weight="800",
            white_space="nowrap", overflow="hidden", text_overflow="ellipsis"
        ))

def render_pace_card(label: str, pace: str):
    """Affiche une zone d'intensité."""
    with me.box(style=me.Style(
        background="rgba(40, 165, 168, 0.08)",
        padding=me.Padding.symmetric(vertical=15, horizontal=5),
        border_radius=12,
        width="31%", min_width="100px", text_align="center",
        border=me.Border.all(me.BorderSide(width=1, color="rgba(40, 165, 168, 0.2)"))
    )):
        me.text(label, style=me.Style(font_size="0.6rem", color=st.COLOR_PRIMARY, font_weight="700", letter_spacing="0.5px"))
        me.text(pace, style=me.Style(font_size="1.4rem", color=st.COLOR_TEXT, font_weight="900"))

# ==================================================
# 4. ÉCRAN PRINCIPAL
# ==================================================

def dashboard_screen(s: State):
    with me.box(style=st.CONTENT_CONTAINER):
        
        # Header Bienvenue
        me.text(f"HELLO, {s.prenom.upper() if s.prenom else 'ATHLÈTE'} 👋", style=st.PAGE_TITLE_STYLE)

        # --- SECTION : PROFIL ---
        me.text("MON PROFIL PHYSIOLOGIQUE", style=st.PAGE_SUBTITLE_STYLE)
        with me.box(style=st.CARDS_CONTAINER_STYLE):
            render_metric_card("SPORT", s.sport_pref or "NON DÉFINI", "fitness_center")
            render_metric_card("NIVEAU", s.niveau or "DÉBUTANT", "trending_up")
            render_metric_card("ÂGE", calculate_age(s.date_n), "cake")
            render_metric_card("POIDS", f"{s.poids} KG" if s.poids else "N/A", "monitor_weight")

        # --- SECTION : ALLURES ---
        me.text("MES ZONES D'INTENSITÉ", style=st.PAGE_SUBTITLE_STYLE)
        with me.box(style=st.SETTINGS_CARD_STYLE):
            with me.box(style=me.Style(width="100%", display="flex", flex_direction="column", align_items="center", padding=me.Padding.all(15))):
                
                vma_val = s.vma if s.vma > 0 else 15.0
                
                # Contrôle VMA
                with me.box(style=me.Style(display="flex", align_items="center", gap=20)):
                    with me.content_button(type="icon", on_click=on_vma_decrement):
                        me.icon("remove_circle_outline", style=me.Style(color=st.COLOR_PRIMARY))
                    
                    me.text(f"{vma_val:.1f}", style=me.Style(font_size=32, font_weight="900", color=st.COLOR_PRIMARY))
                    
                    with me.content_button(type="icon", on_click=on_vma_increment):
                        me.icon("add_circle_outline", style=me.Style(color=st.COLOR_PRIMARY))

                me.text("VMA (KM/H)", style=me.Style(font_size=10, opacity=0.5, letter_spacing="1px"))
                
                # Slider
                with me.box(style=me.Style(width="90%", max_width=400, margin=me.Margin(top=10))):
                    me.slider(min=8, max=24, step=0.1, value=vma_val, on_value_change=on_vma_slider_change)

                me.box(style=me.Style(height=20))

                # Cards Allures
                with me.box(style=me.Style(display="flex", flex_wrap="wrap", gap=8, width="100%", justify_content="center")):
                    render_pace_card("E.F (65%)", calculate_pace(vma_val, 0.65))
                    render_pace_card("SEUIL (85%)", calculate_pace(vma_val, 0.85))
                    render_pace_card("VMA (100%)", calculate_pace(vma_val, 1.0))

        # --- SECTION : STRAVA ---
        me.text("ACTIVITÉS RÉCENTES", style=st.PAGE_SUBTITLE_STYLE)
        with me.box(style=st.SETTINGS_CARD_STYLE):
            with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", padding=me.Padding.all(20), width="100%")):
                me.icon("directions_run", style=me.Style(font_size=30, color=st.COLOR_PRIMARY, opacity=0.3))
                me.text("SYNCHRONISE TES ENTRAÎNEMENTS", style=me.Style(font_size="0.8rem", margin=me.Margin(top=10), font_weight="bold"))
                with me.box(style=me.Style(margin=me.Margin(top=10), cursor="pointer"), on_click=lambda e: setattr(s, "current_page", "settings")):
                    me.text("CONNECTER MON COMPTE STRAVA", style=st.LINK_STYLE)

        # --- SECTION : ACTION ---
        with me.box(style=me.Style(width="100%", margin=me.Margin(top=20, bottom=40), display="flex", justify_content="center")):
             me.button("GÉNÉRER UNE SÉANCE IA", on_click=on_generate_workout, type="flat", style=st.LOGIN_BUTTON_STYLE)