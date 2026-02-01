import mesop as me
import styles as st
from state import State

def on_back_click(e: me.ClickEvent):
    s = me.state(State)
    if s.is_logged_in:
        s.current_page = "dashboard"
    else:
        s.current_page = "login"

def cgu_screen(s: State):
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
        me.text("CONDITIONS GÉNÉRALES D'UTILISATION", style=st.PAGE_TITLE)
        
        me.text("Date d'entrée en vigueur : 1er Février 2026", 
                style=me.Style(color=st.COLOR_TEXT, opacity=0.5, font_size="0.85rem", margin=me.Margin(bottom=30)))

        # ZONE DE TEXTE (Déroulante)
        with me.box(style=me.Style(
            height=480, 
            overflow_y="scroll",
            padding=me.Padding(right=20)
        )):
            
            # --- SECTION 1 ---
            me.text("1. OBJET DU SERVICE", style=st.PAGE_SUBTITLE)
            me.text(
                "Stradisimo fournit une interface d'analyse de données sportives et de génération de plans d'entraînement personnalisés. L'accès au service est réservé aux personnes physiques majeures pour un usage strictement personnel.",
                style=st.TEXT_NORMAL 
            )
            me.box(style=me.Style(height=25))

            # --- SECTION 2 ---
            me.text("2. AVERTISSEMENT SANTÉ & RESPONSABILITÉ", style=st.PAGE_SUBTITLE)
            me.text(
                "L'utilisation de Stradisimo ne se substitue en aucun cas à un avis médical professionnel. L'utilisateur reconnaît expressément que :",
                style=st.TEXT_NORMAL
            )
            with me.box(style=me.Style(margin=me.Margin(left=15, top=10))):
                me.text("• Il a consulté un médecin et possède un certificat de non-contre-indication à la pratique sportive intensive.", style=st.TEXT_NORMAL)
                me.text("• Stradisimo n'est pas responsable des blessures, pathologies ou accidents survenant lors de l'exécution des séances suggérées.", style=st.TEXT_NORMAL)
                me.text("• Les plans d'entraînement sont des suggestions automatisées basées sur des algorithmes et ne tiennent pas compte de l'état de fatigue réel ou de douleurs soudaines.", style=st.TEXT_NORMAL)
            me.box(style=me.Style(height=25))

            # --- SECTION 3 ---
            me.text("3. PROTECTION DES DONNÉES (RGPD)", style=st.PAGE_SUBTITLE)
            me.text(
                "Conformément au Règlement Général sur la Protection des Données (RGPD), Stradisimo s'engage à protéger la confidentialité de vos informations sportives :",
                style=st.TEXT_NORMAL
            )
            with me.box(style=me.Style(margin=me.Margin(left=15, top=10))):
                me.text("• Finalité : Les données de poids, VMA et niveau servent uniquement au calcul des zones d'intensité.", style=st.TEXT_NORMAL)
                me.text("• Conservation : Vos données sont conservées tant que votre compte est actif. En cas de suppression, toutes vos données physiologiques sont effacées de nos serveurs sous 30 jours.", style=st.TEXT_NORMAL)
                me.text("• Hébergement : Les données sont stockées sur des serveurs sécurisés via la technologie Supabase.", style=st.TEXT_NORMAL)
            me.box(style=me.Style(height=25))

            # --- SECTION 4 ---
            me.text("4. PROPRIÉTÉ INTELLECTUELLE", style=st.PAGE_SUBTITLE)
            me.text(
                "L'architecture de l'application, les algorithmes de planification et les interfaces graphiques sont la propriété exclusive de Stradisimo. Toute reproduction ou extraction de données sans autorisation préalable est interdite.",
                style=st.TEXT_NORMAL
            )
            me.box(style=me.Style(height=25))

            # --- SECTION 5 ---
            me.text("5. MODIFICATION DES CONDITIONS", style=st.PAGE_SUBTITLE)
            me.text(
                "Stradisimo se réserve le droit de modifier les présentes CGU à tout moment. L'utilisation continue du service après notification d'une mise à jour constitue une acceptation des nouvelles conditions.",
                style=st.TEXT_NORMAL
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