# ngrok setup

> **Prev:** [13_DOCKER_BUILD_AND_RUN.md](13_DOCKER_BUILD_AND_RUN.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [15_LANGSMITH_SETUP.md](15_LANGSMITH_SETUP.md)

1. Sign up — https://ngrok.com
2. `ngrok config add-authtoken <TOKEN>`
3. With Docker listening on **8000**:

```bash
ngrok http 8000
```

4. **One tunnel, one public URL.** The ngrok window shows a single `Forwarding` line, e.g. `https://abc-xyz.ngrok-free.dev -> http://localhost:8000`. That is expected. Email and Drive do **not** get separate ngrok addresses: GAS posts to the **same host**; FastAPI routes differ by **path** (`POST /webhook/email` vs `POST /webhook/drive-image`). The `http://127.0.0.1:4040` line is only the **local** traffic inspector, not another public URL.

5. Set GAS Script Properties using the **https** hostname from that line plus the path (ngrok may show `*.ngrok-free.app` or `*.ngrok-free.dev` — use exactly what it prints):

| Property | Pattern |
|----------|---------|
| `WEBHOOK_URL` | `https://<your-ngrok-host>/webhook/email` |
| `IMAGE_WEBHOOK_URL` | `https://<your-ngrok-host>/webhook/drive-image` |

If ngrok prints `https://my-tunnel.ngrok-free.dev` (hostname changes on the free plan when you restart):

- `WEBHOOK_URL` → `https://my-tunnel.ngrok-free.dev/webhook/email`
- `IMAGE_WEBHOOK_URL` → `https://my-tunnel.ngrok-free.dev/webhook/drive-image`

6. Browser test: `https://<your-ngrok-host>/health`

7. **Search / history thumbnails:** Stored URLs look like `<origin>/uploads/<file>`. If the origin is `http://127.0.0.1:8000` or the Docker service name, the browser cannot load them. Do **one** of the following (then `docker compose restart agents` / rebuild frontend if you change `NEXT_PUBLIC_*`):

   - Set **`NEXT_PUBLIC_API_URL`** to the same https origin you use for the API in the browser (e.g. `https://<your-ngrok-host>` with no trailing slash). The backend uses this when saving new rows and **rewrites** old `127.0.0.1` / `localhost` / `agents` URLs when returning Search/history JSON.

   - Or set **`API_PUBLIC_BASE_URL`** to that https origin (it takes priority for new rows if both are set).

   Rebuild the frontend image after changing `NEXT_PUBLIC_API_URL` (`docker compose build frontend && docker compose up -d`).

> **NEXT:** Return to [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md) and update both webhook URLs.

Free tier URLs change on restart — update GAS each time.
