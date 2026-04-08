# OpenAI service

- **Settings:** `OpenAISettings` — `OPENAI_API_KEY`, `OPENAI_CLASSIFICATION_MODEL`, `OPENAI_EXTRACTION_MODEL`, `OPENAI_OCR_MODEL`, `OPENAI_MAX_TOKENS`, `OPENAI_TEMPERATURE` (via `OPENAI_` prefix).
- **Client:** `OpenAIClient.chat_completion(..., json_mode=)` and `vision_completion(...)` for PNG data URLs.
- Retries once on `RateLimitError` (2s delay).
