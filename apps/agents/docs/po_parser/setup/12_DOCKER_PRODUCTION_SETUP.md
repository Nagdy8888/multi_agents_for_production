# Docker production profile (real backend)

**When:** After Phase 1.5 E2E passes and Phase 2 code is implemented.

**Summary:**

1. Fill **all** keys in `.env` (OpenAI, LangSmith, Airtable, webhook secrets, `GAS_WEBAPP_URL`, etc.).
2. Stop the mock:

   ```bash
   docker compose --profile mock down
   ```

3. Start the production service:

   ```bash
   docker compose --profile production up --build
   ```

4. Health check:

   ```bash
   curl http://localhost:8000/health
   ```

   **Windows PowerShell:** `curl` is an alias for **`Invoke-WebRequest`**, which may prompt about script execution and prints a verbose object. Prefer one of:

   ```powershell
   curl.exe http://localhost:8000/health
   ```

   ```powershell
   Invoke-RestMethod http://localhost:8000/health
   ```

   ```powershell
   Invoke-WebRequest -UseBasicParsing http://localhost:8000/health
   ```

   Expected (production API):

   ```json
   {"status":"healthy","timestamp":"2026-04-05T12:00:00.000000+00:00"}
   ```

   There is **no** `"mode":"mock"` field (that comes only from `scripts/test_e2e_mock.py`).

5. Expose with ngrok the same way as mock — update GAS `WEBHOOK_URL` if the host port changes.

**Do not run mock and production at the same time** — both use host port **8000** by default.

**Reference:** [../documentations/TESTING_GUIDE.md](../documentations/TESTING_GUIDE.md), `.cursor/plans/po_parsing_ai_agent_211da517.plan.md`.
