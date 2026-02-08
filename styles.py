import mesop as me

# ==================================================
# 1. PALETTE DE COULEURS OFFICIELLE
# ==================================================
COLOR_BG = "#0d0b50"        # Bleu nuit (Fond)
COLOR_CARD_BG = "#161465"   # Bleu cartes
COLOR_SECONDARY = "#0D0B50" # Bleu nuit profond (Texte dans zones claires)
COLOR_PRIMARY = "#28A5A8"   # Turquoise (Boutons / Accents)
COLOR_ACCENT = "#F37B1F"    # Orange (Titres)
COLOR_TEXT = "#E5E5E5"      # Gris clair (Texte général)
COLOR_INPUT_BG = "#E5E5E5"  # Gris clair (Champs de saisie)
COLOR_ERROR = "#FF4B4B"     # Rouge erreurs

# ==================================================
# 2. POLICES
# ==================================================
FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;600;700&"
    "family=Kanit:wght@700;900&display=swap"
)

# ==================================================
# 3. LAYOUT GLOBAL ET CONTENEURS
# ==================================================
MAIN_BOX_STYLE = me.Style(
    background=COLOR_BG,
    min_height="100vh",
    display="flex",
    flex_direction="column",
    align_items="center",
    font_family="Inter, sans-serif",
    color=COLOR_TEXT,
    padding=me.Padding.symmetric(vertical=20, horizontal=10),
)

# Conteneur de contenu principal (utilisé dans main.py)
CONTENT_CONTAINER = me.Style(
    display="flex",
    flex_direction="column",
    align_items="center",
    width="100%",
    max_width=800,
    padding=me.Padding.all(20),
    box_sizing="border-box",
)

# ==================================================
# 4. LOGO / HEADER
# ==================================================
LOGO_CONTAINER_STYLE = me.Style(
    text_align="center",
    margin=me.Margin(top="5vh", bottom="3vh"),
    width="100%",
)

LOGO_ROW_STYLE = me.Style(
    display="flex",
    justify_content="center",
    align_items="baseline",
)

LOGO_TEXT_MAIN_STYLE = me.Style(
    font_family="Kanit, sans-serif",
    font_size="clamp(2rem, 6vw, 4rem)", 
    font_weight="900",
    color=COLOR_PRIMARY,
    text_transform="uppercase",
    line_height="1",
)

LOGO_TEXT_SECONDARY_STYLE = me.Style(
    font_family="Kanit, sans-serif",
    font_size="clamp(2rem, 6vw, 4rem)",
    font_weight="900",
    color=COLOR_ACCENT,
    text_transform="uppercase",
    line_height="1",
)

LOGO_SUBTITLE_STYLE = me.Style(
    font_family="Inter, sans-serif",
    font_size="clamp(0.67rem, 2.5vw, 1.4rem)", 
    color=COLOR_TEXT,
    opacity=0.8,
    letter_spacing="0.02rem",
    margin=me.Margin(top=2),
    text_align="center",
    white_space="nowrap", 
)

# ==================================================
# 5. TITRES ET TEXTES GÉNÉRAUX (UNIFORMISATION)
# ==================================================

# Titre de page principal (Dashboard, Paramètres, etc.)
PAGE_TITLE_STYLE = me.Style(
    color=COLOR_ACCENT,
    font_family="Kanit, sans-serif",
    font_size="clamp(1.5rem, 5vw, 2.2rem)",
    font_weight="900",
    text_transform="uppercase",
    letter_spacing="1px",
    margin=me.Margin(bottom=15, top=10),
    text_align="center"
)

# Alias pour compatibilité
PAGE_TITLE = PAGE_TITLE_STYLE

# Sous-titre de section (ex: "MON COMPTE" dans les réglages)
PAGE_SUBTITLE = me.Style(
    color=COLOR_PRIMARY,
    font_family="Inter, sans-serif",
    font_size="1.1rem",
    font_weight="600",
    text_align="left",
    width="100%",
    margin=me.Margin(top=30, bottom=15),
    letter_spacing="0.5px"
)

