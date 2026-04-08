# Lab 20 — Prompts and LLM Calls

**Estimated time:** 25 min  
**Difficulty:** Beginner

The **vision** node uses **VISION_ANALYZER_PROMPT** from prompts/system.py: role, JSON structure (visual_description, dominant_mood, visible_subjects, etc.), and "return only valid JSON." The **taggers** use **build_tagger_prompt** from prompts/tagger.py: role, category, allowed values, rules (JSON shape, confidence > 0.5, confidence scale), image description, and optional instructions. **ChatOpenAI** is configured with OPENAI_MODEL and OPENAI_API_KEY. This lab summarizes the prompts and LLM usage; see Labs 05 and 07 for execution flow.

---

## Learning objectives

- Know the structure of **VISION_ANALYZER_PROMPT** and which field becomes vision_description for the taggers.
- Know **build_tagger_prompt** parameters and the confidence scale in the prompt.
- See where ChatOpenAI is instantiated (vision and taggers) and with what settings.

---

## prompts/system.py

**VISION_ANALYZER_PROMPT** — "You are a visual product analyst... Return ONLY valid JSON" with keys: visual_description (2–3 sentences), dominant_mood, visible_subjects, color_observations, design_observations, seasonal_indicators, style_indicators, text_present. The parser maps **visual_description** to **vision_description** in state for the taggers.

**Source:** [backend/src/image_tagging/prompts/system.py](../../backend/src/image_tagging/prompts/system.py)

---

## prompts/tagger.py

**build_tagger_prompt(description, category, allowed_values, instructions=None)** — F-string with: role ("product tagging assistant"), category name, rules (only allowed values, JSON with tags, confidence_scores, reasoning, confidence > 0.5, scale 0.9+ / 0.7–0.9 / 0.5–0.7), "Return ONLY valid JSON", allowed values list, image description, and optional additional instructions.

**Source:** [backend/src/image_tagging/prompts/tagger.py](../../backend/src/image_tagging/prompts/tagger.py)

---

## ChatOpenAI usage

**Vision (vision.py):** ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY). ainvoke([SystemMessage(VISION_ANALYZER_PROMPT), HumanMessage(content=[text, image_url])]). **Taggers (taggers.py):** Same model; ainvoke([{"role": "user", "content": prompt}]) with prompt from build_tagger_prompt. Both use retry with exponential backoff (1 s, 2 s).

---

## Lab summary

- Vision prompt defines JSON and visual_description. Tagger prompt defines category, allowed values, confidence scale, and JSON shape. ChatOpenAI is used for both with the same model and key; vision sends multimodal message, taggers send text-only.

---

## Next

Appendices: [A-glossary.md](A-glossary.md), [B-full-state-tracker.md](B-full-state-tracker.md), [C-file-map.md](C-file-map.md).
