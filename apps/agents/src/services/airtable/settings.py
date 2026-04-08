from pydantic_settings import BaseSettings, SettingsConfigDict


class AirtableSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AIRTABLE_",
        env_file=".env",
        extra="ignore",
    )

    api_key: str = ""
    base_id: str = ""
    po_table: str = "Customer POs"
    items_table: str = "PO Items"
    # Optional Airtable attachment field on Customer POs (e.g. "Attachments")
    attachments_field: str = ""
    # Table/view IDs for building clickable record URLs (avoids needing schema:read scope).
    # Get these from any Airtable record URL: .../appXXX/tblXXX/viwXXX/recXXX
    po_table_id: str = ""
    po_view_id: str = ""
    items_table_id: str = ""
    items_view_id: str = ""
