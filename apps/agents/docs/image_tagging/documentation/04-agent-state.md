# 04 — Agent State

This document describes `ImageTaggingState`: every field (type, default, who writes it, who reads it), the `Annotated[list, operator.add]` reducer on `partial_tags`, a field × node lifecycle table, and example initial and final state.

---

## Definition

**File:** `backend/src/image_tagging/schemas/states.py`

```python
from typing import Annotated, Literal, Optional, TypedDict
import operator

class ImageTaggingState(TypedDict, total=False):
    """State passed through the LangGraph pipeline."""
    image_id: str
    image_url: str
    image_base64: Optional[str]
    metadata: dict
    vision_description: str
    vision_raw_tags: dict
    partial_tags: Annotated[list, operator.add]
    validated_tags: dict
    flagged_tags: list
    tag_record: dict
    needs_review: bool
    processing_status: Literal["pending", "complete", "needs_review", "failed"]
    error: Optional[str]
```

- **total=False:** All keys are optional; nodes only set the keys they update.
- **partial_tags** is the only field with a reducer; see below.

---

## Field reference

| Field | Type | Default | Written by | Read by |
|-------|------|---------|------------|---------|
| **image_id** | str | — | server (initial_state) | aggregator, server response |
| **image_url** | str | — | server | server response |
| **image_base64** | Optional[str] | — | server, preprocessor (replaces) | preprocessor, vision_analyzer |
| **metadata** | dict | — | preprocessor | — |
| **vision_description** | str | — | vision_analyzer | all taggers |
| **vision_raw_tags** | dict | — | vision_analyzer | — |
| **partial_tags** | list | [] | taggers (reducer) | tag_validator |
| **validated_tags** | dict | — | tag_validator, confidence_filter (replaces) | confidence_filter, aggregator |
| **flagged_tags** | list | — | tag_validator, confidence_filter (append) | aggregator, server |
| **tag_record** | dict | — | tag_aggregator | server |
| **needs_review** | bool | — | confidence_filter | aggregator |
| **processing_status** | Literal | — | preprocessor, vision_analyzer, tag_aggregator | server |
| **error** | Optional[str] | — | preprocessor, vision_analyzer (on failure) | aggregator |

---

## Reducer: `Annotated[list, operator.add]` on partial_tags

- **Why it exists:** Eight tagger nodes run in parallel. Each returns `{"partial_tags": [one TagResult dict]}`. If LangGraph simply overwrote `partial_tags` on each update, only one tagger’s result would remain. The reducer tells LangGraph to **merge** updates by concatenating lists.
- **How LangGraph uses it:** For each node output that has `partial_tags`, it applies `operator.add` (i.e. `+`) between the current state’s `partial_tags` and the node’s `partial_tags`. So after all 8 taggers run, `state["partial_tags"]` is the concatenation of 8 single-element lists: one `TagResult` per category.
- **Who writes:** Each of the 8 tagger nodes returns exactly one element in `partial_tags`. Tag validator does not write `partial_tags`; it reads it and writes `validated_tags` and `flagged_tags`.

---

## State lifecycle (field × node)

| Field | preprocessor | vision | taggers | validator | confidence | aggregator |
|-------|--------------|--------|---------|-----------|------------|------------|
| image_base64 | W | R | — | — | — | — |
| metadata | W | — | — | — | — | — |
| vision_description | — | W | R | — | — | — |
| vision_raw_tags | — | W | — | — | — | — |
| partial_tags | — | — | W (reducer) | R | — | — |
| validated_tags | — | — | — | W | R,W | R |
| flagged_tags | — | — | — | W | R,W | R |
| needs_review | — | — | — | — | W | R |
| tag_record | — | — | — | — | — | W |
| processing_status | W | W | — | — | — | W |
| error | W | W | — | — | — | R |

W = writes, R = reads. Server provides image_id, image_url, image_base64, partial_tags=[] and reads final state for the API response.

---

## Example initial state (from server)

