import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sqlalchemy.orm import Session
from app.models.tables import Transaction, Account, Connection
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def analyze_patterns(df):
    """
    Core logic to identify recurring patterns in transaction history.
    Returns:
    1. recurring_groups: List of (name, dataframe_of_txns, frequency_type, next_date, next_amount)
    2. variable_indices: Set of indices that are NOT recurring
    """
    if df.empty:
        return [], set(df.index)

    # Smart Grouping Key
    def get_key(row):
        if row.get('merchant'):
            return str(row['merchant']).lower().strip()
        return str(row.get('description', '')).lower()[:20]

    # Use a copy to avoid SettingWithCopy warnings
    df = df.copy()
    df['key'] = df.apply(get_key, axis=1)
    
    recurring_groups = []
    variable_indices = set(df.index) 
    
    grouped = df.groupby('key')
    
    for name, group in grouped:
        if len(group) < 2: continue
        
        # Sort by date
        group = group.sort_index()
        dates = group.index
        amounts = group['amount']
        
        # 1. Interval Analysis
        gaps = (dates[1:] - dates[:-1]).days
        if len(gaps) == 0: continue
        
        median_gap = np.median(gaps)
        
        # Frequencies
        is_weekly = 6 <= median_gap <= 8
        is_monthly = 26 <= median_gap <= 35
        is_yearly = 360 <= median_gap <= 370
        
        if not (is_weekly or is_monthly or is_yearly):
            continue
            
        # 2. Amount Consistency Analysis
        mean_amt = amounts.mean()
        std_amt = amounts.std()
        
        # Handle zero division
        cv = 0
        if abs(mean_amt) > 0.01:
            cv = std_amt / abs(mean_amt)
            
        is_consistent = (cv < 0.2) or (std_amt < 1.0)
        
        if is_consistent:
            # It's a bill!
            variable_indices -= set(group.index)
            
            # Project Next Occurrence
            last_date = dates[-1]
            last_amount = amounts.iloc[-1]
            
            days_to_add = 0
            if is_weekly: days_to_add = 7
            elif is_monthly: days_to_add = 30 
            elif is_yearly: days_to_add = 365
            
            next_date = last_date + timedelta(days=days_to_add)
            
            recurring_groups.append({
                "name": name,
                "txns": group,
                "frequency": "monthly" if is_monthly else ("weekly" if is_weekly else "yearly"),
                "next_date": next_date,
                "next_amount": last_amount
            })
            
    return recurring_groups, variable_indices

def detect_recurring(df):
    """
    Wrapper for analyze_patterns to return the Future Projection DataFrame
    and the Historical Variable DataFrame (for forecasting).
    """
    recurring_groups, variable_indices = analyze_patterns(df)
    
    # Build Future Projections
    recurring_txns = []
    for g in recurring_groups:
        recurring_txns.append({
            "ds": g['next_date'],
            "amount": g['next_amount'],
            "name": g['name'],
            "frequency": g['frequency']
        })
        
    recurring_future_df = pd.DataFrame(recurring_txns)
    variable_df = df.loc[list(variable_indices)].copy()
    
    return recurring_future_df, variable_df

def classify_transactions(df):
    """
    Returns the dataframe with a new 'classification' column:
    - 'bill': identified as recurring
    - 'income': amount > 0 (simplification)
    - 'variable': everything else
    """
    if df.empty:
        return df
        
    df = df.copy()
    if 'booked_at' in df.columns and not isinstance(df.index, pd.DatetimeIndex):
         df['booked_at'] = pd.to_datetime(df['booked_at'])
         df = df.set_index('booked_at').sort_index()

    # Default to variable
    df['classification'] = 'variable'
    
    # Identify Recurring
    recurring_groups, _ = analyze_patterns(df)
    
    # Mark Recurring IDs
    recurring_ids = set()
    for g in recurring_groups:
        recurring_ids.update(g['txns']['txn_id'].values)
        
    # Apply tags
    # 1. Bills (Recurring)
    df.loc[df['txn_id'].isin(recurring_ids), 'classification'] = 'bill'
    
    # 2. Income (Positive amounts)
    df.loc[df['amount'] > 0, 'classification'] = 'income'
    
    return df

def generate_forecast(db: Session, days_ahead: int = 30, user_id: int | None = None):
    # 1. Fetch History
    query = db.query(Transaction)
    if user_id is not None:
        query = (
            query.join(Account, Transaction.account_id == Account.account_id)
            .join(Connection, Account.connection_id == Connection.id)
            .filter(Connection.user_id == user_id)
        )
    raw_tx = query.all()
    if not raw_tx: return {}

    df = pd.DataFrame([t.__dict__ for t in raw_tx])
    if 'booked_at' not in df.columns:
        return {}
        
    df['booked_at'] = pd.to_datetime(df['booked_at'])
    df = df.set_index('booked_at').sort_index()
    
    # Filter Internal Transfers
    exclude = ['transfer', 'internal', 'save the change', 'credit card payment']
    
    def is_excluded(desc):
        if not desc: return False
        d = desc.lower()
        return any(k in d for k in exclude)

    mask = df['description'].apply(lambda x: not is_excluded(x))
    df = df[mask]

    # 2. Separate Recurring vs Variable
    future_recurring, history_variable = detect_recurring(df)
    
    # 3. Forecast Variable Spend (statsmodels)
    # We forecast the cumulative trend of variable spending
    variable_daily = history_variable['amount'].resample('D').sum().fillna(0).cumsum()
    
    ai_forecast = []
    if len(variable_daily) > 10:
        try:
            # Additive trend is robust for spending accumulation
            model = ExponentialSmoothing(variable_daily, trend='add').fit()
            pred = model.forecast(days_ahead)
            
            # Make relative to 0 start for combining
            start_val = variable_daily.iloc[-1]
            ai_forecast = [{"ds": pred.index[i], "val": v - start_val} for i, v in enumerate(pred)]
        except Exception as e:
            logger.error(f"ETS forecast failed: {e}")
            pass
        
    # 4. Combine
    current_balance = df['amount'].sum()
    final_curve = []
    last_date = df.index[-1]
    
    for i in range(1, days_ahead + 1):
        day = last_date + timedelta(days=i)
        val = current_balance
        
        if ai_forecast and i < len(ai_forecast):
            val += ai_forecast[i-1]['val']
            
        if not future_recurring.empty:
            bills_due = future_recurring[
                (future_recurring['ds'] > last_date) & 
                (future_recurring['ds'] <= day)
            ]
            val += bills_due['amount'].sum()
            
        final_curve.append({"ds": day.isoformat(), "val": val})

    return {
        "net_forecast": final_curve,
    }
