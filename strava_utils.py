import requests
import time
from datetime import datetime, timezone, timedelta
import supabase_db as db  # Ton module de base de données
from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET  # Import de tes secrets

def refresh_strava_token_if_needed(user_id: str, state):
    """
    Vérifie si le token expire bientôt et le rafraîchit si nécessaire.
    Met à jour la base de données et l'état Mesop (State).
    C'est la clé pour que l'utilisateur n'ait jamais à se reconnecter.
    """
    current_time = int(time.time())
    
    # On rafraîchit si le token expire dans moins de 10 minutes (600 secondes)
    # ou s'il est déjà expiré.
    if state.strava_expires_at - current_time < 600:
        print(f"🔄 Rafraîchissement du token Strava pour l'utilisateur {user_id}...")
        
        payload = {
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'refresh_token': state.strava_refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            res = requests.post("https://www.strava.com/oauth/token", data=payload)
            if res.status_code == 200:
                new_data = res.json()
                
                # 1. Mise à jour du State Mesop pour l'immédiateté
                state.strava_access_token = new_data['access_token']
                state.strava_refresh_token = new_data['refresh_token']
                state.strava_expires_at = new_data['expires_at']
                
                # 2. Sauvegarde en base de données Supabase pour la persistance long terme
                profile_update = {
                    "strava_access_token": new_data['access_token'],
                    "strava_refresh_token": new_data['refresh_token'],
                    "strava_expires_at": new_data['expires_at']
                }
                db.update_profile(user_id, profile_update)
                print("✅ Token Strava renouvelé avec succès.")
                return True
            else:
                print(f"❌ Erreur Strava ({res.status_code}): {res.text}")
                return False
        except Exception as e:
            print(f"❌ Exception lors du rafraîchissement Strava : {e}")
            return False
            
    return True # Le token est encore valide

def sync_latest_activities(user_id: str, state):
    """
    Récupère les dernières activités Strava et les synchronise en base de données.
    Utilise le token rafraîchi automatiquement.
    """
    # Étape cruciale : on s'assure d'avoir un token valide avant l'appel API
    if not refresh_strava_token_if_needed(user_id, state):
        return False
    
    headers = {'Authorization': f'Bearer {state.strava_access_token}'}
    params = {'per_page': 30} # On récupère les 30 dernières par exemple
    
    try:
        res = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params=params)
        if res.status_code == 200:
            activities = res.json()
            if not activities:
                return True
            
            # Préparation des données pour l'upsert dans Supabase
            batch_data = []
            for act in activities:
                batch_data.append({
                    "user_id": user_id,
                    "strava_id": str(act['id']),
                    "name": act['name'],
                    "type": act['type'],
                    "distance": round(act['distance'] / 1000, 2), # km
                    "start_date": act['start_date_local'],
                    "moving_time": act.get('moving_time', 0),
                    "total_elevation_gain": act.get('total_elevation_gain', 0),
                    "average_heartrate": act.get('average_heartrate', 0),
                    "gear_id": act.get('gear_id')
                })
            
            # Appel à ta fonction DB pour sauvegarder (avec on_conflict sur strava_id)
            # db.upsert_activities(batch_data) 
            
            # Mise à jour du timestamp de dernière synchro
            now_iso = datetime.now(timezone.utc).isoformat()
            db.update_profile(user_id, {"last_strava_sync": now_iso})
            state.last_strava_sync = now_iso
            
            return True
    except Exception as e:
        print(f"❌ Erreur lors de la synchro des activités : {e}")
        return False
    return False

def get_strava_auth_url(redirect_uri: str):
    """Génère l'URL pour la première connexion (OAuth)."""
    import urllib.parse
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read,activity:read_all",
        "approval_prompt": "auto"
    }
    return f"https://www.strava.com/oauth/authorize?{urllib.parse.urlencode(params)}"

# --- FONCTION DE CONTRÔLE DE FLUX ---
def sync_if_needed(user_id: str, state):
    """
    Lance la synchro seulement si la dernière date de synchro est vieille de plus d'une heure.
    Cela évite de saturer l'API Strava et de ralentir l'appli inutilement.
    """
    # Si on n'a jamais synchronisé (première connexion)
    if not state.last_strava_sync:
        print("Première synchronisation Strava...")
        return sync_latest_activities(user_id, state)
        
    try:
        # On nettoie la date (cas des 'Z' de Supabase) et on compare
        dt_str = state.last_strava_sync.replace('Z', '+00:00')
        last_sync = datetime.fromisoformat(dt_str)
        
        if datetime.now(timezone.utc) - last_sync > timedelta(hours=1):
            print("Plus d'une heure depuis la dernière synchro, mise à jour...")
            return sync_latest_activities(user_id, state)
        else:
            print("Synchro Strava récente, pas besoin de mise à jour.")
            
    except Exception as e:
        print(f"Erreur lors du calcul du délai de synchro: {e}")
        # En cas de doute, on synchronise
        return sync_latest_activities(user_id, state)
    
    return False