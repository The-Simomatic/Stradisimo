# dashboard.py
import mesop as me
import styles as st
import components as cp

def dashboard_screen(s):
    """
    Affiche le tableau de bord avec les cartes de métriques.
    L'état (s) contient les données récupérées depuis Supabase.
    """
    
    # Conteneur principal des cartes
    with me.box(style=st.CARDS_CONTAINER_STYLE):
        
        # Carte Poids (avec ajout de l'unité)
        cp.metric_card(
            label="Poids actuel", 
            value=f"{s.poids} kg"
        )
        
        # Carte Sport principal
        cp.metric_card(
            label="Discipline", 
            value=s.sport
        )
        
        # Carte Niveau
        cp.metric_card(
            label="Niveau", 
            value=s.niveau
        )
        
        # Tu peux facilement ajouter une 4ème carte ici
        cp.metric_card(
            label="Utilisateur", 
            value=s.email.split('@')[0].capitalize() # Affiche le début de l'email
        )