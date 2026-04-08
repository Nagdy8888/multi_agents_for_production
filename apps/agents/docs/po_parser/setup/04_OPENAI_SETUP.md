# OpenAI setup

**When:** Phase 2+ (real LangGraph pipeline — not required for Phase 1.5 mock E2E).

**Summary:**

1. Create an account at [https://platform.openai.com](https://platform.openai.com) and add billing.
2. Create an API key under **API keys**.
3. Add to `.env` (see [.env.example](../../.env.example)):

   ```env
   OPENAI_API_KEY=sk-...
   OPENAI_CLASSIFICATION_MODEL=gpt-4o-mini
   OPENAI_EXTRACTION_MODEL=gpt-4o-mini
   OPENAI_OCR_MODEL=gpt-4o
   OPENAI_MAX_TOKENS=4096
   OPENAI_TEMPERATURE=0
   ```

4. Prompts and model usage: [../documentations/PROMPTS_REFERENCE.md](../documentations/PROMPTS_REFERENCE.md), [../documentations/SERVICES_REFERENCE.md](../documentations/SERVICES_REFERENCE.md).

**Related:** [01_DEVELOPMENT_SETUP.md](01_DEVELOPMENT_SETUP.md), [12_DOCKER_PRODUCTION_SETUP.md](12_DOCKER_PRODUCTION_SETUP.md), [../documentations/ENVIRONMENT_VARIABLES.md](../documentations/ENVIRONMENT_VARIABLES.md).
