import mesop as me
import styles as st
from state import State

# ==================================================
# LOGIQUE DE NAVIGATION
# ==================================================

def on_nav_click(e: me.ClickEvent):
    """Gère le changement de page via la navbar."""
    s = me.state(State)
    # Réinitialisation des messages lors du changement d'onglet
    s.error_message = ""
    s.success_message = ""
    s.current_page = e.key

def on_settings_click(e: me.ClickEvent):
    """Redirige vers la page des paramètres."""
    s = me.state(State)
    s.current_page = "settings"

# ==================================================
# HEADER (LOGO CENTRÉ + ACTIONS)
# ==================================================

def render_header(s: State, on_logout):
    # On ajoute une position fixe ou un z-index si nécessaire
    with me.box(style=me.Style(
        display="flex",
        justify_content="space-between",
        align_items="center",
        width="100%",
        padding=me.Padding.symmetric(horizontal=15, vertical=12),
        border=me.Border(bottom=me.BorderSide(width=1, color="rgba(255,255,255,0.1)", style="solid")),
        background=st.COLOR_BG # Assure que le header est opaque
    )):
        
        # --- BLOC GAUCHE (Espaceur pour centrage parfait) ---
        with me.box(style=me.Style(flex_grow=1, flex_basis="0%")):
            pass

        # --- BLOC CENTRAL (Logo) ---
        with me.box(style=me.Style(
            display="flex",
            flex_direction="column",
            align_items="center",
            flex_grow=2,
        )):
            with me.box(style=st.LOGO_ROW_STYLE):
                me.text("STRADI", style=st.LOGO_TEXT_MAIN_STYLE)
                me.text("SIMO", style=st.LOGO_TEXT_SECONDARY_STYLE)
            
            me.text(
                "L'appli qui rend la route grandissime",
                style=st.LOGO_SUBTITLE_STYLE
            )

        # --- BLOC DROITE (Actions) ---
        with me.box(style=me.Style(
            display="flex",
            justify_content="flex-end",
            gap=12,
            align_items="center",
            flex_grow=1,
            flex_basis="0%"
        )):
            if s.is_logged_in:
                # Bouton Settings
                with me.content_button(type="icon", on_click=on_settings_click):
                    me.icon(icon="settings", style=me.Style(color=st.COLOR_PRIMARY))
                
                # Bouton Logout
                with me.content_button(type="icon", on_click=on_logout):
                    me.icon(icon="logout", style=me.Style(color=st.COLOR_ERROR))

# ==================================================
# NAVIGATION (BARRE D'ONGLETS)
# ==================================================

def nav_button(label: str, page: str, s: State):
    """Composant bouton pour la navbar avec gestion de l'état actif."""
    is_active = s.current_page == page
    
    # On utilise merge si possible ou une construction simplifiée
    button_style = me.Style(
        border_radius=st.NAV_BUTTON_BASE_STYLE.border_radius,
        padding=st.NAV_BUTTON_BASE_STYLE.padding,
        font_weight=st.NAV_BUTTON_BASE_STYLE.font_weight,
        font_size=st.NAV_BUTTON_BASE_STYLE.font_size,
        text_transform=st.NAV_BUTTON_BASE_STYLE.text_transform,
        cursor="pointer",
        # Style dynamique
        background=st.COLOR_PRIMARY if is_active else "transparent",
        color=st.COLOR_BG if is_active else st.COLOR_PRIMARY,
        border=me.Border.all(me.BorderSide(width=1, color=st.COLOR_PRIMARY)),
        # Petite ombre portée sur le bouton actif
        box_shadow="0 2px 8px rgba(40, 165, 168, 0.3)" if is_active else None
    )
    
    me.button(
        key=page,
        label=label,
        on_click=on_nav_click,
        type="flat",
        style=button_style
    )

def render_navbar(s: State):
    """Affiche la barre de navigation centrée."""
    with me.box(style=st.NAVBAR_CONTAINER_STYLE):
        nav_button("Dashboard", "dashboard", s)
        nav_button("Planning", "planning", s)
        nav_button("CV Sportif", "cv", s)

# ==================================================
# CARTES ET MÉTRIQUES
# ==================================================

def metric_card(label: str, value: str):
    """Carte de statistique réutilisable."""
    with me.box(style=st.METRIC_CARD_STYLE):
        me.text(label, style=st.CARD_LABEL_STYLE)
        me.text(value, style=st.CARD_VALUE_STYLE)