# FYI notes for senior review

**Purpose:** Short, numbered implementation notes to share with a senior reviewer. Each topic that deserves extra context (beyond the main curriculum steps `01`–`12`) can get a dedicated `NOTE_*.md` file in this folder and a one-line entry below.

**How to use:** Add a new row under [Index of notes](#index-of-notes), create `NOTE_<topic>.md` with numbered points (1, 2, 3…), and link it from the relevant curriculum file if applicable.

---

## Index of notes

| # | Topic | Note doc | Source in repo (issue / behavior) | One-line summary |
|---|--------|----------|-------------------------------------|------------------|
| 1 | Classification body snippet | [NOTE_clamp_text_classification.md](NOTE_clamp_text_classification.md) | [`utils.py`](../../src/po_parser/utils.py) **L6–L9** (`clamp_text`); [`classifier.py`](../../src/po_parser/nodes/classifier.py) **L41–L49** (`snippet` → `body_snippet` in prompt) | Only the **first 500 characters** of the email body go into the **classifier** LLM prompt; full body is still used later in `parse_body` / consolidation. |
| 2 | Gmail `SEARCH_QUERY` | [NOTE_search_query_gmail.md](NOTE_search_query_gmail.md) | [`gas/Config.gs`](../../gas/Config.gs) **L19–L20** (`SEARCH_QUERY`) | GAS only pulls emails whose **subject** matches **PO** or the phrase **Purchase Order**, plus `is:unread`, label exclusions, and exclusions for own notification emails. |

<!-- Add future rows here, e.g.:
| 3 | … | NOTE_….md | `path/file.py` L10–L20 | … |
-->

---

## Note 1 — Classification: `clamp_text(body, 500)` (summary)

For the full numbered list, see [NOTE_clamp_text_classification.md](NOTE_clamp_text_classification.md).

**Where in code**

| Location | Lines | What to look at |
|----------|-------|-----------------|
| [`src/po_parser/utils.py`](../../src/po_parser/utils.py) | **6–9** | `clamp_text` — truncates to `max_chars` |
| [`src/po_parser/nodes/classifier.py`](../../src/po_parser/nodes/classifier.py) | **41–42** | `body` → `snippet = clamp_text(body, 500)` |
| Same file | **45–49** | `body_snippet=snippet` passed into `CLASSIFICATION_USER_TEMPLATE` |

1. **`clamp_text`** (see table above) truncates text to `max_chars` when longer; **`500`** is only applied in **`classify_node`** at **L42**.
2. Only the **classification** OpenAI call uses this snippet; **`state["email"].body`** is unchanged for downstream nodes.
3. **Rationale:** smaller prompt (cost/latency); subject + attachment names still full in the template.
4. **Edge case:** PO signals only after character 500 in the body could weaken classification; raise limit or adjust heuristics if misclassification appears.

---

## Note 2 — Gmail: `SEARCH_QUERY` (PO / Purchase Order in **subject**)

For the full numbered list, see [NOTE_search_query_gmail.md](NOTE_search_query_gmail.md).

**Where in code**

| Location | Lines | What to look at |
|----------|-------|-----------------|
| [`gas/Config.gs`](../../gas/Config.gs) | **L19–L20** | `SEARCH_QUERY` string passed to `GmailApp.search` in `Code.gs` |

**Summary:** The trigger does **not** search the email body for “PO” or “Purchase Order.” It uses Gmail’s **`subject:(...)`** operator so only **subjects** are matched for those terms (together with unread, label filters, and notification exclusions — see the note file).

---

*Last updated: curriculum maintainer — append new numbered sections when adding `NOTE_*.md` files.*
