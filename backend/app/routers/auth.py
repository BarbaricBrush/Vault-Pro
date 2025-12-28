from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.services import truelayer, crypto
from app.models.tables import Connection, OAuthState
from app.routers.users import get_current_user
import uuid
from datetime import datetime, timedelta

router = APIRouter()

import urllib.parse

OAUTH_STATE_TTL_MINUTES = 10

@router.get("/auth/start")
def auth_start(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Construct TrueLayer auth URL
    client_id = settings.TRUELAYER_CLIENT_ID.strip()
    redirect_uri = settings.TRUELAYER_REDIRECT_URI.strip()
    auth_url = settings.TRUELAYER_AUTH_URL.strip()
    
    scope = "info accounts balance transactions offline_access"
    
    # URL Encode parameters
    state = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=OAUTH_STATE_TTL_MINUTES)
    db.add(OAuthState(user_id=current_user.id, state=state, expires_at=expires_at))
    db.commit()

    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        # Use the provider from settings (allows switching to uk-ob-all for Live)
        "providers": settings.TRUELAYER_PROVIDERS, 
        "state": state
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"{auth_url}/?{query_string}"
    
    return {"url": url}

@router.get("/auth/callback")
def auth_callback(code: str, state: str, db: Session = Depends(get_db), provider: str = "unknown_provider"):
    # Validate state
    oauth_state = db.query(OAuthState).filter(OAuthState.state == state).first()
    if not oauth_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    if oauth_state.expires_at and oauth_state.expires_at < datetime.utcnow():
        db.delete(oauth_state)
        db.commit()
        raise HTTPException(status_code=400, detail="Expired OAuth state")

    # Exchange code
    try:
        tokens = truelayer.exchange_code(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # If provider wasn't in callback params, try metadata, otherwise keep what we have
    final_provider_id = provider
    if final_provider_id == "unknown_provider":
         try:
            meta = truelayer.get_metadata(tokens["access_token"])
            final_provider_id = meta.get("provider_id", "unknown")
         except:
            pass

    # Store connection
    conn = Connection(
        user_id=oauth_state.user_id,
        provider=final_provider_id,
        access_token_enc=crypto.encrypt(tokens["access_token"]),
        refresh_token_enc=crypto.encrypt(tokens["refresh_token"]),
        status="active",
        # expires_in is usually 3600 (1h)
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    db.delete(oauth_state)
    db.commit()
    
    # Redirect back to Frontend
    return RedirectResponse(f"{settings.FRONTEND_URL}/settings?success=true")
