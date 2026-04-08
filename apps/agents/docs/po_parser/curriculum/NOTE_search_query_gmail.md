# Note: Gmail `SEARCH_QUERY` (PO / Purchase Order in subject)

**Source lines:** [`gas/Config.gs`](../../gas/Config.gs) **`SEARCH_QUERY`** (~**L19–L20**). Related curriculum: [`01_GAS_TRIGGER_FLOW.md`](01_GAS_TRIGGER_FLOW.md). Senior index: [`SENIOR_FYI_NOTES.md`](SENIOR_FYI_NOTES.md).

1. **Subject filter (what gets matched):** `subject:(PO OR "Purchase Order")` — Gmail searches **only the subject line**, not the body. A thread matches if the subject contains the term **PO** *or* the exact phrase **Purchase Order** (quotes = phrase match).

2. **Unread only:** `is:unread` — already processed (read) messages are not returned by this search.

3. **Exclude labeled threads:** `-label:PO-Processed -label:PO-Processing-Failed` — skip threads already handled or marked failed.

4. **Exclude notification noise:** `-subject:"PO Processed:" -subject:"PO Processing FAILED:" -from:me` — avoids re-processing emails sent by the script (success/failure notifications) that would otherwise match **PO** in the subject.

5. **Full string** — see `Config.gs`; do not change without updating GAS docs and [`01_GAS_TRIGGER_FLOW.md`](01_GAS_TRIGGER_FLOW.md).
