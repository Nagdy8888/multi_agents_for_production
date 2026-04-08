# Comprehensive Undergraduate Curriculum

Step-by-step learning path for the Image Analysis Agent project. Each lesson combines **concepts** (theory at undergraduate level) with **in-project** code walkthroughs, **key takeaways**, **exercises**, and a **Next** link to the following lesson. Study the lessons in order (01 through 14) to understand not only this project but the patterns for building similar AI agent systems.

## Structure

- **Part 1 — Foundations (01–03):** What an AI agent is, project overview and architecture, Python and FastAPI basics.
- **Part 2 — The LangGraph Agent (04–09):** LangGraph core concepts, state and data models, graph builder, preprocessor and vision, taggers and taxonomy, validation and aggregation.
- **Part 3 — Backend and Database (10–11):** API design and endpoints, database persistence and search.
- **Part 4 — Frontend and Deployment (12–13):** Next.js and components, Docker and deployment.
- **Part 5 — Synthesis (14):** End-to-end trace, what you learned, applying the pattern to future projects, and resources.

## Lessons (14)

| # | File | Description |
|---|------|-------------|
| 01 | [01-what-is-an-ai-agent.md](01-what-is-an-ai-agent.md) | What AI agents are (vs chatbots), state and tools, MIS context, ReAct / plan-and-execute / DAG architectures |
| 02 | [02-project-overview-and-architecture.md](02-project-overview-and-architecture.md) | What the project does end-to-end, four layers, request lifecycles (single, bulk, search), glossary |
| 03 | [03-python-fastapi-foundations.md](03-python-fastapi-foundations.md) | Python async, venv, FastAPI routes, UploadFile, CORS, static files, exception handler, background tasks |
| 04 | [04-langgraph-core-concepts.md](04-langgraph-core-concepts.md) | StateGraph, state, nodes, edges, reducers, Send API, compile, ainvoke |
| 05 | [05-state-and-data-models.md](05-state-and-data-models.md) | ImageTaggingState, partial_tags reducer, Pydantic models, data flow from taggers to aggregator |
| 06 | [06-graph-builder-walkthrough.md](06-graph-builder-walkthrough.md) | Line-by-line graph construction, fan-out to taggers, full agent diagram |
| 07 | [07-preprocessor-and-vision.md](07-preprocessor-and-vision.md) | Preprocessor steps, vision node (messages, retry, parse), system prompt |
| 08 | [08-taggers-taxonomy-and-prompts.md](08-taggers-taxonomy-and-prompts.md) | Taxonomy (flat vs hierarchical), run_tagger, prompt template, all 8 taggers |
| 09 | [09-validation-confidence-aggregation.md](09-validation-confidence-aggregation.md) | Validator, confidence filter, aggregator, TagRecord and processing_status |
| 10 | [10-api-design-and-endpoints.md](10-api-design-and-endpoints.md) | All REST endpoints, BATCH_STORAGE, bulk background task, filter params, exception handler |
| 11 | [11-database-persistence-and-search.md](11-database-persistence-and-search.md) | image_tags schema, build_search_index, search_index @>, get_available_filter_values |
| 12 | [12-frontend-nextjs-and-components.md](12-frontend-nextjs-and-components.md) | App Router, pages and components, data flow for analyze, search, bulk |
| 13 | [13-docker-and-deployment.md](13-docker-and-deployment.md) | Backend and frontend Dockerfiles, docker-compose, NEXT_PUBLIC_API_URL, commands |
| 14 | [14-end-to-end-and-future-projects.md](14-end-to-end-and-future-projects.md) | Full trace, checklist of what you learned, applying the pattern, next steps and resources |

## How to use this curriculum

- Read lessons **in order** for a coherent narrative from agents and architecture through to deployment and future projects.
- Use **In this project** sections to locate exact files and functions in the codebase.
- Do the **Exercises** at the end of each lesson to reinforce understanding.
- Use the **Next** link at the bottom of each lesson to move to the following one.
