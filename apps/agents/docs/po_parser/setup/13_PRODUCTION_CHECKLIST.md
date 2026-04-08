# Production checklist

**When:** Before going live with the real LangGraph pipeline + cloud or static URL.

Use this as a final gate. Detailed items are in `.cursor/plans/po_parsing_ai_agent_211da517.plan.md` (Production Checklist / Phase 4). Cross-check [../documentations/ENVIRONMENT_VARIABLES.md](../documentations/ENVIRONMENT_VARIABLES.md) and [../documentations/TESTING_GUIDE.md](../documentations/TESTING_GUIDE.md).

**Minimum themes:**

- [ ] `.env` complete and secrets strong (webhook + GAS callback).
- [ ] GAS pushed, Web App deployed, Script properties set, trigger active.
- [ ] Google Sheet tabs and headers correct.
- [ ] Docker production build and health check OK.
- [ ] End-to-end test with a real PO email: Airtable + Sheets + notification + label.
- [ ] LangSmith tracing verified (if enabled).

Expand this document as you harden production requirements.
