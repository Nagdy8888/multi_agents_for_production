# ngrok setup (local dev tunnel)

**Purpose:** Expose `http://localhost:8000` (Docker mock or real API) to the public internet so **Google Apps Script** can `UrlFetchApp` your webhook. GAS cannot call `localhost` on your PC.

## Why ngrok

- Your machine: Docker listens on `127.0.0.1:8000` (mapped to host port 8000).
- GAS executes in Google’s cloud — it needs an **HTTPS URL** that reaches that port.
- ngrok creates a tunnel: `https://xxxx.ngrok-free.app` → `localhost:8000`.

## 1. Create an ngrok account

1. Go to [https://ngrok.com/signup](https://ngrok.com/signup).
2. The free tier is enough for development.

## 2. Install ngrok

- **Windows:** [Download](https://ngrok.com/download) installer, `choco install ngrok`, or `winget install ngrok.ngrok`. If `ngrok` is not found after install, open a **new** terminal, restart Cursor, or call the full path to `ngrok.exe` (PATH refresh).
- **macOS:** `brew install ngrok`
- **Linux:** `snap install ngrok` or download the binary.

Verify:

```bash
ngrok version
```

## 3. Add your authtoken

1. Open [https://dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken).
2. Copy the token.
3. Run:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

If you see **ERR_NGROK_108**, the authtoken was not configured — repeat this step.

## 4. Start the tunnel

1. Start the Docker mock (or production) server so something is listening on **8000**:

   ```bash
   docker compose --profile mock up
   ```

2. In a **separate** terminal:

   ```bash
   ngrok http 8000
   ```

3. Copy the **Forwarding** HTTPS URL, e.g. `https://abc123.ngrok-free.app`.

## 5. Configure GAS `WEBHOOK_URL`

In Apps Script: **Project Settings → Script properties**:

- Key: `WEBHOOK_URL`
- Value: **full URL including path**, e.g.

  ```text
  https://abc123.ngrok-free.app/webhook/email
  ```

Do **not** omit `/webhook/email` — that is the FastAPI route.

## 6. Verify from a browser

Open:

```text
https://<your-ngrok-host>/health
```

You should see JSON like `{"status":"healthy","mode":"mock"}` when the **mock** profile is running, or `{"status":"healthy","timestamp":"...Z"}` when **production** (`uvicorn src.api.main:app`) is running (no `mode` key).

- **502 Bad Gateway:** Nothing listening on port 8000 — start Docker first.
- **Tunnel not found:** ngrok stopped or wrong URL.

## 7. ngrok web UI (optional)

While ngrok runs, open [http://localhost:4040](http://localhost:4040) to inspect requests, status codes, and bodies (useful for debugging GAS → Python).

## Important notes

- **Free tier:** The URL usually **changes** every time you restart ngrok. Update **`WEBHOOK_URL`** in GAS Script Properties each time.
- **Paid reserved domain:** You can get a stable URL (optional).
- Keep the **ngrok terminal open** while testing.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| ERR_NGROK_108 | Run `ngrok config add-authtoken ...` |
| 502 from ngrok URL | Start Docker; confirm `curl http://localhost:8000/health` works locally |
| GAS `UrlFetchApp` timeout | Server must respond quickly — webhook returns 202; check Docker logs |
| Connection reset | Restart ngrok; update URL in GAS |
