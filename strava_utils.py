import requests
import time
from datetime import datetime, timezone, timedelta
import os
import supabase_db as db
from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET

# ==================================================
# 1. GESTION DES TOKENS (AUTH)
# ==================================================

def exchange_code_for_token(code: str):
    """Échange le code d'autorisation reçu contre des jetons d'accès."""
    payload = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    try:
        res = requests.post("https://www.strava.com/oauth/token", data=payload)
        if res.status_code == 200:
            return res.json()
        print(f"Erreur Token Exchange: {res.text}")
        return None
    except Exception as e:
        print(f"Exception Token Exchange: {e}")
        return None

def refresh_strava_token_if_needed(user_id: str, s):
    """Vérifie l'expiration et rafraîchit le token si nécessaire (< 10 min)."""
    # On récupère les infos fraîches de la DB pour être sûr
    profile, _ = db.get_user_profile(user_id)
    if not profile: return False
    
    expires_at = profile.get("strava_expires_at", 0)
    refresh_token = profile.get("strava_refresh_token")
    current_time = int(time.time())

    # S'il reste moins de 10 min (600s) ou si expiré
    if expires_at and (expires_at - current_time) < 600:
        print("🔄 Le token Strava expire bientôt, rafraîchissement...")
        payload = {
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        try:
            res = requests.post("https://www.strava.com/oauth/token", data=payload)
            if res.status_code == 200:
                new_data = res.json()
                # Mise à jour DB
                db.update_profile(user_id, {
                    "strava_access_token": new_data['access_token'],
                    "strava_refresh_token": new_data['refresh_token'],
                    "strava_expires_at": new_data['expires_at']
                })
                # Mise à jour State
                s.strava_access_token = new_data['access_token']
                s.strava_refresh_token = new_data['refresh_token']
                s.strava_expires_at = new_data['expires_at']
                return True
        except Exception as e:
            print(f"Erreur Refresh: {e}")
            return False
            
    # Si le token est encore bon, on met à jour le state pour être sûr
    s.strava_access_token = profile.get("strava_access_token")
    return True

# ==================================================
# 2. TRAITEMENT DES DONNÉES (LOGIQUE MÉTIER)
# ==================================================

def _format_activity_for_db(user_id: str, act: dict) -> dict:
    """Transforme la donnée brute Strava au format exact de ta DB (Logique 'Old App')."""
    return {
        "user_id": user_id,
        "strava_id": int(act['id']),  # Converti en int car ta DB attend un bigint
        "external_id": act.get('external_id'),
        "name": act.get('name', 'Sans titre'),
        "type": act.get('type'),
        "distance": round(act.get('distance', 0) / 1000, 2),
        "start_date": act.get('start_date_local', '')[:10],
        
        # --- AJOUTS ET CORRECTIONS ---
        "elapsed_time": float(act.get('elapsed_time', 0)), # Ta nouvelle colonne (double precision)
        "moving_time": int(act.get('moving_time', 0)),    # bigint
        "total_elevation_gain": float(act.get('total_elevation_gain', 0)),
        "elev_high": float(act.get('elev_high', 0)),
        "average_heartrate": float(act.get('average_heartrate', 0)),
        "max_heartrate": float(act.get('max_heartrate', 0)),
        "average_speed": float(act.get('average_speed', 0)),
        "max_speed": float(act.get('max_speed', 0)),
        "average_cadence": float(act.get('average_cadence', 0)),
        "average_watts": float(act.get('average_watts', 0)),
        "kilojoules": float(act.get('kilojoules', 0)),
        "suffer_score": float(act.get('suffer_score', 0)),
        "kudos_count": int(act.get('kudos_count', 0)),
        "device_name": act.get('device_name'),
        "start_latlng": act.get('start_latlng'), # Array double precision[]
        "end_latlng": act.get('end_latlng'),     # Array double precision[]
        "gear_id": act.get('gear_id')
    }

# ==================================================
# 3. SYNCHRONISATION
# ==================================================

def sync_latest_activities(user_id: str, s):
    """Récupère les 30 dernières activités (Synchro rapide)."""
    token = s.strava_access_token
    if not token: return False

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        res = requests.get(url, headers=headers, params={'per_page': 30})
        if res.status_code == 200:
            activities = res.json()
            if not activities: return True
            
            batch_data = [_format_activity_for_db(user_id, act) for act in activities]
            
            # Envoi en DB
            db.upsert_activities(batch_data)
            
            # Update date de synchro
            db.update_profile(user_id, {"last_strava_sync": datetime.now(timezone.utc).isoformat()})
            return True
        else:
            print(f"Erreur API Strava: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Erreur Sync: {e}")
    return False

def import_complete_history(user_id: str, s):
    """Importe TOUT l'historique (boucle pagination). Attention: peut être long."""
    token = s.strava_access_token
    if not token: return 0

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {token}'}
    
    page = 1
    total_imported = 0
    per_page = 200 # Max autorisé par Strava par page
    
    while True:
        print(f"📥 Importation page {page}...")
        try:
            res = requests.get(url, headers=headers, params={'per_page': per_page, 'page': page})
            if res.status_code != 200:
                print(f"Arrêt prématuré : {res.status_code}")
                break
            
            activities = res.json()
            if not activities: # Liste vide = fin de l'historique
                break
                
            batch_data = [_format_activity_for_db(user_id, act) for act in activities]
            db.upsert_activities(batch_data)
            
            total_imported += len(activities)
            page += 1
            time.sleep(0.5) # On fait une pause de 500ms entre chaque page de 200
            
        except Exception as e:
            print(f"Erreur durant l'import massif: {e}")
            break
            
    # Update date de synchro finale
    db.update_profile(user_id, {"last_strava_sync": datetime.now(timezone.utc).isoformat()})
    return total_imported