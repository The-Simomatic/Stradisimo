import mesop as me
import styles as st

def planning_screen(s): 
    # Utilisation du conteneur standard pour le centrage
    with me.box(style=st.CONTENT_CONTAINER):
        
        # Utilisation du style de titre de page officiel
        me.text("PLANNING", style=st.PAGE_TITLE_STYLE)
        
        # Petit message d'attente stylisé
        with me.box(style=me.Style(margin=me.Margin(top=20), text_align="center")):
            me.icon(icon="construction", style=me.Style(color=st.COLOR_PRIMARY, font_size=40))
            me.text(
                "Le planning d'entraînement est en cours de construction...", 
                style=me.Style(font_style="italic", opacity=0.7, margin=me.Margin(top=10))
            )