# Optionnel : créer un alias pour éviter l'erreur si tu as déjà codé avec _STYLE
PAGE_SUBTITLE_STYLE = PAGE_SUBTITLE

TEXT_NORMAL = me.Style(
    color=COLOR_TEXT,
    font_family="Inter, sans-serif",
    font_size="1rem",
    font_weight="400",
    line_height="1.5"
)

# ==================================================
# 6. FORMULAIRES ET SAISIE
# ==================================================
LOGIN_FORM_CONTAINER = me.Style(
    background=COLOR_CARD_BG,
    padding=me.Padding.all(30),
    border_radius=25,
    width="100%",
    max_width=420, # Légèrement augmenté pour donner de l'air aux champs côte à côte
    display="flex",
    flex_direction="column",
    align_items="stretch",
    # --- LES AJUSTEMENTS CLÉS ---
    height="auto",               # Laisse le cadre grandir avec le contenu
    min_height="400px",          # Une base minimum pour garder un bel aspect
    margin=me.Margin(bottom=40), # Évite que le bas du cadre ne touche le bord de l'écran
    # ----------------------------
    border=me.Border.all(me.BorderSide(width=1, color="rgba(64,224,208,0.2)")),
    box_shadow="0 10px 30px rgba(0,0,0,0.3)",
    box_sizing="border-box",
)

INPUT_STYLE = me.Style(
    background=COLOR_INPUT_BG,
    color=COLOR_SECONDARY,
    border_radius=12,
    padding=me.Padding.symmetric(horizontal=16, vertical=0), 
    margin=me.Margin(bottom=10),
    width="100%",
    height=70, # Hauteur optimisée pour le tactile
    font_weight="500", 
    border=me.Border.all(me.BorderSide(width=1, color="rgba(64, 224, 208, 0.1)")),
    box_sizing="border-box",
)

LOGIN_TITLE_STYLE = me.Style(
    font_family="Kanit, sans-serif",
    font_size="1.8rem",
    font_weight="900",
    color=COLOR_ACCENT,
    text_transform="uppercase",
    margin=me.Margin(bottom=25),
    text_align="center",
)

# ==================================================
# 7. BOUTONS ET LIENS
# ==================================================
LOGIN_BUTTON_STYLE = me.Style(
    background=COLOR_PRIMARY,
    color=COLOR_BG,
    font_weight="700",
    height=50,
    border_radius=15,
    margin=me.Margin(top=15),
    cursor="pointer",
    width="100%",
)

LOGIN_BUTTON_DISABLED_STYLE = me.Style(
    background="#444444",
    color="#888888",
    width="100%",
    padding=me.Padding.all(15),
    border_radius=15,
    font_weight="bold",
    text_transform="uppercase",
    cursor="not-allowed",
    opacity=0.6
)

LINK_STYLE = me.Style(
    color=COLOR_PRIMARY,
    font_size="0.85rem",
    text_decoration="underline",
    cursor="pointer",
    margin=me.Margin(top=10, bottom=5),
    text_align="center",
    font_weight="600",
)

# ==================================================
# 8. NAVIGATION ET CARTES
# ==================================================
NAVBAR_CONTAINER_STYLE = me.Style(
    display="flex",
    gap=8,
    justify_content="center",
    margin=me.Margin(bottom=20),
    flex_wrap="wrap",
)

NAV_BUTTON_BASE_STYLE = me.Style(
    border_radius=999,
    padding=me.Padding.symmetric(vertical=8, horizontal=16),
    font_weight="700",
    font_size="0.75rem",
    text_transform="uppercase",
    cursor="pointer",
)

