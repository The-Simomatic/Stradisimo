import mesop as me

@me.stateclass
class State:
    # --- ÉTAT DE SESSION & AUTH ---
    is_logged_in: bool = False
    is_loading: bool = False
    user_id: str = ""           
    email: str = ""             
    password: str = ""          
    
    # --- UI & SÉCURITÉ MOT DE PASSE ---
    # Ajout de ces deux variables pour tes nouvelles fonctionnalités
    show_password_text: bool = False  # Bascule pour l'icône "œil"
    password_confirm: str = ""        # Stockage du deuxième champ de vérification
    
    # --- NAVIGATION ---
    current_page: str = "login" 
    show_signup: bool = False

    # --- MESSAGES DE FEEDBACK ---
    error_message: str = ""     
    success_message: str = ""   

    # --- CONSENTEMENT & LÉGAL ---
    accept_cgu: bool = False    

    # --- LOGIQUE DE FLUX (PROFIL) ---
    is_completing_profile: bool = False 

    # --- DONNÉES UTILISATEUR ---
    prenom: str = ""
    nom: str = ""               
    date_n: str = ""            
    poids: str = ""             
    sexe: str = ""              
    niveau: str = "Débutant" 
    sport_pref: str = ""
    vma: float = 15.0