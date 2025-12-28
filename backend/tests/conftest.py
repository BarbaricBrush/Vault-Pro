import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("TRUELAYER_CLIENT_ID", "test-client-id")
os.environ.setdefault("TRUELAYER_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("ENCRYPTION_KEY", "MDEyMzQ1Njc4OUFCQ0RFRjAxMjM0NTY3ODlBQkNERUY=")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("DISABLE_SCHEDULER", "1")
