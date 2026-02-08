import mesop as me
import styles as st
from state import State
from datetime import datetime
import json

# ==================================================
# 1. ACTIONS & LOGIQUE
# ==================================================

def on_vma_slider_change(e: me.SliderValueChangeEvent):
    s = me.state(State)
    s.vma = float(e.value)

def on_vma_increment(e: me.ClickEvent):
    s = me.state(State)
    if s.vma < 24:
        s.vma = round(s.vma + 0.1, 1)

def on_vma_decrement(e: me.ClickEvent):
    s = me.state(State)
    if s.vma > 8:
        s.vma = round(s.vma - 0.1, 1)

def on_generate_workout(e: me.ClickEvent):
    pass

# ==================================================
# 2. UTILITAIRES DE CALCUL & FORMATAGE
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
    if not birth_date_str or len(birth_date_str) < 10:
        return "N/A"
    try:
        birth_date = datetime.strptime(birth_date_str[:10], "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return f"{age} ANS"
    except:
        return "N/A"

def format_duration(seconds: int) -> str:
    """Convertit les secondes en format MM:SS ou HH:MM:SS."""
    if not seconds: return "00:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}:{secs:02d}min"

# ==================================================
# 3. COMPOSANTS UI RÉUTILISABLES
# ==================================================

def render_metric_card(label: str, value: str, icon_name: str):
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
    with me.box(style=me.Style(
        background="rgba(40, 165, 168, 0.08)",
        padding=me.Padding.symmetric(vertical=15, horizontal=5),
        border_radius=12,
        width="31%", min_width="100px", text_align="center",
        border=me.Border.all(me.BorderSide(width=1, color="rgba(40, 165, 168, 0.2)"))
    )):
        me.text(label, style=me.Style(font_size="0.6rem", color=st.COLOR_PRIMARY, font_weight="700", letter_spacing="0.5px"))
        me.text(pace, style=me.Style(font_size="1.4rem", color=st.COLOR_TEXT, font_weight="900"))

def render_activity_item(act: dict):
    """Composant pour une ligne d'activité Strava."""
    with me.box(style=me.Style(
        display="flex", 
        justify_content="space-between", 
        align_items="center",
        width="100%",
        padding=me.Padding.symmetric(vertical=12),
        border=me.Border(bottom=me.BorderSide(width=1, color="rgba(255,255,255,0.05)"))
    )):
        with me.box():
            me.text(act.get("name", "Activité"), style=me.Style(font_weight="bold", font_size="0.9rem"))
            date_raw = act.get("start_date", "")[:10]
            me.text(date_raw, style=me.Style(font_size="0.75rem", opacity=0.6))
        
        with me.box(style=me.Style(text_align="right")):
            dist_km = act.get("distance", 0)
            me.text(f"{dist_km:.2f} km", style=me.Style(color=st.COLOR_PRIMARY, font_weight="bold"))
            me.text(format_duration(act.get("moving_time", 0)), style=me.Style(font_size="0.75rem", opacity=0.8))

# ==================================================
# 4. ÉCRAN PRINCIPAL
# ==================================================

def dashboard_screen(s: State):
    # --- NOUVEAU : RECHARGEMENT AUTOMATIQUE ---
    # Si on arrive sur la page et que le JSON est vide (ou "[]"), on recharge depuis la DB
    if not s.recent_activities_json or s.recent_activities_json == "[]":
        import supabase_db as db # Import local pour éviter les imports circulaires si besoin
        activities = db.get_latest_activities(s.user_id)
        if activities:
            s.recent_activities_json = json.dumps(activities)
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
                
                with me.box(style=me.Style(display="flex", align_items="center", gap=20)):
                    with me.content_button(type="icon", on_click=on_vma_decrement):
                        me.icon("remove_circle_outline", style=me.Style(color=st.COLOR_PRIMARY))
                    me.text(f"{vma_val:.1f}", style=me.Style(font_size=32, font_weight="900", color=st.COLOR_PRIMARY))
                    with me.content_button(type="icon", on_click=on_vma_increment):
                        me.icon("add_circle_outline", style=me.Style(color=st.COLOR_PRIMARY))

                me.text("VMA (KM/H)", style=me.Style(font_size=10, opacity=0.5, letter_spacing="1px"))
                
                with me.box(style=me.Style(width="90%", max_width=400, margin=me.Margin(top=10))):
                    me.slider(min=8, max=24, step=0.1, value=vma_val, on_value_change=on_vma_slider_change)

                me.box(style=me.Style(height=20))

                with me.box(style=me.Style(display="flex", flex_wrap="wrap", gap=8, width="100%", justify_content="center")):
                    render_pace_card("E.F (65%)", calculate_pace(vma_val, 0.65))
                    render_pace_card("SEUIL (85%)", calculate_pace(vma_val, 0.85))
                    render_pace_card("VMA (100%)", calculate_pace(vma_val, 1.0))

        # --- SECTION : STRAVA (DATABASE) ---
        me.text("ACTIVITÉS RÉCENTES", style=st.PAGE_SUBTITLE_STYLE)
        
        # On décode le JSON stocké dans le state (prévoir une valeur par défaut "[]")
        try:
            activities = json.loads(s.recent_activities_json or "[]")
        except:
            activities = []

        with me.box(style=st.SETTINGS_CARD_STYLE):
            if not activities:
                with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", padding=me.Padding.all(30), width="100%")):
                    me.icon("directions_run", style=me.Style(font_size=30, color=st.COLOR_PRIMARY, opacity=0.3))
                    me.text("AUCUNE ACTIVITÉ RÉCENTE", style=me.Style(font_size="0.8rem", margin=me.Margin(top=10), font_weight="bold"))
                    with me.box(style=me.Style(margin=me.Margin(top=10), cursor="pointer"), on_click=lambda e: setattr(s, "current_page", "settings")):
                        me.text("CONNECTER STRAVA", style=st.LINK_STYLE)
            else:
                with me.box(style=me.Style(padding=me.Padding.symmetric(horizontal=20, vertical=10), width="100%")):
                    for act in activities:
                        render_activity_item(act)
                    
                    # Petit bouton discret pour voir plus / gérer
                    with me.box(style=me.Style(margin=me.Margin(top=10), text_align="center")):
                        with me.box(style=me.Style(cursor="pointer"), on_click=lambda e: setattr(s, "current_page", "settings")):
                            me.text("VOIR TOUTES LES ACTIVITÉS", style=me.Style(font_size="0.7rem", color=st.COLOR_PRIMARY, font_weight="bold"))

        # --- SECTION : ACTION ---
        with me.box(style=me.Style(width="100%", margin=me.Margin(top=20, bottom=40), display="flex", justify_content="center")):
             me.button("GÉNÉRER UNE SÉANCE IA", on_click=on_generate_workout, type="flat", style=st.LOGIN_BUTTON_STYLE)