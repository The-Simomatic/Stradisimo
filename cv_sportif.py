import mesop as me
import styles as st
import json
from datetime import datetime
from dataclasses import replace
from state import State
import supabase_db as db  # Import pour interroger la base de données

def on_filter_year_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.cv_filter_year = e.value

def on_filter_type_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.cv_filter_type = e.value

def cv_screen(s: State):
    # 1. RÉCUPÉRATION DES DONNÉES DEPUIS LA DB
    # On récupère TOUT l'historique pour calculer les stats réelles
    all_activities = db.get_all_user_activities(s.user_id) or []

    # 2. PRÉPARATION DES FILTRES
    # Extraction des années uniques à partir de l'historique complet
    years = sorted(list(set(a['start_date'][:4] for a in all_activities)), reverse=True)
    years_options = [me.SelectOption(label="Toutes les années", value="Toutes")] + \
                    [me.SelectOption(label=y, value=y) for y in years]

    types_options = [
        me.SelectOption(label="Tous les sports", value="Tous"),
        me.SelectOption(label="Course à pied", value="Run"),
        me.SelectOption(label="Vélo", value="Ride"),
        me.SelectOption(label="Natation", value="Swim"),
    ]

    # 3. APPLICATION DES FILTRES SUR LA LISTE COMPLÈTE
    filtered = all_activities
    if s.cv_filter_year != "Toutes":
        filtered = [a for a in filtered if a['start_date'].startswith(s.cv_filter_year)]
    if s.cv_filter_type != "Tous":
        filtered = [a for a in filtered if a['type'] == s.cv_filter_type]

    # 4. CALCULS DES STATS
    total_dist = sum(a.get('distance', 0) for a in filtered)  # km
    total_elev = sum(a.get('total_elevation_gain', 0) for a in filtered)
    total_time = sum(a.get('moving_time', 0) for a in filtered) / 3600  # heures
    count = len(filtered)

    # 5. RENDU DE L'INTERFACE
    with me.box(style=st.CONTENT_CONTAINER):
        me.text("MON CV SPORTIF", style=st.PAGE_TITLE_STYLE)
        
        # --- BARRE DE FILTRES ---
        with me.box(style=st.FILTER_BAR_STYLE):
            me.select(
                label="Année",
                options=years_options,
                value=s.cv_filter_year,
                on_selection_change=on_filter_year_change,
                style=me.Style(width=200)
            )
            me.select(
                label="Discipline",
                options=types_options,
                value=s.cv_filter_type,
                on_selection_change=on_filter_type_change,
                style=me.Style(width=200)
            )

        # --- GRILLE DE STATS GLOBALES ---
        with me.box(style=st.CV_STATS_GRID):
            render_stat_card("Activités", str(count), "sorties")
            render_stat_card("Distance", f"{total_dist:,.0f}".replace(",", " "), "km")
            render_stat_card("Dénivelé", f"{total_elev:,.0f}".replace(",", " "), "m")
            render_stat_card("Temps total", f"{total_time:.0f}", "h")

        # --- SECTION RECORDS PERSONNELS ---
        if count > 0:
            me.box(style=me.Style(height=40)) # Espacement
            me.text("RECORDS PERSONNELS SUR CETTE SÉLECTION", style=st.PAGE_SUBTITLE)
            
            max_dist = max(a.get('distance', 0) for a in filtered)
            max_elev = max(a.get('total_elevation_gain', 0) for a in filtered)
            
            with me.box(style=st.CV_STATS_GRID):
                render_stat_card("Plus longue distance", f"{max_dist:.1f}", "km", is_record=True)
                render_stat_card("Plus gros dénivelé", f"{max_elev:.0f}", "m", is_record=True)

def render_stat_card(label, value, unit, is_record=False):
    """Affiche une carte de statistique stylisée."""
    border_color = st.COLOR_ACCENT if is_record else "rgba(40, 165, 168, 0.2)"
    
    # Correction : Utilisation de replace() de dataclasses pour modifier le Style
    card_style = replace(
        st.CV_STAT_CARD, 
        border=me.Border.all(me.BorderSide(width=1, color=border_color))
    )
    
    with me.box(style=card_style):
        me.text(value + " " + unit, style=st.CV_STAT_VALUE)
        me.text(label, style=st.CV_STAT_LABEL)