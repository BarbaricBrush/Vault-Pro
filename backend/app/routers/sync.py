from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models.tables import Connection, Account, Transaction, Balance, CategoryRule
from app.services import truelayer, crypto
from datetime import datetime, timedelta
import logging
from typing import Optional
from app.routers.users import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

def run_sync_job_logic(user_id: Optional[int] = None):
    # Independent session for background task
    db = SessionLocal()
    try:
        query = db.query(Connection).filter(Connection.status == "active")
        if user_id is not None:
            query = query.filter(Connection.user_id == user_id)
        connections = query.all()
        for conn in connections:
            try:
                # Decrypt tokens
                refresh_token = crypto.decrypt(conn.refresh_token_enc)
                
                # Refresh token
                new_tokens = truelayer.refresh_token(refresh_token)
                access_token = new_tokens["access_token"]
                
                # Update tokens
                conn.access_token_enc = crypto.encrypt(access_token)
                conn.refresh_token_enc = crypto.encrypt(new_tokens["refresh_token"])
                db.commit()
                
                # Fetch Accounts
                accounts_data = truelayer.get_accounts(access_token)
                
                # Update Connection Provider if unknown
                if accounts_data and (not conn.provider or conn.provider == "unknown" or conn.provider == "unknown_provider"):
                    # Try to find provider info in account payload
                    first_acc = accounts_data[0]
                    # TrueLayer often nests it or we can derive it
                    # But simpler: if we have accounts, update provider from metadata if available there
                    # Actually, let's just save the provider_id if it exists in the account object
                    p_id = first_acc.get("provider", {}).get("provider_id")
                    if p_id:
                        conn.provider = p_id
                        db.commit()

                for acc in accounts_data:
                    # Upsert account
                    account = db.query(Account).filter(Account.account_id == acc["account_id"]).first()
                    if not account:
                        account = Account(
                            account_id=acc["account_id"],
                            connection_id=conn.id,
                            name=acc["display_name"],
                            type=acc["account_type"],
                            currency=acc["currency"],
                            masked_number=acc.get("account_number", {}).get("swift_bic", "") # Simplified
                        )
                        db.add(account)
                    
                    # Fetch Balance
                    balances = truelayer.get_balance(access_token, acc["account_id"])
                    if balances:
                        b = balances[0]
                        bal = Balance(
                            account_id=acc["account_id"],
                            as_of=datetime.fromisoformat(b["update_timestamp"].replace("Z", "+00:00")),
                            available=b.get("available"),
                            current=b.get("current"),
                            raw_json=b
                        )
                        db.add(bal)

                    # Fetch Transactions
                    # Default to 3 months if no history, else from last sync minus overlap buffer
                    to_date = datetime.now()
                    from_date = to_date - timedelta(days=90)
                    
                    if account.last_sync_at:
                        # Overlap by 7 days to catch delayed/settled transactions
                        from_date = account.last_sync_at - timedelta(days=7)
                    
                    # Fetch
                    txns = truelayer.get_transactions(
                        access_token, 
                        acc["account_id"], 
                        from_date.strftime("%Y-%m-%d"), 
                        to_date.strftime("%Y-%m-%d")
                    )
                    
                    for t in txns:
                        # De-dup by ID
                        if db.query(Transaction).filter(Transaction.txn_id == t["transaction_id"]).first():
                            continue
                            
                        # Categorise (Keyword Matcher)
                        cat = "Uncategorised"
                        desc_lower = (t.get("description") or "").lower()
                        merchant_lower = (t.get("merchant_name") or "").lower()
                        combined = f"{desc_lower} {merchant_lower}"
                        
                        # Simple Rules Engine
                        rules = {
                            "Groceries": ["tesco", "sainsbury", "asda", "aldi", "lidl", "waitrose", "morrisons", "co-op"],
                            "Transport": ["uber", "train", "bus", "tfl", "petrol", "shell", "bp ", "esso", "parking"],
                            "Eating Out": ["restaurant", "cafe", "coffee", "starbucks", "costa", "pret", "mcdonalds", "kfc", "nandos", "deliveroo", "eats"],
                            "Entertainment": ["netflix", "spotify", "cinema", "odeon", "prime video", "disney", "ticketmaster"],
                            "Shopping": ["amazon", "ebay", "asos", "zara", "boots", "argos", "apple"],
                            "Bills": ["council tax", "water", "gas", "electricity", "energy", "virgin media", "bt ", "sky ", "vodafone", "o2", "ee "],
                            "Income": ["salary", "payroll", "dividend", "interest"],
                            "Transfers": ["transfer", "amex", "credit card", "save the change", "paypal"]
                        }
                        
                        found = False
                        for category, keywords in rules.items():
                            if any(k in combined for k in keywords):
                                cat = category
                                found = True
                                break
                        
                        # Fallback to TrueLayer if no keyword match
                        if not found and t.get("transaction_classification"):
                             cat = t["transaction_classification"][0] # Use provider category
                        
                        new_txn = Transaction(
                            txn_id=t["transaction_id"],
                            account_id=acc["account_id"],
                            booked_at=datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00")),
                            amount=t["amount"],
                            currency=t["currency"],
                            description=t["description"],
                            merchant=t.get("merchant_name"),
                            category=cat,
                            raw_json=t
                        )
                        db.add(new_txn)
                    
                    account.last_sync_at = to_date
                    db.commit()

            except Exception as e:
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Error syncing connection {conn.id}: {e.response.status_code} {e.response.text}")
                else:
                    logger.error(f"Error syncing connection {conn.id}: {e}")
                continue
    finally:
        db.close()

@router.post("/sync/run")
def trigger_sync(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    background_tasks.add_task(run_sync_job_logic, current_user.id)
    return {"status": "Sync started"}
