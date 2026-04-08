"""Category tagger prompt builder (spec 6.2)."""


def build_tagger_prompt(
    description: str,
    category: str,
    allowed_values: list[str],
    instructions: str | None = None,
) -> str:
    """Build system prompt for a category tagger node."""
    values_str = ", ".join(allowed_values)
    base = f"""You are a product tagging assistant. Based on the image description below,
select the most applicable tags for the "{category}" category.

Rules:
- Only use values from the provided allowed_values list
- Return tags as a JSON object with this exact structure:
  {{"tags": ["value1", "value2"], "confidence_scores": {{"value1": 0.95, "value2": 0.72}}, "reasoning": "..."}}
- Include a tag only if confidence > 0.5
- For confidence: 0.9+ = clearly visible, 0.7–0.9 = likely present, 0.5–0.7 = possibly present
- Return ONLY valid JSON, no markdown

Allowed values: {values_str}

Image description:
{description}"""
    if instructions:
        base += f"\n\nAdditional instructions: {instructions}"
    return base