CARDS_CONTAINER_STYLE = me.Style(
    display="flex",
    gap=12,
    justify_content="center",
    flex_wrap="wrap",
    width="100%",
    max_width=640,
    margin=me.Margin(top=10, bottom=20),
)

METRIC_CARD_STYLE = me.Style(
    background=COLOR_CARD_BG,
    padding=me.Padding.all(16),
    border_radius=20,
    width="calc(50% - 6px)", 
    min_width=140,
    display="flex",
    flex_direction="column",
    gap=4,
    border=me.Border.all(me.BorderSide(width=1, color="rgba(64,224,208,0.1)")),
    box_sizing="border-box",
    box_shadow="0 4px 10px rgba(0,0,0,0.1)",
)

CARD_LABEL_STYLE = me.Style(
    color=COLOR_PRIMARY,
    font_size="0.75rem",
    font_weight="700",
    overflow_wrap="anywhere",
)

CARD_VALUE_STYLE = me.Style(
    color=COLOR_TEXT,
    font_size="1.2rem",
    font_weight="800",
    overflow_wrap="anywhere",
)

# ==================================================
# 9. MESSAGES ET FEEDBACK
# ==================================================
ERROR_TEXT_STYLE = me.Style(
    color=COLOR_ERROR,
    font_size="0.85rem",
    margin=me.Margin(top=15),
    text_align="center",
    font_weight="600"
)

SUCCESS_TEXT_STYLE = me.Style(
    color=COLOR_PRIMARY,
    font_size="0.85rem",
    margin=me.Margin(top=15),
    text_align="center",
    font_weight="600",
)

# ==================================================
# 10. COMPOSANTS RÉGLAGES (SETTINGS)
# ==================================================

BACK_BUTTON_CONTAINER = me.Style(
    display="flex", 
    align_items="center", 
    cursor="pointer", 
    align_self="flex-start",
    margin=me.Margin(bottom=20)
)

BACK_BUTTON_TEXT = me.Style(
    color=COLOR_PRIMARY, 
    font_weight="600", 
    margin=me.Margin(left=8)
)

SETTINGS_CARD_STYLE = me.Style(
    display="flex",
    align_items="center",
    padding=me.Padding.all(18),
    background=COLOR_CARD_BG,
    border_radius=20,
    cursor="pointer",
    margin=me.Margin(bottom=12),
    width="100%",
    max_width=500,
    border=me.Border.all(me.BorderSide(width=1, color="rgba(255,255,255,0.05)")),
    box_shadow="0 4px 12px rgba(0,0,0,0.2)",
    box_sizing="border-box",
)

SETTINGS_CARD_TITLE = me.Style(
    color=COLOR_PRIMARY, 
    font_weight="800", 
    font_size="1.1rem",
    font_family="Inter, sans-serif",
)

SETTINGS_CARD_SUBTITLE = me.Style(
    color=COLOR_TEXT, 
    font_size="0.8rem", 
    font_weight="400",
    opacity=0.6,
)

# ==================================================
# 11. ITEMS D'ACTIVITÉS (DASHBOARD)
# ==================================================

ACTIVITY_ITEM_CONTAINER = me.Style(
    display="flex", 
    justify_content="space-between", 
    align_items="center",
    padding=me.Padding.symmetric(vertical=15, horizontal=12),
    border=me.Border(bottom=me.BorderSide(width=1, color="rgba(255,255,255,0.08)")),
    width="100%"
)

ACTIVITY_NAME_STYLE = me.Style(
    font_weight="700", 
    font_size="1rem", 
    color=COLOR_TEXT,
    font_family="Inter"
)

ACTIVITY_DATE_STYLE = me.Style(
    font_size="0.8rem", 
    color=COLOR_TEXT,
    opacity=0.6,
    margin=me.Margin(top=2)
)

ACTIVITY_DISTANCE_STYLE = me.Style(
    color=COLOR_PRIMARY,
    font_weight="900", 
    font_size="1.1rem",
    font_family="Kanit"
)