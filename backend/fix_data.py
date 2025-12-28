from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.tables import Connection, Account, Transaction
from sqlalchemy import text

# Create a session
db = SessionLocal()

try:
    print("Fixing missing provider_ids...")
    
    # Get all connections
    connections = db.query(Connection).all()
    
    for conn in connections:
        print(f"Processing Connection: {conn.provider} (ID: {conn.id})")
        
        # Get all accounts for this connection
        accounts = db.query(Account).filter(Account.connection_id == conn.id).all()
        
        for acc in accounts:
            # Update transactions for this account to have the connection's provider
            # Note: In our previous schema, Transaction didn't have provider_id column explicitly saved
            # BUT our join query depends on Connection.provider being populated.
            
            # Check if Connection.provider is populated
            if not conn.provider:
                # If we don't have it, we can't fix it easily without re-auth.
                # But typically TrueLayer saves it.
                print(f"  WARNING: Connection {conn.id} has no provider string!")
            else:
                print(f"  Account {acc.account_id} belongs to provider {conn.provider}")
                
    # Check if the query itself is working
    # The issue might be that Connection.provider is NULL in the database
    
    result = db.execute(text("SELECT id, provider FROM connections")).fetchall()
    print("\nCURRENT DATABASE STATE:")
    for r in result:
        print(f"Connection ID: {r[0]}, Provider: {r[1]}")

finally:
    db.close()