```json
{
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "image_url": "http://localhost:8000/uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
  "image_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwc...",
  "partial_tags": []
}
```

---

## Example final state (after successful run)

```json
{
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "image_url": "http://localhost:8000/uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
  "image_base64": "/9j/4AAQ...",
  "metadata": { "width": 800, "height": 600, "format": "JPEG" },
  "vision_description": "A red gift box with gold ribbon and holly...",
  "vision_raw_tags": { "visual_description": "...", "dominant_mood": "festive", "visible_subjects": ["gift_box", "ribbon"], "color_observations": "Red and gold...", "design_observations": "...", "seasonal_indicators": "Christmas", "style_indicators": "Traditional", "text_present": "None" },
  "partial_tags": [
    { "category": "season", "tags": ["christmas"], "confidence_scores": { "christmas": 0.92 } },
    { "category": "theme", "tags": ["traditional"], "confidence_scores": { "traditional": 0.88 } },
    { "category": "objects", "tags": ["gift_box", "ribbon", "holly"], "confidence_scores": { "gift_box": 0.95, "ribbon": 0.9, "holly": 0.7 } },
    { "category": "dominant_colors", "tags": ["crimson", "gold_metallic"], "confidence_scores": { "crimson": 0.9, "gold_metallic": 0.85 } },
    { "category": "design_elements", "tags": ["foil_metallic", "centered_motif"], "confidence_scores": { "foil_metallic": 0.88, "centered_motif": 0.75 } },
    { "category": "occasion", "tags": ["gifting_general"], "confidence_scores": { "gifting_general": 0.9 } },
    { "category": "mood", "tags": ["joyful_fun"], "confidence_scores": { "joyful_fun": 0.82 } },
    { "category": "product_type", "tags": ["gift_bag_medium"], "confidence_scores": { "gift_bag_medium": 0.78 } }
  ],
  "validated_tags": {
    "season": [{ "value": "christmas", "confidence": 0.92, "parent": null }],
    "theme": [{ "value": "traditional", "confidence": 0.88, "parent": null }],
    "objects": [
      { "value": "gift_box", "confidence": 0.95, "parent": "objects_items" },
      { "value": "ribbon", "confidence": 0.9, "parent": "objects_items" },
      { "value": "holly", "confidence": 0.7, "parent": "plants_nature" }
    ],
    "dominant_colors": [
      { "value": "crimson", "confidence": 0.9, "parent": "red_family" },
      { "value": "gold_metallic", "confidence": 0.85, "parent": "metallic_family" }
    ],
    "design_elements": [{ "value": "foil_metallic", "confidence": 0.88, "parent": null }, { "value": "centered_motif", "confidence": 0.75, "parent": null }],
    "occasion": [{ "value": "gifting_general", "confidence": 0.9, "parent": null }],
    "mood": [{ "value": "joyful_fun", "confidence": 0.82, "parent": null }],
    "product_type": [{ "value": "gift_bag_medium", "confidence": 0.78, "parent": "gift_bag" }]
  },
  "flagged_tags": [],
  "tag_record": {
    "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "season": ["christmas"],
    "theme": ["traditional"],
    "objects": [{ "parent": "objects_items", "child": "gift_box" }, { "parent": "objects_items", "child": "ribbon" }, { "parent": "plants_nature", "child": "holly" }],
    "dominant_colors": [{ "parent": "red_family", "child": "crimson" }, { "parent": "metallic_family", "child": "gold_metallic" }],
    "design_elements": ["foil_metallic", "centered_motif"],
    "occasion": ["gifting_general"],
    "mood": ["joyful_fun"],
    "product_type": { "parent": "gift_bag", "child": "gift_bag_medium" },
    "needs_review": false,
    "processed_at": "2025-03-17T12:00:00.000000+00:00"
  },
  "needs_review": false,
  "processing_status": "complete"
}
```

See [05-agent-data-models.md](05-agent-data-models.md) for the Pydantic models that produce these shapes.
