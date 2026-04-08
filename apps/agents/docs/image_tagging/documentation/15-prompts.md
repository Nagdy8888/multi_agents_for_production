# 15 — Prompts

This document gives the full text of the vision analyzer system prompt and the tagger prompt builder, example rendered prompts for season and objects, and tips for tuning.

---

## Vision analyzer prompt

**File:** `backend/src/image_tagging/prompts/system.py`

**Constant:** `VISION_ANALYZER_PROMPT`

**Full text:**

```
You are a visual product analyst for a gift product company.
Analyze this product image and return a JSON object with the following structure.
Return ONLY valid JSON, no markdown, no explanation.

{
  "visual_description": "<2-3 sentence description>",
  "dominant_mood": "<overall feel>",
  "visible_subjects": ["<list of things you see>"],
  "color_observations": "<describe the color palette in detail>",
  "design_observations": "<describe patterns, textures, layout>",
  "seasonal_indicators": "<any holiday/seasonal cues>",
  "style_indicators": "<art style, aesthetic>",
  "text_present": "<any text or lettering visible>"
}
```

Used by the vision_analyzer node as the system message. The model is also sent the image (data URI) and the user message: "Analyze this image and return the JSON object." See [09-node-vision-analyzer.md](09-node-vision-analyzer.md).

---

## Tagger prompt builder

**File:** `backend/src/image_tagging/prompts/tagger.py`

**Function:** `build_tagger_prompt(description: str, category: str, allowed_values: list[str], instructions: str | None = None) -> str`

**Template (conceptual):**

- Role: "You are a product tagging assistant. Based on the image description below, select the most applicable tags for the \"{category}\" category."
- Rules:
  - Only use values from the provided allowed_values list.
  - Return tags as a JSON object with this exact structure: `{"tags": ["value1", "value2"], "confidence_scores": {"value1": 0.95, "value2": 0.72}, "reasoning": "..."}`.
  - Include a tag only if confidence > 0.5.
  - For confidence: 0.9+ = clearly visible, 0.7–0.9 = likely present, 0.5–0.7 = possibly present.
  - Return ONLY valid JSON, no markdown.
- "Allowed values: {values_str}" (comma-separated).
- "Image description:\n{description}".
- If instructions is provided: "\n\nAdditional instructions: {instructions}".

---

## Example: season category

**Inputs:** category = "season", description = "A red gift box with gold ribbon and holly leaves. Festive Christmas styling.", allowed_values = ["christmas", "hanukkah", ...], instructions = None.

**Rendered prompt (abbreviated):**

```
You are a product tagging assistant. Based on the image description below,
select the most applicable tags for the "season" category.

Rules:
- Only use values from the provided allowed_values list
- Return tags as a JSON object with this exact structure:
  {"tags": ["value1", "value2"], "confidence_scores": {"value1": 0.95, "value2": 0.72}, "reasoning": "..."}
- Include a tag only if confidence > 0.5
- For confidence: 0.9+ = clearly visible, 0.7–0.9 = likely present, 0.5–0.7 = possibly present
- Return ONLY valid JSON, no markdown

Allowed values: christmas, hanukkah, kwanzaa, new_years, ...

Image description:
A red gift box with gold ribbon and holly leaves. Festive Christmas styling.
```

---

## Example: objects category (hierarchical)

**Inputs:** category = "objects", description = same as above, allowed_values = flat list of all object children (santa, gift_box, ribbon, holly, ...), instructions = "Select all visible objects and subjects. For hierarchical categories, return the child values (e.g. santa, reindeer, ribbon)."

The rendered prompt ends with:

```
...
Allowed values: santa, mrs_claus, gift_box, ribbon, holly, ...

Image description:
A red gift box with gold ribbon and holly leaves. Festive Christmas styling.

Additional instructions: Select all visible objects and subjects. For hierarchical categories, return the child values (e.g. santa, reindeer, ribbon).
```

---

## Tuning tips

- **Confidence scale:** Change the rule text (0.9+, 0.7–0.9, 0.5–0.7) to make the model more or less conservative. Stricter wording can reduce false positives and increase empty/low-confidence returns.
- **New categories:** Add the category to the taxonomy and a new tagger that calls `run_tagger(state, "new_category", instructions=..., max_tags=...)`. The same prompt template applies; adjust instructions and max_tags as needed.
- **Vision description quality:** If taggers perform poorly, improve the vision prompt (e.g. ask for more detail on colors, objects, or style) so `vision_description` carries more signal. Taggers only see text, not the image.
- **Allowed values length:** For very long lists (e.g. all objects), the prompt can be large; consider chunking or shortening if you hit context limits, though current taxonomy sizes are fine for gpt-4o.
