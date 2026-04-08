# Lab 19 — Taxonomy and Config

**Estimated time:** 20 min  
**Difficulty:** Beginner

The **taxonomy** defines allowed tag values per category: flat categories are lists; hierarchical categories are dicts (parent → list of children). **get_flat_values(category)** returns a flat list of allowed values (all children for hierarchical). **get_parent_for_child(category, child)** returns the parent key for hierarchical categories. **configuration.py** holds CONFIDENCE_THRESHOLD, CATEGORY_CONFIDENCE_OVERRIDES, MAX_COLORS, MAX_OBJECTS, and model settings. This lab summarizes taxonomy and config; see Labs 07–09 for usage.

---

## Learning objectives

- Understand **TAXONOMY** structure: flat (e.g. season, theme) vs hierarchical (objects, dominant_colors, product_type).
- See **get_flat_values** and **get_parent_for_child** and where they are used (taggers, validator, aggregator).
- See **configuration.py** constants used by confidence filter and taggers.

---

## taxonomy.py

**TAXONOMY** — Dict: category → list of strings (flat) or dict parent → list of children (hierarchical). **get_flat_values(category):** if list return it; if dict return all children from all parents. **get_parent_for_child(category, child):** for dict entries find the parent that contains child; return parent key or None.

**Source:** [backend/src/image_tagging/taxonomy.py](../../backend/src/image_tagging/taxonomy.py)

---

## configuration.py

**CONFIDENCE_THRESHOLD** = 0.65. **NEEDS_REVIEW_THRESHOLD** = 3. **MAX_COLORS** = 5, **MAX_OBJECTS** = 10. **CATEGORY_CONFIDENCE_OVERRIDES** = {"product_type": 0.80, "season": 0.60}. **VISION_MODEL**, **TAGGER_MODEL** from settings (OPENAI_MODEL).

**Source:** [backend/src/image_tagging/configuration.py](../../backend/src/image_tagging/configuration.py)

---

## Lab summary

- Taxonomy: flat vs hierarchical; get_flat_values and get_parent_for_child. Config: thresholds, overrides, max tags, model names.

---

## Next lab

[20-prompts-and-llm-calls.md](20-prompts-and-llm-calls.md)
