# Spending Dashboard MVP

A simple dashboard to track spending using TrueLayer (Sandbox) and Streamlit.

## Prerequisites

- Docker & Docker Compose
- A TrueLayer Console account (Sandbox)

## Setup

1. **TrueLayer Setup**:
   - Go to [TrueLayer Console](https://console.truelayer.com/).
   - Create a Data API Client (Sandbox).
   - Set Redirect URI to `http://localhost:8000/auth/callback`.
   - Copy Client ID and Client Secret.

2. **Environment Variables**:
   - Rename `.env.example` to `.env`.
   - Fill in `TRUELAYER_CLIENT_ID` and `TRUELAYER_CLIENT_SECRET`.
   - Optional: set `JWT_SECRET` (falls back to `ENCRYPTION_KEY` if unset).
   - Optional: set `FRONTEND_URL` (defaults to `http://localhost:3000`).
   - Generate an encryption key:
     ```bash
     python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
     ```
     Paste this into `ENCRYPTION_KEY` in `.env`.

3. **Run**:
   ```bash
   docker-compose up --build
   ```

4. **Usage**:
   - Dashboard: Open [http://localhost:8501](http://localhost:8501)
     - Sign in with a user account to load data (API endpoints require JWT).
   - Click "Connect Bank" in the sidebar.
   - Follow the TrueLayer Sandbox flow (use `user` / `password` or the provided mock credentials).
   - Once connected, click "Trigger Sync" in the sidebar.
   - Refresh the dashboard to see your data.

## Safe Mode
**WARNING**: This application is configured for **SANDBOX** use only.
- Do not use real bank credentials.
- Tokens are encrypted but the setup is not hardened for production.
- Logs are not fully sanitized in this MVP.

## Architecture
- **Backend**: FastAPI (Python 3.12)
- **Database**: Postgres 15
- **Frontend**: Streamlit
- **Job Runner**: APScheduler (in-app)
