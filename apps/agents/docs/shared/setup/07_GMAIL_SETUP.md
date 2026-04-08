# Gmail setup (PO parser)

> **Prev:** [06_GOOGLE_SHEETS_SETUP.md](06_GOOGLE_SHEETS_SETUP.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [08_GOOGLE_DRIVE_SETUP.md](08_GOOGLE_DRIVE_SETUP.md)

## Labels

Create in Gmail:

- `PO-Processed`
- `PO-Processing-Failed`

## Search query

Default in `gas-scripts/shared/Config.gs` (`SEARCH_QUERY`). Test the same string in Gmail search.

## Test mail

- Unread
- Subject contains `PO` or `Purchase Order`
- Send to the mailbox the script runs as

Trigger runs every **5 minutes** (after you install it in guide 09).
