import mesop as me

@me.stateclass
class State:
    # --- ÉTAT DE SESSION & AUTH ---
    is_logged_in: bool = False
    is_loading: bool = False
    user_id: str = ""           # UUID Supabase : sert à filtrer les données (RLS)
    email: str = ""             # Stocke l'email après login pour la réinitialisation PW
    password: str = ""          # Utilisé temporairement lors de la saisie login/signup
    
    # --- NAVIGATION ---
    # dashboard, settings, profile_edit, password_edit, cgu, login
    current_page: str = "login" 
    
    # Bascule entre Login (False) et Signup (True)
    show_signup: bool = False

    # --- MESSAGES DE FEEDBACK (Feedback visuel) ---
    error_message: str = ""     # S'affiche en rouge
    success_message: str = ""   # S'affiche en turquoise (ex: "Email envoyé !")

    # --- CONSENTEMENT & LÉGAL ---
    accept_cgu: bool = False    # Obligatoire pour l'inscription

    # --- LOGIQUE DE FLUX (PROFIL) ---
    # Bloque l'utilisateur sur le formulaire profil s'il est incomplet
    is_completing_profile: bool = False 

    # --- DONNÉES UTILISATEUR (Colonnes table 'profiles') ---
    # Ces variables doivent être mappées lors du chargement initial (fetch)
    prenom: str = ""
    nom: str = ""               
    date_n: str = ""            # Format ISO YYYY-MM-DD
    poids: str = ""
    sexe: str = ""              
    niveau: str = "Débutant" 
    sport_pref: str = ""