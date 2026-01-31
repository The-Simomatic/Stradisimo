import mesop as me

@me.stateclass # <--- Utilise impérativement ceci pour la définition
class State:
    # --- ÉTAT DE SESSION & AUTH ---
    is_logged_in: bool = False
    is_loading: bool = False
    user_id: str = ""           
    email: str = ""             
    password: str = ""          
    
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