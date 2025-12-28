import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

# Configuration
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Vault", layout="wide", page_icon="🏦")

# --- THEME STATE ---
# Check URL params first, then session state, then default to 'dark'
query_params = st.query_params
default_theme = query_params.get("theme", "dark")

if 'theme' not in st.session_state:
    st.session_state.theme = default_theme

def toggle_theme():
    new_theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    st.session_state.theme = new_theme
    st.query_params["theme"] = new_theme

# --- DYNAMIC CSS ---
# Define theme colors
if st.session_state.theme == 'light':
    root_vars = """
        --bg-color: #f8fafc;
        --card-bg: #ffffff;
        --sidebar-bg: #f1f5f9;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --accent: #2563eb;
        --success: #059669;
        --danger: #dc2626;
        --border-color: #e2e8f0;
    """
else:
    root_vars = """
        --bg-color: #0f1116;
        --card-bg: #1e212b;
        --sidebar-bg: #0f1116;
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
        --accent: #3b82f6;
        --success: #10b981;
        --danger: #ef4444;
        --border-color: rgba(255,255,255,0.05);
    """

theme_css = f"""
<style>
    /* VARIABLES */
    :root {{
        {root_vars}
    }}

    /* GLOBAL RESET */
    .stApp {{
        background-color: var(--bg-color);
        color: var(--text-primary);
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    
    /* SIDEBAR OVERRIDE */
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }}
    
    /* HIDE STREAMLIT CHROME */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* CARDS */
    .saas-card {{
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }}
    
    /* METRICS */
    .metric-label {{
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }}
    .metric-value {{
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }}
    .metric-delta {{
        font-size: 0.875rem;
        font-weight: 500;
        margin-top: 4px;
    }}
    .delta-pos {{ color: var(--success); }}
    .delta-neg {{ color: var(--danger); }}
    
    /* TABLES */
    div[data-testid="stDataFrame"] {{
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 10px;
    }}
    
    /* TEXT ELEMENTS */
    h1, h2, h3, h4, h5, h6, p, span, div {{
        color: var(--text-primary);
    }}
    .stMarkdown p {{
        color: var(--text-primary) !important;
    }}
</style>
"""

