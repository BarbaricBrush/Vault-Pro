from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.tables import Account, Connection

db = SessionLocal()
try:
    print("Cleaning up orphaned accounts...")
    
    # Get valid connection IDs
    valid_conn_ids = [c.id for c in db.query(Connection).all()]
    print(f"Valid Connections: {valid_conn_ids}")
    
    # Find accounts with invalid connection_ids
    orphans = db.query(Account).filter(Account.connection_id.notin_(valid_conn_ids)).all()
    print(f"Found {len(orphans)} orphaned accounts.")
    
    # Delete them
    if orphans:
        db.query(Account).filter(Account.connection_id.notin_(valid_conn_ids)).delete(synchronize_session=False)
        db.commit()
        print("Deleted orphans.")
        
    # Check remaining count
    count = db.query(Account).count()
    print(f"Remaining valid accounts: {count}")

finally:
    db.close()
