"""Supabase/PostgreSQL settings. Load from project root .env."""
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI", "").strip()
SUPABASE_ENABLED = bool(DATABASE_URI)
