# Note: `clamp_text(body, 500)` in classification

Summary of how the email body is trimmed for the **classifier** LLM prompt only.

**Source lines:** [`src/po_parser/utils.py`](../../src/po_parser/utils.py) **L6–L9** (`clamp_text`); [`src/po_parser/nodes/classifier.py`](../../src/po_parser/nodes/classifier.py) **L41–L49** (snippet → prompt). Related curriculum: [`04_CLASSIFICATION.md`](04_CLASSIFICATION.md). Senior index: [`SENIOR_FYI_NOTES.md`](SENIOR_FYI_NOTES.md).

1. **`clamp_text(text, max_chars)`** — If `text` is longer than `max_chars`, the function returns **only the first `max_chars` characters**; otherwise it returns the full string. There is no “…” suffix in code—it is a plain slice.

2. **`clamp_text(body, 500)` in `classify_node`** — The classifier sets `snippet = clamp_text(body, 500)` and passes `snippet` into `CLASSIFICATION_USER_TEMPLATE` as `body_snippet`. So the **OpenAI classification call** sees at most **500 characters** of the email body in the user message.

3. **Why cap at 500** — Keeps the classification prompt **small** (lower latency, lower token cost). Subject and attachment filenames are still sent in full in the same template; together they usually give enough signal for “is this a PO?”.

4. **Full body is not removed from the pipeline** — `state["email"].body` is unchanged. Later nodes (for example **`parse_body`**) still process the **entire** body for consolidation and extraction. Only the **classification** step uses this short snippet in its prompt.

5. **Risk to be aware of** — If the only PO cues appear **after** the first 500 characters of the body, the classifier might get a weaker signal. In practice, subjects and attachments often carry the decision; if you see misclassification on long bodies, consider raising the limit or relying more on rule fallback / attachment hints.
