import mesop as me
import styles as st

def cv_screen(s):
    with me.box(style=me.Style(margin=me.Margin(top=20))):
        me.text("PAGE CV SPORTIF", style=st.LOGIN_TITLE_STYLE)
        me.text("Le CV Sportif est en cours de construction...", style=me.Style(font_style="italic"))