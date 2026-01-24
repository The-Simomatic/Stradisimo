import mesop as me
import styles as st

# Ajoute 's' ici entre les parenthèses
def planning_screen(s): 
    with me.box(style=me.Style(margin=me.Margin(top=20))):
        me.text("PAGE PLANNING", style=st.LOGIN_TITLE_STYLE)
        me.text("Le planning est en cours de construction...", style=me.Style(font_style="italic"))