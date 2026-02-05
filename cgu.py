import mesop as me
import styles as st
from state import State

def on_back_click(e: me.ClickEvent):
    s = me.state(State)
    # On valide définitivement la consultation quand il quitte la page
    s.has_opened_cgu = True 
    
    if s.is_logged_in:
        s.current_page = "dashboard"
    else:
        # S'il vient du Signup, current_page repassera à 'login' 
        # mais s.show_signup restera True, donc il reviendra au bon endroit.
        s.current_page = "login"

def cgu_screen(s: State):
    # Conteneur principal avec le style "Card" que tu as défini
    with me.box(style=me.Style(
        background=st.COLOR_CARD_BG,
        padding=me.Padding.all(35),
        border_radius=20,
        max_width=850,
        margin=me.Margin.symmetric(vertical=40, horizontal="auto"),
        border=me.Border.all(me.BorderSide(width=1, color="rgba(40, 165, 168, 0.2)")),
        box_shadow="0 12px 40px rgba(0,0,0,0.15)"
    )):
        # Bouton Retour
        with me.box(on_click=on_back_click, style=me.Style(
            cursor="pointer", 
            display="flex", 
            align_items="center",
            gap=8,
            margin=me.Margin(bottom=25)
        )):
            me.icon(icon="arrow_back", style=me.Style(font_size=20, color=st.COLOR_PRIMARY))
            me.text("RETOUR", style=me.Style(color=st.COLOR_PRIMARY, font_weight="700", font_size="0.85rem", letter_spacing="1px"))

        # TITRE PRINCIPAL
        # Note : Vérifie que st.PAGE_TITLE existe, sinon utilise st.LOGIN_TITLE_STYLE
        me.text("CONDITIONS GÉNÉRALES D'UTILISATION", style=st.LOGIN_TITLE_STYLE)
        
        me.text("Date d'entrée en vigueur : 1er Février 2026", 
                style=me.Style(color=st.COLOR_TEXT, opacity=0.5, font_size="0.85rem", margin=me.Margin(bottom=30)))

        # ZONE DE TEXTE (Déroulante pour mobile)
        with me.box(style=me.Style(
            height=480, 
            overflow_y="scroll",
            padding=me.Padding(right=20)
        )):
            
            # --- SECTION 1 ---
            me.text("1. OBJET DU SERVICE", style=me.Style(color=st.COLOR_PRIMARY, font_weight="bold", margin=me.Margin(bottom=10)))
            me.text(
                "Stradisimo fournit une interface d'analyse de données sportives et de génération de plans d'entraînement personnalisés. L'accès au service est réservé aux personnes physiques majeures pour un usage strictement personnel.",
                style=me.Style(color=st.COLOR_TEXT, line_height="1.5", font_size="0.9rem")
            )
            me.box(style=me.Style(height=25))

            # --- SECTION 2 ---
            me.text("2. AVERTISSEMENT SANTÉ & RESPONSABILITÉ", style=me.Style(color=st.COLOR_PRIMARY, font_weight="bold", margin=me.Margin(bottom=10)))
            me.text(
                "L'utilisation de Stradisimo ne se substitue en aucun cas à un avis médical professionnel. L'utilisateur reconnaît expressément que :",
                style=me.Style(color=st.COLOR_TEXT, line_height="1.5", font_size="0.9rem")
            )
            with me.box(style=me.Style(margin=me.Margin(left=15, top=10))):
                me.text("• Il a consulté un médecin et possède un certificat de non-contre-indication.", style=me.Style(color=st.COLOR_TEXT, font_size="0.9rem"))
                me.text("• Stradisimo n'est pas responsable des blessures ou accidents.", style=me.Style(color=st.COLOR_TEXT, font_size="0.9rem"))
                me.text("• Les plans sont des suggestions automatisées basées sur des algorithmes.", style=me.Style(color=st.COLOR_TEXT, font_size="0.9rem"))
            me.box(style=me.Style(height=25))

            # --- SECTION 3 ---
            me.text("3. PROTECTION DES DONNÉES (RGPD)", style=me.Style(color=st.COLOR_PRIMARY, font_weight="bold", margin=me.Margin(bottom=10)))
            me.text(
                "Conformément au RGPD, Stradisimo s'engage à protéger la confidentialité de vos informations sportives via la technologie Supabase.",
                style=me.Style(color=st.COLOR_TEXT, line_height="1.5", font_size="0.9rem")
            )
            me.box(style=me.Style(height=25))

            # --- SECTION 4 ---
            me.text("4. PROPRIÉTÉ INTELLECTUELLE", style=me.Style(color=st.COLOR_PRIMARY, font_weight="bold", margin=me.Margin(bottom=10)))
            me.text(
                "L'architecture de l'application et les algorithmes de planification sont la propriété exclusive de Stradisimo.",
                style=me.Style(color=st.COLOR_TEXT, line_height="1.5", font_size="0.9rem")
            )

        # FOOTER CGU
        with me.box(style=me.Style(
            margin=me.Margin(top=30), 
            padding=me.Padding(top=20),
            border=me.Border(top=me.BorderSide(width=1, color="rgba(255,255,255,0.05)")),
            text_align="center"
        )):
            me.text("Stradisimo Analytics - Performance & Privacy", 
                    style=me.Style(color=st.COLOR_PRIMARY, opacity=0.4, font_size="0.75rem", font_weight="bold"))