# Inject CSS
st.markdown(theme_css, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
LOGO_MAP = {
    "barclays": "https://ui-avatars.com/api/?name=B&background=00aeef&color=fff&rounded=true&bold=true",
    "natwest": "https://ui-avatars.com/api/?name=N&background=440099&color=fff&rounded=true&bold=true",
    "santander": "https://ui-avatars.com/api/?name=S&background=ec0000&color=fff&rounded=true&bold=true",
    "lloyds": "https://ui-avatars.com/api/?name=L&background=006a4d&color=fff&rounded=true&bold=true",
    "hsbc": "https://ui-avatars.com/api/?name=H&background=db0011&color=fff&rounded=true&bold=true",
    "monzo": "https://ui-avatars.com/api/?name=M&background=14233c&color=fff&rounded=true&bold=true",
    "revolut": "https://ui-avatars.com/api/?name=R&background=0075eb&color=fff&rounded=true&bold=true",
    "mock": "https://ui-avatars.com/api/?name=T&background=888888&color=fff&rounded=true&bold=true"
}

def get_logo(provider):
    if not provider: return LOGO_MAP["mock"]
    provider = provider.lower()
    for key, url in LOGO_MAP.items():
        if key in provider: return url
    return LOGO_MAP["mock"]

def get_auth_headers():
    token = st.session_state.get("auth_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def fetch_data(headers=None):
    data = {}
    headers = headers or {}
    
    # Balances
    try:
        data["balances"] = requests.get(f"{API_URL}/api/balances", timeout=2, headers=headers).json()
    except:
        data["balances"] = []
        
    # Summary
    try:
        data["summary"] = requests.get(f"{API_URL}/api/summary/monthly", timeout=2, headers=headers).json()
    except:
        data["summary"] = []
        
    # Transactions
    try:
        data["transactions"] = requests.get(f"{API_URL}/api/transactions", timeout=5, headers=headers).json()
    except:
        data["transactions"] = []
        
    # Connections
    try:
        data["connections"] = requests.get(f"{API_URL}/api/connections", timeout=2, headers=headers).json()
    except:
        data["connections"] = []
        
    return data

# --- NAVIGATION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'Overview'

# --- SIDEBAR ---
with st.sidebar:
    c_logo, c_toggle = st.columns([3, 1])
    with c_logo:
        st.title("💎 Vault")
    with c_toggle:
        # Theme Toggle Button
        btn_txt = "☀️" if st.session_state.theme == 'dark' else "🌙"
        if st.button(btn_txt, key="theme_toggle"):
            toggle_theme()
            st.rerun()

    st.markdown("Your Financial Command Center", help="Switch tabs below to navigate")
    st.divider()

    # Auth
    if "auth_token" not in st.session_state:
        st.markdown("### Sign in")
        email = st.text_input("Email", key="auth_email")
        password = st.text_input("Password", type="password", key="auth_password")
        if st.button("Sign in", use_container_width=True):
            try:
                resp = requests.post(
                    f"{API_URL}/auth/token",
                    data={"username": email, "password": password},
                    timeout=5,
                )
                if resp.ok:
                    st.session_state.auth_token = resp.json().get("access_token")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception:
                st.error("Login failed")
        st.divider()
    else:
        if st.button("Sign out", use_container_width=True):
            del st.session_state["auth_token"]
            st.rerun()
        st.divider()
    
    # Custom Nav Menu
    cols = st.columns(3)
    
    # Navigation Buttons (Simple Icons)
    if st.button("📊 Overview", use_container_width=True, type="primary" if st.session_state.page == 'Overview' else "secondary"):
        st.session_state.page = 'Overview'
        st.rerun()
        
    if st.button("💳 Transactions", use_container_width=True, type="primary" if st.session_state.page == 'Transactions' else "secondary"):
        st.session_state.page = 'Transactions'
        st.rerun()
        
    if st.button("⚙️ Settings", use_container_width=True, type="primary" if st.session_state.page == 'Settings' else "secondary"):
        st.session_state.page = 'Settings'
        st.rerun()
        
    st.divider()
    
    # Sync Action
    if st.button("🔄 Sync Now", use_container_width=True):
        try:
            requests.post(f"{API_URL}/sync/run", timeout=1, headers=get_auth_headers())
            st.toast("Sync started...", icon="🚀")
        except:
            st.warning("Triggered")

auth_headers = get_auth_headers()
if not auth_headers:
    st.info("Sign in to load your data.")
    st.stop()

# --- DATA LOADING ---
data = fetch_data(auth_headers)
balances = data.get("balances", [])
summary = data.get("summary", [])
transactions = data.get("transactions", [])

# --- PAGE: OVERVIEW ---
if st.session_state.page == 'Overview':
    st.markdown("## Overview")
    
    # 1. METRICS ROW
    total_cash = sum(b.get('current', 0) for b in balances)
    
    # Calculate spend delta
    spend_this = 0
    spend_last = 0
    if summary:
        df_sum = pd.DataFrame(summary)
        today = datetime.now()
        this_m = today.strftime("%Y-%m")
        last_m = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        spend_this = df_sum[df_sum['month'] == this_m]['total'].sum()
        spend_last = df_sum[df_sum['month'] == last_m]['total'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="saas-card">
            <div class="metric-label">Net Worth</div>
            <div class="metric-value">£{total_cash:,.2f}</div>
            <div class="metric-delta delta-pos">All Accounts</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        delta_val = spend_this - spend_last
        delta_cls = "delta-neg" if delta_val > 0 else "delta-pos"
        arrow = "⬆" if delta_val > 0 else "⬇"
        st.markdown(f"""
        <div class="saas-card">
            <div class="metric-label">Monthly Spend</div>
            <div class="metric-value">£{spend_this:,.2f}</div>
            <div class="metric-delta {delta_cls}">{arrow} £{abs(delta_val):,.0f} vs last month</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="saas-card">
            <div class="metric-label">Runway</div>
            <div class="metric-value">{(total_cash / (spend_this if spend_this > 0 else 1)):.1f} Mo</div>
            <div class="metric-delta" style="color:var(--text-secondary);">Based on current spend</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("###") # Spacing

    # 2. MAIN GRID (Chart + List)
    c_main, c_side = st.columns([2, 1])
    
    with c_main:
        # CHART
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("##### Financial Projection")
        try:
            forecast_resp = requests.get(f"{API_URL}/api/forecast?days=30", timeout=5, headers=auth_headers)
            f_data = forecast_resp.json()
            
            fig = go.Figure()
            # Net Balance
            if 'net_forecast' in f_data:
                df_net = pd.DataFrame(f_data['net_forecast'])
                line_color = '#3b82f6' if st.session_state.theme == 'dark' else '#2563eb'
                fig.add_trace(go.Scatter(x=df_net['ds'], y=df_net['val'], mode='lines', name='Balance', line=dict(color=line_color, width=3)))
            
            # Determine plotly template based on theme
            plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
            
            fig.update_layout(
                template=plotly_template,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                height=300,
                legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Loading forecast...")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_side:
        # ACCOUNTS LIST
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("##### Accounts")
        border_col = "rgba(255,255,255,0.1)" if st.session_state.theme == 'dark' else "rgba(0,0,0,0.1)"
        
        for bal in balances:
            logo = get_logo(bal.get('provider_id'))
            name = bal.get('provider_id', 'Bank').replace("uk-ob-", "").title()
            amt = bal.get('current', 0)
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid {border_col}; padding-bottom:10px;">
                <div style="display:flex; align-items:center;">
                    <img src="{logo}" style="width:24px; height:24px; border-radius:50%; margin-right:10px;">
                    <span style="font-size:0.9rem; font-weight:500;">{name}</span>
                </div>
                <div style="font-weight:600;">£{amt:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: TRANSACTIONS ---
elif st.session_state.page == 'Transactions':
    st.markdown("## Transactions")
    
    if transactions:
        df = pd.DataFrame(transactions)
        df["Logo"] = df["provider_id"].apply(get_logo)
        
        # Filters
        f1, f2 = st.columns(2)
        with f1:
            search = st.text_input("🔍 Search", placeholder="Netflix, Uber...")
        with f2:
            cats = st.multiselect("Category", options=df['category'].unique())
            
        if search:
            df = df[df['description'].str.contains(search, case=False) | df['merchant'].str.contains(search, case=False)]
        if cats:
            df = df[df['category'].isin(cats)]

        # Styling Logic
        def highlight_row(row):
            c = row.get('classification', 'variable')
            bg = 'transparent'
            
            is_dark = st.session_state.theme == 'dark'
            
            if c == 'bill':
                bg = 'rgba(127, 29, 29, 0.3)' if is_dark else 'rgba(254, 202, 202, 0.4)'
            elif c == 'income':
                bg = 'rgba(6, 78, 59, 0.3)' if is_dark else 'rgba(167, 243, 208, 0.4)'
            elif c == 'variable':
                bg = 'transparent' 
                
            return [f'background-color: {bg}' for _ in row]

        # Columns to display
        display_df = df[["Logo", "booked_at", "description", "amount", "category", "classification"]]
        
        st.dataframe(
            display_df.style.apply(highlight_row, axis=1),
            column_config={
                "Logo": st.column_config.ImageColumn("", width="small"),
                "booked_at": st.column_config.DatetimeColumn("Date", format="D MMM"),
                "amount": st.column_config.NumberColumn("Amount", format="£%.2f"),
                "classification": st.column_config.TextColumn("AI Type", help="Auto-detected by AI"),
            },
            hide_index=True,
            use_container_width=True,
            height=600
        )

# --- PAGE: SETTINGS ---
elif st.session_state.page == 'Settings':
    st.markdown("## Settings")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Manage Connections")
        try:
            conns = data.get("connections", [])
            for c in conns:
                c_id = c["id"]
                name = c.get("provider", "Unknown")
                st.markdown(f"**{name}** (ID: {c_id})")
                if st.button("Revoke Connection", key=f"rev_{c_id}"):
                    requests.delete(f"{API_URL}/api/connections/{c_id}", headers=auth_headers)
                    st.rerun()
        except:
            pass
            
    with c2:
        st.markdown("### Add New Bank")
        try:
            auth_resp = requests.get(f"{API_URL}/auth/start", timeout=5, headers=auth_headers)
            if auth_resp.ok:
                start_url = auth_resp.json().get("url")
                if start_url:
                    st.link_button("Connect via TrueLayer", start_url)
        except:
            st.error("Service unavailable")
