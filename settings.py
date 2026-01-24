import mesop as me
import styles as st

# Ajoute 's' ici entre les parenthèses
def settings_screen(s): 
    with me.box(style=me.Style(margin=me.Margin(top=20))):
        me.text("PAGE PARAMÈTRES", style=st.LOGIN_TITLE_STYLE)
        me.text("Les paramètres sont en cours de construction...", style=me.Style(font_style="italic"))