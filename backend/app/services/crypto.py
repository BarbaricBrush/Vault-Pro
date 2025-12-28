from cryptography.fernet import Fernet
from app.config import settings

raw_key = settings.ENCRYPTION_KEY
key = raw_key.encode() if isinstance(raw_key, str) else raw_key

try:
    f = Fernet(key)
except Exception as e:
    raise RuntimeError("Invalid ENCRYPTION_KEY; must be a urlsafe base64-encoded 32-byte key.") from e

def encrypt(data: str) -> str:
    if not data: return None
    return f.encrypt(data.encode()).decode()

def decrypt(token: str) -> str:
    if not token: return None
    return f.decrypt(token.encode()).decode()
