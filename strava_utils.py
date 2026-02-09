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
        print(f"❌ [LOG] Erreur Token Exchange: {res.text}")
        return None
    except Exception as e:
        print(f"❌ [LOG] Exception Token Exchange: {e}")
        return None

def refresh_strava_token_if_needed(user_id: str, s):
    """Vérifie l'expiration et rafraîchit le token si nécessaire (< 10 min)."""
    profile, _ = db.get_user_profile(user_id)
    if not profile: return False
    
    expires_at = profile.get("strava_expires_at", 0)
    refresh_token = profile.get("strava_refresh_token")
    current_time = int(time.time())

    if expires_at and (expires_at - current_time) < 600:
        print("🔄 [LOG] Le token Strava expire bientôt, rafraîchissement...")
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
                db.update_profile(user_id, {
                    "strava_access_token": new_data['access_token'],
                    "strava_refresh_token": new_data['refresh_token'],
                    "strava_expires_at": new_data['expires_at']
                })
                s.strava_access_token = new_data['access_token']
                s.strava_refresh_token = new_data['refresh_token']
                s.strava_expires_at = new_data['expires_at']
                return True
        except Exception as e:
            print(f"❌ [LOG] Erreur Refresh: {e}")
            return False
            
    s.strava_access_token = profile.get("strava_access_token")
    return True

# ==================================================
# 2. TRAITEMENT DES DONNÉES (LOGIQUE MÉTIER)
# ==================================================

def _format_activity_for_db(user_id: str, act: dict) -> dict:
    """Transforme la donnée brute Strava au format exact de ta DB."""
    return {
        "user_id": user_id,
        "strava_id": int(act['id']),
        "external_id": act.get('external_id'),
        "name": act.get('name', 'Sans titre'),
        "type": act.get('type'),
        "distance": round(act.get('distance', 0) / 1000, 2),
        "start_date": act.get('start_date_local', '')[:10],
        "elapsed_time": float(act.get('elapsed_time', 0)),
        "moving_time": int(act.get('moving_time', 0)),
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
        "start_latlng": act.get('start_latlng'),
        "end_latlng": act.get('end_latlng'),
        "gear_id": act.get('gear_id')
    }

# ==================================================
# 3. SYNCHRONISATION
# ==================================================

def sync_recent_activities(user_id: str, s):
    """Récupère uniquement les activités manquantes depuis la dernière date en base."""
    print("🚀 [LOG] DÉBUT SYNCHRO DES MANQUANTES")
    token = s.strava_access_token
    if not token: return 0

    # Récupération du timestamp de la dernière activité (nécessite db.get_last_activity_timestamp)
    last_ts = db.get_last_activity_timestamp(user_id)
    
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {token}'}
    params = {'after': last_ts, 'per_page': 100} 
    
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            activities = res.json()
            if not activities:
                print("⚠️ [LOG] Aucune nouvelle activité trouvée.")
                return 0
            
            batch_data = [_format_activity_for_db(user_id, act) for act in activities]
            db.upsert_activities(batch_data)
            db.update_profile(user_id, {"last_strava_sync": datetime.now(timezone.utc).isoformat()})
            
            print(f"✅ [LOG] Fin synchro rapide : {len(activities)} activités ajoutées.")
            return len(activities)
        else:
            print(f"❌ [LOG] Erreur API Strava: {res.status_code}")
            return 0
    except Exception as e:
        print(f"❌ [LOG] Erreur Sync Récente: {e}")
        return 0

def import_complete_history(user_id: str, s, max_pages=5):
    """Importe l'historique Strava par blocs avec logs de début et de fin."""
    print(f"🚀 [LOG] DÉBUT IMPORT COMPLET - Page de départ: {s.strava_import_next_page}")
    token = s.strava_access_token
    if not token: 
        print("❌ [LOG] Annulation : Pas de token.")
        return

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {token}'}
    current_page = s.strava_import_next_page
    total_imported = 0
    pages_processed = 0
    per_page = 200 

    while pages_processed < max_pages:
        print(f"📥 [LOG] Requête Strava : Page {current_page}...")
        try:
            res = requests.get(url, headers=headers, params={'per_page': per_page, 'page': current_page})
            
            if res.status_code != 200:
                print(f"⚠️ [LOG] Arrêt API : Code {res.status_code}")
                break
            
            activities = res.json()
            if not activities: 
                print("🏁 [LOG] Fin de l'historique Strava atteinte.")
                s.strava_import_next_page = -1 
                break
                
            batch_data = [_format_activity_for_db(user_id, act) for act in activities]
            db.upsert_activities(batch_data)
            
            total_imported += len(activities)
            print(f"✅ [LOG] Page {current_page} traitée (+{len(activities)} act.)")
            
            current_page += 1
            pages_processed += 1
            s.strava_import_next_page = current_page
            
            yield total_imported
            time.sleep(0.6) 
            
        except Exception as e:
            print(f"❌ [LOG] Erreur critique durant l'import : {e}")
            break
            
    db.update_profile(user_id, {"last_strava_sync": datetime.now(timezone.utc).isoformat()})
    print(f"✅ [LOG] FIN DU BLOC D'IMPORT. Total récupéré : {total_imported}")