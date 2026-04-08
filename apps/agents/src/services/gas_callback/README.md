# GAS Web App callback

- **Settings:** `GAS_WEBAPP_URL`, `GAS_WEBAPP_SECRET`, optional `timeout` (default 30s) on `GASCallbackSettings`.
- **Client:** `send_results_async` (httpx async) and `send_results` (uses `asyncio.run` for sync callers such as LangGraph nodes).

The shared secret is sent as JSON `secret`, not as an HTTP header, because GAS `doPost` cannot read arbitrary headers.

`send_results_async` uses **`httpx.AsyncClient`** (non-blocking HTTP). `send_results` uses **`asyncio.run`** so sync LangGraph nodes and `BackgroundTasks` workers can call it without blocking the FastAPI event loop on the request thread.
