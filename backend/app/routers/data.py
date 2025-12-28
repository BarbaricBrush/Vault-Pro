from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from datetime import date, datetime
import pandas as pd

from app.database import get_db
from app.models.tables import Transaction, Account, Connection, Balance
from app.schemas import TransactionOut, BalanceOut, ConnectionOut
from app.services import forecasting
from app.routers.users import get_current_user

router = APIRouter()

@router.get("/api/balances", response_model=List[BalanceOut])
def get_balances(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    accounts = (
        db.query(Account, Connection.provider)
        .join(Connection, Account.connection_id == Connection.id)
        .filter(Connection.user_id == current_user.id)
        .all()
    )

    out = []
    for acc, provider in accounts:
        latest_bal = (
            db.query(Balance)
            .filter(Balance.account_id == acc.account_id)
            .order_by(Balance.as_of.desc())
            .first()
        )

        out.append(
            {
                "account_id": acc.account_id,
                "account_name": acc.name,
                "provider_id": provider,
                "currency": acc.currency,
                "current": latest_bal.current if latest_bal else 0.0,
                "available": latest_bal.available if latest_bal else 0.0,
                "updated_at": latest_bal.as_of if latest_bal else datetime.now(),
            }
        )
    return out

@router.get("/api/connections", response_model=List[ConnectionOut])
def get_connections(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Connection).filter(Connection.user_id == current_user.id).all()

@router.get("/api/forecast")
def get_forecast(days: int = 30, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Returns predicted cumulative balance/spend trend for the next N days.
    """
    return forecasting.generate_forecast(db, days_ahead=days, user_id=current_user.id)

@router.delete("/api/connections/{connection_id}")
def delete_connection(
    connection_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    conn = (
        db.query(Connection)
        .filter(Connection.id == connection_id, Connection.user_id == current_user.id)
        .first()
    )
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    db.query(Account).filter(Account.connection_id == connection_id).delete()
    db.delete(conn)
    db.commit()
    return {"status": "deleted"}

@router.get("/api/transactions", response_model=List[TransactionOut])
def get_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = (
        db.query(
            Transaction,
            Account.name.label("account_name"),
            Connection.provider.label("provider_id"),
        )
        .join(Account, Transaction.account_id == Account.account_id)
        .join(Connection, Account.connection_id == Connection.id)
        .filter(Connection.user_id == current_user.id)
    )

    if start_date:
        query = query.filter(Transaction.booked_at >= start_date)
    if end_date:
        query = query.filter(Transaction.booked_at <= end_date)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    results = query.order_by(Transaction.booked_at.desc()).limit(1000).all()

    if not results:
        return []

    data = []
    for txn, acc_name, prov_id in results:
        t_dict = txn.__dict__.copy()
        t_dict["account_name"] = acc_name
        t_dict["provider_id"] = prov_id
        data.append(t_dict)

    df = pd.DataFrame(data)
    df_classified = forecasting.classify_transactions(df)

    if isinstance(df_classified.index, pd.DatetimeIndex) and "booked_at" not in df_classified.columns:
        df_classified = df_classified.reset_index()

    out = df_classified.to_dict(orient="records")
    return out

@router.get("/api/summary/monthly")
def get_monthly_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    results = (
        db.query(
            func.to_char(Transaction.booked_at, "YYYY-MM").label("month"),
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
        )
        .join(Account, Transaction.account_id == Account.account_id)
        .join(Connection, Account.connection_id == Connection.id)
        .filter(Connection.user_id == current_user.id)
        .group_by("month", Transaction.category)
        .order_by(text("month DESC"))
        .all()
    )

    return [{"month": r.month, "category": r.category, "total": r.total} for r in results]
