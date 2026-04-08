# Google Sheets setup

**Purpose:** Three tabs for **PO Data**, **PO Items**, and **Monitoring Logs**. GAS uses `SpreadsheetApp.openById(SPREADSHEET_ID)` — no Sheets API key in Python.

## 1. Create the spreadsheet

1. Open [https://sheets.google.com](https://sheets.google.com) as the **same account** as the GAS project.
2. **Blank spreadsheet**.
3. Name it e.g. `PO Parsing Agent - Data & Monitoring`.

## 2. Tab: PO Data

1. Rename **Sheet1** to **`PO Data`** (exact name — matches `TAB_PO_DATA` in `gas/Config.gs`).
2. In **row 1**, add these headers (order matters for `SheetsWriter.gs`):

| Column | Header |
|--------|--------|
| A | PO Number |
| B | Customer |
| C | PO Date |
| D | Ship Date |
| E | Status |
| F | Source Type |
| G | Email Subject |
| H | Sender |
| I | Confidence |
| J | Validation Status |
| K | Processing Timestamp |
| L | Airtable Link |

## 3. Tab: PO Items

1. **Insert sheet** → name **`PO Items`**.
2. Row 1 headers:

| Column | Header |
|--------|--------|
| A | PO Number |
| B | SKU |
| C | Description |
| D | Quantity |
| E | Unit Price |
| F | Total Price |
| G | Destination/DC |
| H | Processing Timestamp |

## 4. Tab: Monitoring Logs

1. **Insert sheet** → name **`Monitoring Logs`**.
2. Row 1 headers:

| Column | Header |
|--------|--------|
| A | Timestamp (Cairo) |
| B | Email ID |
| C | Subject |
| D | Sender |
| E | Classification Result |
| F | Confidence |
| G | Parse Status |
| H | Processing Time (ms) |
| I | Errors |
| J | Node |

## 5. Get `SPREADSHEET_ID`

From the browser URL:

```text
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
```

Copy the segment between `/d/` and `/edit`.

## 6. Add to GAS Script properties

**Project Settings → Script properties:**

- `SPREADSHEET_ID` = the ID above.

## 7. Access

The script owner must have **edit** access to the file (owner is fine). No service account.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Exception: Cannot find sheet` | Tab names must be exactly `PO Data`, `PO Items`, `Monitoring Logs`. |
| Append goes to wrong columns | Row 1 headers must match the tables above; don’t insert blank columns at the start. |
