from .client import SupabaseClient, build_search_index, get_client
from .settings import DATABASE_URI, SUPABASE_ENABLED

__all__ = [
    "SupabaseClient",
    "build_search_index",
    "get_client",
    "DATABASE_URI",
    "SUPABASE_ENABLED",
]
