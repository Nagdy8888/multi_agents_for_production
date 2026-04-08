# GAS Web App (Python → GAS callback)

**Purpose:** Deploy a **Web App** so the Python mock (or real backend) can `POST` JSON to `doPost(e)` in `gas/WebApp.gs`. The callback includes `secret` in the **JSON body** (GAS cannot read custom HTTP headers like `x-webhook-secret` in `doPost`).

## 1. Deploy as Web App

1. Open the project: `cd gas && clasp open` (or open from [script.google.com](https://script.google.com)).
2. **Deploy → New deployment**.
3. Select type **Web app**.
4. Settings:
   - **Execute as:** Me (your account).
   - **Who has access:** **Anyone** (anonymous callers — required so Docker/ngrok can POST without Google login).
5. **Deploy** and authorize when asked.
6. **Copy the Web App URL** — it looks like:

   ```text
   https://script.google.com/macros/s/AKfycb.../exec
   ```

## 2. Put URL in Python `.env`

In the repo root `.env`:

```env
GAS_WEBAPP_URL=https://script.google.com/macros/s/XXXX/exec
```

Use the exact URL from the deployment dialog (no trailing slash unless your deployment requires it).

## 3. Shared secret (`GAS_WEBAPP_SECRET`)

1. Generate a strong secret, e.g.:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Python `.env`:**

   ```env
   GAS_WEBAPP_SECRET=<same value>
   ```

3. **GAS Script properties:**

   - `GAS_WEBAPP_SECRET` = **same value**

`WebApp.gs` compares `payload.secret` to `getConfig('GAS_WEBAPP_SECRET')`.

## 4. Notification recipients

**Script properties:**

```text
NOTIFICATION_RECIPIENTS=you@company.com,team@company.com
```

Comma-separated, no spaces required (the code trims spaces).

## 5. Quick callback test (optional)

From a machine that can reach the Web App URL.

**macOS / Linux / Git Bash** (bash):

```bash
curl -X POST "YOUR_WEB_APP_URL" \
  -H "Content-Type: application/json" \
  -d "{\"secret\":\"YOUR_GAS_WEBAPP_SECRET\",\"message_id\":\"test-msg\",\"status\":\"error\",\"errors\":[\"test\"]}"
```

**Windows PowerShell** — use **`curl.exe`** (not `curl`, which is an alias for `Invoke-WebRequest` and does not support `-d`). Run the **whole** command; do not paste only the `-d` line.

```powershell
curl.exe -X POST "YOUR_WEB_APP_URL" -H "Content-Type: application/json" -d '{"secret":"YOUR_GAS_WEBAPP_SECRET","message_id":"test-msg","status":"error","errors":["test"]}'
```

**PowerShell without curl** (`Invoke-RestMethod`):

```powershell
$uri = "YOUR_WEB_APP_URL"
$body = @{ secret = "YOUR_GAS_WEBAPP_SECRET"; message_id = "test-msg"; status = "error"; errors = @("test") } | ConvertTo-Json
Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json; charset=utf-8"
```

If the secret is wrong, the response JSON will indicate an error. If correct, check Monitoring Logs / inbox depending on `status`. If Google returns a redirect HTML page, retry with `curl.exe ... -L` (follow redirects).

## 6. After every `clasp push` that changes `doPost`

1. **Deploy → Manage deployments**.
2. **Edit** the Web App deployment → **New version** → **Deploy**.
3. The **URL does not change**; only the code version updates.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 403 / invalid secret | `GAS_WEBAPP_SECRET` must match in `.env` and Script properties. |
| `doPost` never runs | Wrong URL; deployment not updated; use POST not GET. |
| CORS / redirect confusion | Use `exec` URL from deployment; follow redirects in curl with `-L` if needed. |
