import mesop as me
import styles as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import replace
from state import State
import supabase_db as db 

# ==================================================
# 1. LOGIQUE DES GRAPHIQUES (PLOTLY)
# ==================================================

def render_distance_chart(filtered_activities):
    """Génère un graphique en barres interactif."""
    if not filtered_activities:
        return None
    
    df = pd.DataFrame(filtered_activities)
    df['start_date'] = pd.to_datetime(df['start_date'])
    
    # On groupe par mois
    df_monthly = df.set_index('start_date').resample('ME')['distance'].sum().reset_index()
    df_monthly['month_name'] = df_monthly['start_date'].dt.strftime('%b')

    fig = go.Figure(data=[
        go.Bar(
            x=df_monthly['month_name'],
            y=df_monthly['distance'],
            marker_color=st.COLOR_PRIMARY,
            text=df_monthly['distance'].round(0),
            textposition='auto',
        )
    ])

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=st.COLOR_TEXT),
        margin=dict(l=10, r=10, t=20, b=20),
        height=300,
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="km"),
        xaxis=dict(showgrid=False)
    )

    # Utilisation du mode 'config' pour s'assurer que c'est responsive
    return fig.to_html(
        full_html=False, 
        include_plotlyjs='cdn', 
        config={'responsive': True, 'displayModeBar': False}
    )

# ==================================================
# 2. ACTIONS
# ==================================================

def on_filter_year_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.cv_filter_year = e.value

def on_filter_type_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.cv_filter_type = e.value

# ==================================================
# 3. COMPOSANTS UI
# ==================================================

def render_stat_card(label, value, unit, is_record=False):
    border_color = st.COLOR_ACCENT if is_record else "rgba(40, 165, 168, 0.2)"
    card_style = replace(st.CV_STAT_CARD, border=me.Border.all(me.BorderSide(width=1, color=border_color)))
    
    with me.box(style=card_style):
        me.text(value + " " + unit, style=st.CV_STAT_VALUE)
        me.text(label, style=st.CV_STAT_LABEL)

# ==================================================
# 4. ÉCRAN PRINCIPAL
# ==================================================

def cv_screen(s: State):
    # Récupération des données (Limitée par ta fonction DB à 5000 désormais)
    all_activities = db.get_all_user_activities(s.user_id) or []

    # Années disponibles
    years = sorted(list(set(a['start_date'][:4] for a in all_activities)), reverse=True)
    years_options = [me.SelectOption(label="Toutes les années", value="Toutes")] + \
                    [me.SelectOption(label=y, value=y) for y in years]

    # Filtrage
    filtered = all_activities
    if s.cv_filter_year != "Toutes":
        filtered = [a for a in filtered if a['start_date'].startswith(s.cv_filter_year)]
    if s.cv_filter_type != "Tous":
        filtered = [a for a in filtered if a['type'] == s.cv_filter_type]

    # Stats
    total_dist = sum(a.get('distance', 0) for a in filtered)
    total_elev = sum(a.get('total_elevation_gain', 0) for a in filtered)
    total_time = sum(a.get('moving_time', 0) for a in filtered) / 3600
    count = len(filtered)

    with me.box(style=st.CONTENT_CONTAINER):
        me.text("MON CV SPORTIF", style=st.PAGE_TITLE_STYLE)
        
        # Filtres
        with me.box(style=st.FILTER_BAR_STYLE):
            me.select(label="Année", options=years_options, value=s.cv_filter_year,
                      on_selection_change=on_filter_year_change, style=me.Style(width=200))
            me.select(label="Discipline", 
                      options=[me.SelectOption(label="Tous", value="Tous"), 
                               me.SelectOption(label="Course", value="Run"),
                               me.SelectOption(label="Vélo", value="Ride")], 
                      value=s.cv_filter_type, on_selection_change=on_filter_type_change, style=me.Style(width=200))

        # Stats Grid
        with me.box(style=st.CV_STATS_GRID):
            render_stat_card("Activités", f"{count:,}".replace(",", " "), "sorties")
            render_stat_card("Distance", f"{total_dist:,.0f}".replace(",", " "), "km")
            render_stat_card("Dénivelé", f"{total_elev:,.0f}".replace(",", " "), "m")
            render_stat_card("Temps total", f"{total_time:.0f}", "h")

        # Graphique
        if count > 0:
            me.box(style=me.Style(height=30))
            me.text("ÉVOLUTION MENSUELLE", style=st.PAGE_SUBTITLE)
            chart_html = render_distance_chart(filtered)
            if chart_html:
                # On force une hauteur minimum pour la boîte qui contient le HTML
                with me.box(style=me.Style(
                    background=st.COLOR_CARD_BG,
                    padding=me.Padding.all(15),
                    border_radius=15,
                    margin=me.Margin(top=10, bottom=20),
                    min_height=320 
                )):
                    me.html(chart_html)

        # Records
        if count > 0:
            me.text("RECORDS SUR CETTE SÉLECTION", style=st.PAGE_SUBTITLE)
            max_dist = max((a.get('distance', 0) for a in filtered), default=0)
            max_elev = max((a.get('total_elevation_gain', 0) for a in filtered), default=0)
            
            with me.box(style=st.CV_STATS_GRID):
                render_stat_card("Plus longue distance", f"{max_dist:.1f}", "km", is_record=True)
                render_stat_card("Plus gros dénivelé", f"{max_elev:.0f}", "m", is_record=True)