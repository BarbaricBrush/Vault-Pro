# Vault Pro (Banking Dashboard) Project Context

Summary
- Web app for banking insights and forecasting.
- UI: Next.js dashboard (primary), Streamlit dashboard (optional).
- API: FastAPI.
- DB: Postgres (Docker/local), SQLite fallback in config.

Structure
- `frontend/`: Next.js app (dashboard, auth, settings).
- `backend/`: FastAPI service.
- `dashboard/`: Streamlit UI.
- `infra/docker-compose.yml`: local dev stack.

Local Dev
- Set env vars in `.env` (see README).
- Run: `docker-compose up --build` from `infra/`.
- URLs: `http://localhost:3000` (frontend), `http://localhost:8000` (API), `http://localhost:8501` (Streamlit).

Auth + Data
- Register at `/register`, login at `/login`.
- API endpoints require JWT.
- TrueLayer OAuth redirect: `/auth/callback`.

Key Env Vars
- `DATABASE_URL`
- `TRUELAYER_CLIENT_ID`
- `TRUELAYER_CLIENT_SECRET`
- `TRUELAYER_REDIRECT_URI`
- `TRUELAYER_AUTH_URL`
- `TRUELAYER_API_URL`
- `TRUELAYER_PROVIDERS`
- `ENCRYPTION_KEY`
- `JWT_SECRET` (optional, falls back to `ENCRYPTION_KEY`)
- `FRONTEND_URL`
- `NEXT_PUBLIC_API_URL` (frontend only)
- `DISABLE_SCHEDULER=1` to disable APScheduler in dev/tests.

Deployment Notes
- Frontend: Vercel.
- Backend: Render/Fly.
- DB: Neon/Supabase.
- Update TrueLayer Console redirect to your live API domain.

Notes
- Sandbox only unless you switch to Live and harden security.
