# Google Sheets setup (two spreadsheets)

> **Prev:** [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md) | **Index:** [00_SETUP_INDEX.md](00_SETUP_INDEX.md) | **Next:** [07_GMAIL_SETUP.md](07_GMAIL_SETUP.md)

## A — PO parser sheet

One spreadsheet, three tabs (exact names):

1. **PO Data** — row 1: `PO Number`, `Customer`, `PO Date`, `Ship Date`, `Status`, `Source Type`, `Email Subject`, `Sender`, `Confidence`, `Validation Status`, `Processing Timestamp`, `Airtable Link`
2. **PO Items** — row 1: `PO Number`, `SKU`, `Description`, `Quantity`, `Unit Price`, `Total Price`, `Destination/DC`, `Processing Timestamp`
3. **Monitoring Logs** — row 1: `Timestamp (Cairo)`, `Email ID`, `Subject`, `Sender`, `Classification Result`, `Confidence`, `Parse Status`, `Processing Time (ms)`, `Errors`, `Node`

Copy spreadsheet ID from URL → GAS property `SPREADSHEET_ID`.

## B — Image tagger sheet (**different file**)

Tabs (names match `gas-scripts/shared/Config.gs`):

1. **Image Tags** — row 1: `Image ID`, `Filename`, `Drive File ID`, `Tags JSON`, `Confidence`, `Processing Status`, `Timestamp` (see `image_tagger/SheetsWriter.gs` column order)
2. **Image Monitoring** — row 1: `Timestamp`, `Image ID`, `Filename`, `Status`, `Processing Time (ms)`, `Errors`

Copy ID → GAS `IMAGE_SPREADSHEET_ID`.

> **NEXT:** Update [05_GAS_SCRIPT_PROPERTIES.md](05_GAS_SCRIPT_PROPERTIES.md) with both IDs.
