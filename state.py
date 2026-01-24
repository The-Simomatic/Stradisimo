import mesop as me

@me.stateclass
class State:
    # --- ÉTAT DE SESSION ---
    is_logged_in: bool = False
    is_loading: bool = False
    
    # --- NAVIGATION ---
    # dashboard, planning, cv, settings, cgu
    current_page: str = "dashboard" 
    
    # Bascule entre le formulaire de connexion (False) et d'inscription (True)
    show_signup: bool = False

    # --- AUTHENTIFICATION ---
    email: str = ""
    password: str = ""
    error_message: str = ""
    
    # Consentement obligatoire pour l'inscription
    accept_cgu: bool = False

    # --- DONNÉES UTILISATEUR (Profil) ---
    prenom: str = ""
    poids: str = ""
    sport: str = ""
    niveau: str = ""