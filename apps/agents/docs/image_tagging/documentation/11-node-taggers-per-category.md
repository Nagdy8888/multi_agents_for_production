# 11 — Node: Taggers Per Category

This document lists each of the 8 tagger functions with its signature, custom instructions, max_tags, and which taxonomy category it uses. Example outputs are illustrative.

---

## File

**File:** `backend/src/image_tagging/nodes/taggers.py`

All taggers call `run_tagger(state, category, instructions=..., max_tags=...)` — see [10-node-taggers-overview.md](10-node-taggers-overview.md).

---

## 1. tag_season

- **Signature:** `async def tag_season(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"season"`
- **Instructions:** None (default).
- **max_tags:** None (no cap).
- **Taxonomy:** [06-taxonomy-complete-reference.md](06-taxonomy-complete-reference.md) — season (19 flat values).

**Example output (partial_tags element):**

```json
{ "category": "season", "tags": ["christmas"], "confidence_scores": { "christmas": 0.92 } }
```

---

## 2. tag_theme

- **Signature:** `async def tag_theme(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"theme"`
- **Instructions:** `"Select all aesthetic themes that apply."`
- **max_tags:** None.
- **Taxonomy:** theme (18 flat values).

**Example output:**

```json
{ "category": "theme", "tags": ["traditional", "elegant_luxury"], "confidence_scores": { "traditional": 0.88, "elegant_luxury": 0.72 } }
```

---

## 3. tag_objects

- **Signature:** `async def tag_objects(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"objects"`
- **Instructions:** `"Select all visible objects and subjects. For hierarchical categories, return the child values (e.g. santa, reindeer, ribbon)."`
- **max_tags:** `MAX_OBJECTS` (10) from configuration.
- **Taxonomy:** objects (7 parents, many children) — get_flat_values returns all children.

**Example output:**

```json
{ "category": "objects", "tags": ["gift_box", "ribbon", "holly"], "confidence_scores": { "gift_box": 0.95, "ribbon": 0.9, "holly": 0.7 } }
```

---

## 4. tag_colors

- **Signature:** `async def tag_colors(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"dominant_colors"`
- **Instructions:** `"Select up to 5 dominant colors. Return the specific shade names (e.g. crimson, navy)."`
- **max_tags:** `MAX_COLORS` (5).
- **Taxonomy:** dominant_colors (9 families with shades).

**Example output:**

```json
{ "category": "dominant_colors", "tags": ["crimson", "gold_metallic", "white"], "confidence_scores": { "crimson": 0.9, "gold_metallic": 0.85, "white": 0.78 } }
```

---

## 5. tag_design

- **Signature:** `async def tag_design(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"design_elements"`
- **Instructions:** `"Select all applicable patterns, textures, layout features, and typography."`
- **max_tags:** None.
- **Taxonomy:** design_elements (33 flat values).

**Example output:**

```json
{ "category": "design_elements", "tags": ["foil_metallic", "centered_motif", "no_text"], "confidence_scores": { "foil_metallic": 0.88, "centered_motif": 0.75, "no_text": 0.9 } }
```

---

## 6. tag_occasion

- **Signature:** `async def tag_occasion(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"occasion"`
- **Instructions:** `"Select all applicable occasions or use cases."`
- **max_tags:** None.
- **Taxonomy:** occasion (8 flat values).

**Example output:**

```json
{ "category": "occasion", "tags": ["gifting_general"], "confidence_scores": { "gifting_general": 0.9 } }
```

---

## 7. tag_mood

- **Signature:** `async def tag_mood(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"mood"`
- **Instructions:** `"Select all applicable moods or tones."`
- **max_tags:** None.
- **Taxonomy:** mood (9 flat values).

**Example output:**

```json
{ "category": "mood", "tags": ["joyful_fun"], "confidence_scores": { "joyful_fun": 0.82 } }
```

---

## 8. tag_product

- **Signature:** `async def tag_product(state: ImageTaggingState) -> dict[str, Any]`
- **Category:** `"product_type"`
- **Instructions:** `"Select the single most likely product type. Return one specific child value (e.g. gift_bag_medium, wrapping_paper_roll)."`
- **max_tags:** 1.
- **Taxonomy:** product_type (5 parents with children).

**Example output:**

```json
{ "category": "product_type", "tags": ["gift_bag_medium"], "confidence_scores": { "gift_bag_medium": 0.78 } }
```

---

## Summary table

| Tagger | Category | Instructions | max_tags |
|--------|----------|--------------|----------|
| tag_season | season | — | None |
| tag_theme | theme | Select all aesthetic themes that apply | None |
| tag_objects | objects | Hierarchical; return child values | 10 |
| tag_colors | dominant_colors | Up to 5; specific shade names | 5 |
| tag_design | design_elements | Patterns, textures, layout, typography | None |
| tag_occasion | occasion | Occasions or use cases | None |
| tag_mood | mood | Moods or tones | None |
| tag_product | product_type | Single most likely; one child value | 1 |
