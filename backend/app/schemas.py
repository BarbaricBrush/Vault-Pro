from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Data Schemas ---
class TransactionOut(BaseModel):
    txn_id: str
    account_id: str
    booked_at: datetime
    amount: float
    currency: str
    description: str
    merchant: Optional[str]
    category: str
    provider_id: Optional[str] = None
    account_name: Optional[str] = None
    classification: Optional[str] = "variable" # 'bill', 'income', 'variable'
    
    class Config:
        from_attributes = True

class MonthlySummary(BaseModel):
    month: str
    category: str
    total: float

class BalanceOut(BaseModel):
    account_id: str
    account_name: str
    provider_id: str
    currency: str
    current: Optional[float]
    available: Optional[float]
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ConnectionOut(BaseModel):
    id: int
    provider: Optional[str]
    status: str
    created_at: datetime
    user_label: Optional[str] = None

    class Config:
        from_attributes = True
