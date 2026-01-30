import mesop as me

@me.stateclass
class State:
    # --- ÉTAT DE SESSION ---
    is_logged_in: bool = False
    is_loading: bool = False
    user_id: str = "" # Indispensable pour lier l'Auth au Profil [cite: 2026-01-22]
    
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
    # Ces champs correspondent exactement à ta table 'profiles' [cite: 2026-01-22]
    prenom: str = ""
    nom: str = ""            # Ajouté : obligatoire [cite: 2026-01-22]
    date_n: str = ""         # Ajouté : obligatoire [cite: 2026-01-22]
    poids: str = ""
    sexe: str = ""           # Ajouté : pour le formulaire [cite: 2026-01-22]
    niveau: str = "Débutant" # Valeur par défaut
    sport_pref: str = ""     # Renommé pour correspondre à ta base [cite: 2026-01-22]