import mesop as me

# ==================================================
# 1. PALETTE DE COULEURS OFFICIELLE
# ==================================================

COLOR_BG = "#ffffff"        # Bleu nuit (Fond)
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
    "family=Kanit:wght@900;700&display=swap"
)

# ==================================================
# 3. LAYOUT GLOBAL
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
    font_size="clamp(2.6rem, 9vw, 5.5rem)",
    font_weight="900",
    color=COLOR_PRIMARY,
    text_transform="uppercase",
    line_height="1",
)

LOGO_TEXT_SECONDARY_STYLE = me.Style(
    font_family="Kanit, sans-serif",
    font_size="clamp(2.6rem, 9vw, 5.5rem)",
    font_weight="900",
    color=COLOR_ACCENT,
    text_transform="uppercase",
    line_height="1",
)

LOGO_SUBTITLE_STYLE = me.Style(
    font_family="Inter, sans-serif",
    font_size="clamp(1.5rem, 2vw, 1.1rem)", # Corrigé : plus petit pour l'équilibre
    color=COLOR_TEXT,
    opacity=0.9,
    letter_spacing="0.05rem",
    margin=me.Margin(top=5),
    text_align="center",
)

# ==================================================
# 5. FORMULAIRES ET SAISIE
# ==================================================

LOGIN_FORM_CONTAINER = me.Style(
    background=COLOR_CARD_BG,
    padding=me.Padding.all(30),
    border_radius=25,
    width="100%",
    max_width=380,
    display="flex",
    flex_direction="column",
    align_items="stretch",
    border=me.Border.all(me.BorderSide(width=1, color="rgba(64,224,208,0.2)")),
    box_shadow="0 10px 30px rgba(0,0,0,0.3)",
)

# styles.py (Section 5)

INPUT_STYLE = me.Style(
    background=COLOR_INPUT_BG,
    color=COLOR_SECONDARY,
    border_radius=12,
    # On passe le vertical à 0 car Mesop ajoute déjà un padding interne 
    # important aux composants input. Cela va vraiment "dégonfler" la zone.
    padding=me.Padding.symmetric(horizontal=12, vertical=0), 
    margin=me.Margin(bottom=10),
    width="100%",
    # On s'assure que le texte est bien lisible
    font_weight="500", 
    line_height="1.2",
    # On retire la bordure ou on la met en turquoise très clair 
    # pour rester dans ta palette au lieu du noir (0,0,0)
    border=me.Border.all(
        me.BorderSide(width=1, color="rgba(64, 224, 208, 0.1)")
    )
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
# 6. BOUTONS ET LIENS
# ==================================================

LOGIN_BUTTON_STYLE = me.Style(
    background=COLOR_PRIMARY,
    color=COLOR_BG,
    font_weight="700",
    height=50,
    border_radius=15,
    margin=me.Margin(top=15),
    cursor="pointer",
)

LOGIN_BUTTON_DISABLED_STYLE = me.Style(
    background="#444444",        # Gris foncé pour l'aspect désactivé
    color="#888888",             # Texte grisé
    width="100%",
    padding=me.Padding.all(15),
    border_radius=10,
    font_weight="bold",
    text_transform="uppercase",
    cursor="not-allowed",        # Change le curseur de la souris
    opacity=0.6                  # Légère transparence
)

LINK_STYLE = me.Style(
    color=COLOR_PRIMARY,       # Changé de COLOR_TEXT à COLOR_PRIMARY (Turquoise)
    font_size="0.85rem",
    text_decoration="underline",
    cursor="pointer",
    margin=me.Margin(top=10, bottom=5),
    text_align="center",
    font_weight="600",         # Optionnel : un peu plus gras pour la lisibilité
)

# ==================================================
# 7. NAVIGATION ET CARTES (AJOUTÉ / FIXÉ)
# ==================================================

NAVBAR_CONTAINER_STYLE = me.Style(
    display="flex",
    gap=12,
    justify_content="center",
    margin=me.Margin(bottom=30),
)

NAV_BUTTON_BASE_STYLE = me.Style(
    border_radius=999,
    padding=me.Padding.symmetric(vertical=10, horizontal=20),
    font_weight="700",
    font_size="0.75rem",
    text_transform="uppercase",
    cursor="pointer",
)

# INDISPENSABLE POUR dashboard.py
CARDS_CONTAINER_STYLE = me.Style(
    display="flex",
    gap=16,
    justify_content="center",
    flex_wrap="wrap",
    width="100%",
    max_width=640,
    margin=me.Margin(top=10),
)

METRIC_CARD_STYLE = me.Style(
    background=COLOR_CARD_BG,
    padding=me.Padding.all(20),
    border_radius=20,
    width="calc(50% - 10px)",
    min_width=150,
    display="flex",
    flex_direction="column",
    gap=8,
    border=me.Border.all(me.BorderSide(width=1, color="rgba(64,224,208,0.1)")),
)

CARD_LABEL_STYLE = me.Style(
    color=COLOR_PRIMARY,
    font_size="0.8rem",
    font_weight="700",
)

CARD_VALUE_STYLE = me.Style(
    color=COLOR_TEXT,
    font_size="1.4rem",
    font_weight="800",
)

# ==================================================
# 8. MESSAGES ET FEEDBACK
# ==================================================

ERROR_TEXT_STYLE = me.Style(
    color=COLOR_ERROR,
    font_size="0.85rem",
    margin=me.Margin(top=15),
    text_align="center",
    font_weight="600"
)

SUCCESS_TEXT_STYLE = me.Style(
    color=COLOR_PRIMARY,     # Turquoise pour le succès
    font_size="0.85rem",
    margin=me.Margin(top=15),
    text_align="center",
    font_weight="600",
    font_family="Inter, sans-serif",
)

# TITRES ET TEXTES GÉNÉRAUX

# --- 1. TITRE DE PAGE (Orange, Majuscule, Kanit 700) ---
PAGE_TITLE = me.Style(
    color=COLOR_ACCENT,        # Ton orange #F37B1F
    font_family="Kanit",
    font_size="2.2rem",
    font_weight="700",
    text_transform="uppercase",
    letter_spacing=1,
    margin=me.Margin(bottom=5)
)

# --- 2. SOUS-TITRE DE PAGE (Turquoise, Inter 600) ---
PAGE_SUBTITLE = me.Style(
    color=COLOR_PRIMARY,       # Ton turquoise #28A5A8
    font_family="Inter",
    font_size="1.1rem",
    font_weight="600",
    margin=me.Margin(bottom=20)
)

# --- 3. TEXTE NORMAL (Gris clair E5E5E5, Inter) ---
TEXT_NORMAL = me.Style(
    color=COLOR_TEXT,           # Gris clair spécifique
    font_family="Inter",
    font_size="1rem",
    font_weight="400",
    line_height="1.5"          # Pour une meilleure lisibilité
)

