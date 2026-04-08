# Gmail setup (monitored inbox)

**Purpose:** Ensure PO-like mail is found by the search in `gas/Config.gs` and that labels make sense for success vs failure.

## 1. Inbox

- Use the **same Google account** that owns the Apps Script project (the script runs as **you**).
- Optional: use a dedicated mailbox or forwarding so only PO traffic hits this inbox.

## 2. Labels

Create (or let the script create on first use):

- **`PO-Processed`** — webhook returned 2xx and callback completed successfully.
- **`PO-Processing-Failed`** — webhook failed (non-2xx) or downstream error path.

You can create them in Gmail: **Settings → Labels → Create new label**.

## 3. Search query (default)

In `Config.gs`:

```text
subject:(PO OR "Purchase Order") is:unread -label:PO-Processed -label:PO-Processing-Failed
```

**Test in Gmail’s search bar** before relying on automation. Adjust if your subjects differ (e.g. add a customer code).

## 4. Sending a Phase 1.5 test email

- **To:** your monitored Gmail address.
- **Subject:** must match the query, e.g. `Test PO 12345` (contains “PO”) or `Purchase Order 999`.
- **Body:** any text.
- **Unread:** leave as unread (or mark unread) so `is:unread` matches.

## 5. Timing

The time-driven trigger runs at most every **5 minutes**. Wait up to one cycle after sending.

## 6. Quotas (awareness)

- Gmail / Apps Script limits apply (daily send, etc.).
- `UrlFetchApp` payload size limit (large attachments) — see Google quotas.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| No webhook | Subject doesn’t match `PO` / `Purchase Order`; email already read; labels exclude the thread; trigger not installed. |
| Same email reprocessed | On success, code calls `markRead()` — if webhook fails, mail stays unread and may retry. |
