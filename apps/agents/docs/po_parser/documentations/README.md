# Technical documentation

Reference material for the **PO Parsing AI Agent**. Each file is intended to match the **Documentation Plan** section of [`.cursor/plans/po_parsing_ai_agent_211da517.plan.md`](../../.cursor/plans/po_parsing_ai_agent_211da517.plan.md): real project detail, not placeholders. Where the **implementation** differs from an older plan sentence, the docs call that out (e.g. parser graph order, `doPost` auth, Airtable 429 retry).

Setup steps live in [../setup/README.md](../setup/README.md). The numbered **runtime curriculum** is under [../curriculum/README.md](../curriculum/README.md) (full walkthroughs 01–12 per [the project plan](../../.cursor/plans/po_parsing_ai_agent_211da517.plan.md), grounded in the repo). The same curriculum Mermaid also appears in [TESTING_GUIDE.md](TESTING_GUIDE.md).

| Document | Contents (plan-aligned) |
|----------|---------------------------|
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Volume/scaling problem, objective, scope, success targets (&gt;90%), out of scope, quoted principles, tech stack, Mermaid |
| [ARCHITECTURE.md](ARCHITECTURE.md) | GAS / FastAPI / LangGraph / services / observability, rationale table, scalability, security, Mermaid |
| [DATA_FLOW.md](DATA_FLOW.md) | Steps 1–12, timing estimates, JSON at each stage, sequence + plan subflows |
| [API_REFERENCE.md](API_REFERENCE.md) | Auth, errors, rate/size limits, health + webhook, `curl`, Mermaid |
| [SCHEMAS_REFERENCE.md](SCHEMAS_REFERENCE.md) | Fields required/optional, JSON examples (incl. Greenbrier / Family Dollar), `AgentState` read/write matrix, class Mermaid |
| [LANGGRAPH_REFERENCE.md](LANGGRAPH_REFERENCE.md) | Why LangGraph, wiring, **node-by-node table**, **full plan §2.5 node prose**, Studio, LangSmith, plan subflows |
| [SERVICES_REFERENCE.md](SERVICES_REFERENCE.md) | OpenAI/Airtable/GAS client methods, limits, costs, callback contract, Mermaid |
| [PROMPTS_REFERENCE.md](PROMPTS_REFERENCE.md) | Full classification + extraction + OCR text, thresholds, examples, versioning |
| [GAS_REFERENCE.md](GAS_REFERENCE.md) | Scopes, Script Properties, **per-file functions**, limits, timezones, Mermaid |
| [EDGE_CASES.md](EDGE_CASES.md) | Table + plan narratives; implementation deltas (e.g. multi-PO) |
| [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) | Full `.env` + Script Properties tables, Docker/local, security, timezone strategy |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Categories, strategy, retries **plan vs code**, monitoring, alerts, Mermaid |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | pytest layout, per-node test plan, coverage goal, mock E2E, curriculum Mermaid |

Authoritative implementation spec: `.cursor/plans/po_parsing_ai_agent_211da517.plan.md`.

**Mermaid diagrams:** Each file above includes a **“Diagram(s) from project plan”** section (where applicable) copying the Mermaid blocks from that plan. The plan does not define separate diagrams for `PROMPTS_REFERENCE`, `EDGE_CASES`, or `ENVIRONMENT_VARIABLES`; those files have no plan Mermaid to add. When a plan diagram differs slightly from the current code (e.g. parser routing, `doPost` auth labeling), the doc section calls that out.
