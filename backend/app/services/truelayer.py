import requests
from app.config import settings

def exchange_code(code: str):
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.TRUELAYER_CLIENT_ID,
        "client_secret": settings.TRUELAYER_CLIENT_SECRET,
        "redirect_uri": settings.TRUELAYER_REDIRECT_URI,
        "code": code
    }
    resp = requests.post(f"{settings.TRUELAYER_AUTH_URL}/connect/token", data=data)
    resp.raise_for_status()
    return resp.json()

def refresh_token(refresh_token: str):
    data = {
        "grant_type": "refresh_token",
        "client_id": settings.TRUELAYER_CLIENT_ID,
        "client_secret": settings.TRUELAYER_CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    resp = requests.post(f"{settings.TRUELAYER_AUTH_URL}/connect/token", data=data)
    resp.raise_for_status()
    return resp.json()

def get_accounts(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{settings.TRUELAYER_API_URL}/data/v1/accounts", headers=headers)
    resp.raise_for_status()
    return resp.json()["results"]

def get_balance(access_token: str, account_id: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{settings.TRUELAYER_API_URL}/data/v1/accounts/{account_id}/balance", headers=headers)
    resp.raise_for_status()
    return resp.json()["results"]

def get_transactions(access_token: str, account_id: str, from_date: str, to_date: str):
    # from_date, to_date in YYYY-MM-DD
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"from": from_date, "to": to_date}
    resp = requests.get(f"{settings.TRUELAYER_API_URL}/data/v1/accounts/{account_id}/transactions", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()["results"]

def get_metadata(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{settings.TRUELAYER_API_URL}/data/v1/me", headers=headers)
    resp.raise_for_status()
    return resp.json()["results"]
