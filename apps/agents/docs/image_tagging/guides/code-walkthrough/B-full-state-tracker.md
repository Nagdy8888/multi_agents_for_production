# Appendix B — Full State Tracker

This appendix shows **ImageTaggingState** at each node boundary during a single image analysis. Keys that are set are shown with example values; keys not yet set are omitted (or shown as "—"). Use this to see how data flows through the pipeline.

---

## 1. Initial state (server, before graph)

From Lab 02. Only these keys exist.

```json
{
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "image_url": "http://localhost:8000/uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "partial_tags": []
}
```

---

## 2. After preprocessor (Lab 04)

image_base64 may be replaced (resized); metadata added.

```json
{
  "image_id": "a1b2c3d4-...",
  "image_url": "http://localhost:8000/uploads/...",
  "image_base64": "/9j/4AAQSkZJRg...",
  "metadata": { "width": 800, "height": 600, "format": "JPEG" },
  "partial_tags": []
}
```

---

## 3. After vision_analyzer (Lab 05)

vision_description and vision_raw_tags added.

```json
{
  "image_id": "a1b2c3d4-...",
  "image_url": "http://localhost:8000/uploads/...",
  "image_base64": "/9j/4AAQ...",
  "metadata": { "width": 800, "height": 600, "format": "JPEG" },
  "vision_description": "A festive gift bag with red and gold design, ribbon and holly.",
  "vision_raw_tags": {
    "visual_description": "A festive gift bag...",
    "dominant_mood": "festive",
    "visible_subjects": ["gift bag", "ribbon", "holly"],
    "color_observations": "Red, gold, green",
    "seasonal_indicators": "Christmas"
  },
  "partial_tags": []
}
```

---

## 4. After all 8 taggers (Lab 06–07)

partial_tags has 8 elements (reducer merged). Other keys unchanged.

```json
{
  "image_id": "a1b2c3d4-...",
  "image_url": "http://localhost:8000/uploads/...",
  "image_base64": "/9j/4AAQ...",
  "metadata": { "width": 800, "height": 600, "format": "JPEG" },
  "vision_description": "A festive gift bag...",
  "vision_raw_tags": { ... },
  "partial_tags": [
    { "category": "season", "tags": ["christmas"], "confidence_scores": { "christmas": 0.92 } },
    { "category": "theme", "tags": ["traditional", "elegant_luxury"], "confidence_scores": { ... } },
    { "category": "objects", "tags": ["ribbon", "holly"], "confidence_scores": { ... } },
    { "category": "dominant_colors", "tags": ["crimson", "gold_metallic"], "confidence_scores": { ... } },
    { "category": "design_elements", "tags": ["foil_metallic", "centered_motif"], "confidence_scores": { ... } },
    { "category": "occasion", "tags": ["gifting_general"], "confidence_scores": { ... } },
    { "category": "mood", "tags": ["joyful_fun"], "confidence_scores": { ... } },
    { "category": "product_type", "tags": ["gift_bag_medium"], "confidence_scores": { ... } }
  ]
}
```

---

## 5. After tag_validator (Lab 08)

validated_tags and flagged_tags added; partial_tags unchanged.

```json
{
  "image_id": "a1b2c3d4-...",
  "image_url": "http://localhost:8000/uploads/...",
  "image_base64": "/9j/4AAQ...",
  "metadata": { ... },
  "vision_description": "A festive gift bag...",
  "vision_raw_tags": { ... },
  "partial_tags": [ ... ],
  "validated_tags": {
    "season": [{ "value": "christmas", "confidence": 0.92, "parent": null }],
    "theme": [{ "value": "traditional", "confidence": 0.88, "parent": null }, { "value": "elegant_luxury", "confidence": 0.72, "parent": null }],
    "objects": [{ "value": "ribbon", "confidence": 0.9, "parent": "objects_items" }, { "value": "holly", "confidence": 0.7, "parent": "objects_natural" }],
    "dominant_colors": [ ... ],
    "design_elements": [ ... ],
    "occasion": [ ... ],
    "mood": [ ... ],
    "product_type": [ ... ]
  },
  "flagged_tags": []
}
```

---

## 6. After confidence_filter (Lab 09)

validated_tags trimmed; some entries may move to flagged_tags with reason "low_confidence"; needs_review set if any flags.

```json
{
  "image_id": "a1b2c3d4-...",
  "image_url": "http://localhost:8000/uploads/...",
  "image_base64": "/9j/4AAQ...",
  "metadata": { ... },
  "vision_description": "A festive gift bag...",
  "vision_raw_tags": { ... },
  "partial_tags": [ ... ],
  "validated_tags": { "season": [...], "theme": [...], ... },
  "flagged_tags": [],
  "needs_review": false
}
```

---

## 7. After tag_aggregator (Lab 10)

tag_record and processing_status added. This is the final state returned by graph.ainvoke.

```json
{
  "image_id": "a1b2c3d4-...",
  "image_url": "http://localhost:8000/uploads/...",
  "image_base64": "/9j/4AAQ...",
  "metadata": { ... },
  "vision_description": "A festive gift bag...",
  "vision_raw_tags": { ... },
  "partial_tags": [ ... ],
  "validated_tags": { ... },
  "flagged_tags": [],
  "needs_review": false,
  "tag_record": {
    "image_id": "a1b2c3d4-...",
    "season": ["christmas"],
    "theme": ["traditional", "elegant_luxury"],
    "objects": [{ "parent": "objects_items", "child": "ribbon" }, { "parent": "objects_natural", "child": "holly" }],
    "dominant_colors": [ ... ],
    "design_elements": [ ... ],
    "occasion": [ ... ],
    "mood": [ ... ],
    "product_type": { "parent": "gift_bags", "child": "gift_bag_medium" },
    "needs_review": false,
    "processed_at": "2025-03-17T12:00:00.000000Z"
  },
  "processing_status": "complete"
}
```

---

## Summary

- **Initial:** image_id, image_url, image_base64, partial_tags.
- **After preprocessor:** + metadata (optional new image_base64).
- **After vision:** + vision_description, vision_raw_tags.
- **After taggers:** partial_tags has 8 elements.
- **After validator:** + validated_tags, flagged_tags.
- **After confidence:** validated_tags trimmed, flagged_tags possibly extended, + needs_review.
- **After aggregator:** + tag_record, processing_status. Server then uses this for DB and response (Lab 11).
