# Technical decisions

Short rationale for key choices.

## LangGraph

- **Why:** Needed a clear pipeline (preprocess → vision → many taggers → validate → aggregate) with shared state and parallel fan-out. LangGraph’s state graph and Send API fit this; we avoid ad-hoc orchestration and get a single compiled graph.
- **Alternative:** Custom asyncio or Celery could work but would duplicate state and flow logic.

## GPT-4o

- **Why:** Strong vision and reliable JSON output for product imagery; good balance of quality and cost for structured tagging.
- **Alternative:** Smaller or specialized vision models could reduce cost but may need more prompt tuning and validation.

## Supabase (PostgreSQL)

- **Why:** Managed Postgres, simple connection string, JSONB and GIN indexes for tag storage and array containment search; fits “optional DB” (app works without it).
- **Alternative:** SQLite or file-based storage would avoid a network DB but would not scale search the same way.

## Next.js + shadcn/ui

- **Why:** Fast iteration, App Router, good DX; shadcn gives accessible components and theming without heavy UI lock-in.
- **Alternative:** Remix or Vite + React could work; shadcn is framework-agnostic enough to move if needed.

## In-memory bulk batch state

- **Why:** Phase 5 bulk upload stores batch state in a module-level dict; simple and no extra infra.
- **Trade-off:** Batches are lost on restart; for production, moving to Redis or DB would be better.
