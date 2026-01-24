import mesop as me
import styles as st
from state import State

def on_back_click(e: me.ClickEvent):
    s = me.state(State)
    s.current_page = "dashboard" 

def cgu_screen(s: State):
    # TOUT LE CODE CI-DESSOUS DOIT ÊTRE INDENTÉ (décalé vers la droite)
    with me.box(style=me.Style(
        background=st.COLOR_CARD_BG,
        padding=me.Padding.all(30),
        border_radius=20,
        max_width=800,
        margin=me.Margin.symmetric(vertical=40, horizontal="auto"),
        border=me.Border.all(me.BorderSide(width=1, color="rgba(64,224,208,0.2)"))
    )):
        # Bouton Retour
        with me.box(on_click=on_back_click, style=me.Style(cursor="pointer", margin=me.Margin(bottom=20))):
            me.text("← Retour", style=me.Style(color=st.COLOR_PRIMARY, font_weight="bold", font_size="0.8rem"))

        # TITRE PRINCIPAL
        me.text("CONDITIONS GÉNÉRALES D'UTILISATION", style=st.PAGE_TITLE)
        
        me.text("Mentions légales et protection des données", 
                style=me.Style(color=st.COLOR_TEXT, opacity=0.6, font_size="0.9rem", margin=me.Margin(bottom=20)))

        # ZONE DE TEXTE (Déroulante)
        # Verifie bien que cette ligne est alignée avec le me.text au dessus
        with me.box(style=me.Style(
            margin=me.Margin(top=10), 
            height=400, 
            overflow_y="scroll",
            padding=me.Padding(right=15)
        )):
            # SECTION 1
            me.text("1. Présentation du service", style=st.PAGE_SUBTITLE)
            me.text(
                "Stradisimo est une plateforme de suivi sportif. En créant un compte, vous acceptez le stockage de vos données de profil (poids, sport, niveau) pour personnaliser votre expérience.",
                style=st.TEXT_NORMAL 
            )
            me.box(style=me.Style(height=25))

            # SECTION 2
            me.text("2. Données personnelles", style=st.PAGE_SUBTITLE)
            me.text(
                "Conformément au RGPD, vous disposez d'un droit d'accès et de suppression de vos données via la page Paramètres de l'application.",
                style=st.TEXT_NORMAL
            )
            me.box(style=me.Style(height=25))

            # SECTION 3
            me.text("3. Utilisation du service", style=st.PAGE_SUBTITLE)
            me.text(
                "L'utilisateur s'engage à fournir des informations exactes. Stradisimo ne pourra être tenu responsable des blessures liées à une mauvaise pratique sportive.",
                style=st.TEXT_NORMAL
            )
            me.box(style=me.Style(height=25))

            # SECTION 4
            me.text("4. Cookies et traceurs", style=st.PAGE_SUBTITLE)
            me.text(
                "Nous utilisons uniquement des cookies techniques nécessaires à votre authentification via Supabase.",
                style=st.TEXT_NORMAL
            )

        # FOOTER
        with me.box(style=me.Style(margin=me.Margin(top=20), text_align="center", opacity=0.4)):
            me.text("© 2026 Stradisimo. Tous droits réservés.", style=st.TEXT_NORMAL)