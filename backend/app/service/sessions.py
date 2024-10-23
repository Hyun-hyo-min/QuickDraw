from datetime import datetime, timedelta


async def update_session_expiration(session_data):
    expires_at = datetime.fromisoformat(session_data["expires_at"])
    expires_at += timedelta(minutes=10)
    session_data["expires_at"] = expires_at.isoformat()


async def add_player_to_session(session_data, client):
    session_data["players"].append(str(client))
