# OpenAI setup

> **Prev:** [09_GAS_TRIGGERS.md](09_GAS_TRIGGERS.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [11_AIRTABLE_SETUP.md](11_AIRTABLE_SETUP.md)

1. https://platform.openai.com — billing + API key.
2. Put key in `ROOT/.env`:

```env
OPENAI_API_KEY=sk-...
OPENAI_CLASSIFICATION_MODEL=gpt-4o-mini
OPENAI_EXTRACTION_MODEL=gpt-4o-mini
OPENAI_OCR_MODEL=gpt-4o
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0
```

Restart containers after edits.
