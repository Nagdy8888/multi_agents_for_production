"""
Load environment variables from the project root .env file.
"""
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required. Set it in the project root .env file.")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
DATABASE_URI = os.getenv("DATABASE_URI")  # optional
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")  # optional
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() in ("true", "1", "yes")
