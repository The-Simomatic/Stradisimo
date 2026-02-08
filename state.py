import mesop as me
import json

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
    active_sub_menu: str = ""  # NOUVEAU : Pour gérer "Strava" vs "Paramètres" sans bug

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
    poids: float = 0.0          # CORRIGÉ : str -> float pour la cohérence DB
    sexe: str = ""              
    niveau: str = "Débutant" 
    sport_pref: str = ""
    vma: float = 15.0
    birth_day: str = ""
    birth_month: str = ""
    birth_year: str = ""

    # --- INTÉGRATION STRAVA (NOUVEAU) ---
    is_strava_linked: bool = False
    strava_access_token: str = ""
    strava_refresh_token: str = ""
    strava_expires_at: int = 0
    last_strava_sync: str = ""
    recent_activities_json: str = "[]" # On initialise avec un tableau vide en string