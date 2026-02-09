import mesop as me

@me.stateclass
class State:
    # --- ÉTAT DE SESSION & AUTH ---
    is_logged_in: bool = False
    is_loading: bool = False
    user_id: str = ""           
    email: str = ""             
    password: str = ""          
    
    # --- UI & NAVIGATION ---
    show_password_text: bool = False
    password_confirm: str = ""
    current_page: str = "login" 
    show_signup: bool = False
    active_sub_menu: str = ""  # Gère "Strava" vs "Paramètres"

    # --- MESSAGES DE FEEDBACK ---
    error_message: str = ""     
    success_message: str = ""   

    # --- CONSENTEMENT & LÉGAL ---
    accept_cgu: bool = False    
    has_opened_cgu: bool = False

    # --- LOGIQUE DE FLUX (PROFIL) ---
    is_completing_profile: bool = False 

    # --- DONNÉES UTILISATEUR ---
    prenom: str = ""
    nom: str = ""               
    date_n: str = ""            
    poids: float = 0.0          
    sexe: str = ""              
    niveau: str = "Débutant" 
    sport_pref: str = ""
    vma: float = 15.0
    birth_day: str = ""
    birth_month: str = ""
    birth_year: str = ""

    # --- INTÉGRATION STRAVA ---
    is_strava_linked: bool = False
    strava_access_token: str = ""
    strava_refresh_token: str = ""
    strava_expires_at: int = 0
    last_strava_sync: str = ""
    recent_activities_json: str = "[]" 
    
    # --- GESTION DE LA PAGINATION (POUR ÉVITER LES TIMEOUTS) ---
    # Cette variable permet de reprendre l'import à la page 6, 11, etc.
    # 1 = début, -1 = importation terminée
    strava_import_next_page: int = 1

    # --- Filtres du CV Sportif ---
    cv_filter_year: str = "Toutes"
    cv_filter_type: str = "Tous"