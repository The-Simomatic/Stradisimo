import mesop as me
import styles as st

def cv_screen(s):
    # Utilisation du conteneur standard pour le centrage et la largeur
    with me.box(style=st.CONTENT_CONTAINER):
        
        # Titre avec le style officiel (Kanit, Orange)
        me.text("CV SPORTIF", style=st.PAGE_TITLE_STYLE)
        
        # Zone de contenu temporaire
        with me.box(style=me.Style(margin=me.Margin(top=20), text_align="center")):
            me.icon(icon="assignment_ind", style=me.Style(color=st.COLOR_PRIMARY, font_size=40))
            me.text(
                "Votre palmarès et vos records arrivent bientôt...", 
                style=me.Style(font_style="italic", opacity=0.7, margin=me.Margin(top=10))
            )