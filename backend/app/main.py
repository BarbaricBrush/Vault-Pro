from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, sync, data, users
from app.database import engine, Base
from app.config import settings
from apscheduler.schedulers.background import BackgroundScheduler
from app.routers.sync import run_sync_job_logic
import logging
import os

# Initialize DB tables (for MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spending Dashboard API")

# --- CORS ---
origins = list({
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router) # Auth Endpoints (Register/Login)
app.include_router(auth.router)  # TrueLayer Auth
app.include_router(sync.router)
app.include_router(data.router)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_sync_job_logic, 'interval', hours=1)
if os.getenv("DISABLE_SCHEDULER") != "1":
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Banking Dashboard API is running. Go to /docs for Swagger UI."}
