from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Connection(Base):
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for migration, but logic should enforce
    provider = Column(String) # e.g. "mock-payments-gb-redirect" or "barclays"
    user_label = Column(String, nullable=True)
    consent_id = Column(String, unique=True, index=True, nullable=True) # ID from TrueLayer
    refresh_token_enc = Column(String, nullable=True) # Encrypted
    access_token_enc = Column(String, nullable=True) # Encrypted
    status = Column(String) # "active", "expired", "pending"
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(String, primary_key=True) # TrueLayer account_id
    connection_id = Column(Integer, ForeignKey("connections.id"))
    name = Column(String)
    type = Column(String)
    currency = Column(String)
    masked_number = Column(String, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    txn_id = Column(String, primary_key=True) # TrueLayer transaction_id or hash
    account_id = Column(String, ForeignKey("accounts.account_id"))
    booked_at = Column(DateTime)
    amount = Column(Float)
    currency = Column(String)
    description = Column(String)
    merchant = Column(String, nullable=True)
    category = Column(String, default="Uncategorised")
    is_pending = Column(Boolean, default=False)
    raw_json = Column(JSON)

class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("accounts.account_id"))
    as_of = Column(DateTime)
    available = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    raw_json = Column(JSON)

class CategoryRule(Base):
    __tablename__ = "category_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String) # simple contains match
    category = Column(String)

class OAuthState(Base):
    __tablename__ = "oauth_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    state = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
