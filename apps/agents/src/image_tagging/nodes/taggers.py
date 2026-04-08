"""Category tagger nodes: run_tagger (generic) + tag_season (spec 4.3)."""
import asyncio
import json
from typing import Any

from langchain_openai import ChatOpenAI

from ..prompts.tagger import build_tagger_prompt
from ..schemas.models import TagResult, TaggerOutput
from ..schemas.states import ImageTaggingState
from ..settings import OPENAI_API_KEY, OPENAI_MODEL
from ..taxonomy import get_flat_values, TAXONOMY


def _parse_tagger_response(text: str) -> TaggerOutput | None:
    """Parse LLM response into TaggerOutput."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    try:
        data = json.loads(stripped)
        return TaggerOutput(
            tags=data.get("tags", []),
            confidence_scores=data.get("confidence_scores", {}),
            reasoning=data.get("reasoning", ""),
        )
    except Exception:
        return None


async def run_tagger(
    state: ImageTaggingState,
    category: str,
    instructions: str | None = None,
    max_tags: int | None = None,
) -> dict[str, Any]:
    """Generic tagger: vision_description + category → TagResult appended to partial_tags."""
    description = state.get("vision_description") or ""
    allowed = get_flat_values(category) if category in TAXONOMY else []
    if not allowed:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}

    prompt = build_tagger_prompt(description, category, allowed, instructions)
    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
    text = None
    for attempt in range(3):
        try:
            response = await llm.ainvoke([{"role": "user", "content": prompt}])
            text = response.content if isinstance(response.content, str) else str(response.content)
            break
        except Exception:
            if attempt < 2:
                await asyncio.sleep(1 * (2**attempt))
            else:
                return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}
    if text is None:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}

    out = _parse_tagger_response(text)
    if not out:
        return {"partial_tags": [TagResult(category=category, tags=[], confidence_scores={}).model_dump()]}

    # Filter to allowed only and confidence > 0.5
    tags = [t for t in out.tags if t in allowed]
    confidence_scores = {k: v for k, v in out.confidence_scores.items() if k in allowed and v > 0.5}
    tags = [t for t in tags if confidence_scores.get(t, 0) > 0.5]

    # Optional cap (e.g. MAX_COLORS=5, MAX_OBJECTS=10)
    if max_tags is not None and len(tags) > max_tags:
        sorted_tags = sorted(tags, key=lambda t: confidence_scores.get(t, 0), reverse=True)
        tags = sorted_tags[:max_tags]
        confidence_scores = {k: v for k, v in confidence_scores.items() if k in tags}

    result = TagResult(category=category, tags=tags, confidence_scores=confidence_scores)
    return {"partial_tags": [result.model_dump()]}


async def tag_season(state: ImageTaggingState) -> dict[str, Any]:
    return await run_tagger(state, "season")


async def tag_theme(state: ImageTaggingState) -> dict[str, Any]:
    return await run_tagger(
        state, "theme",
        instructions="Select all aesthetic themes that apply.",
    )


async def tag_objects(state: ImageTaggingState) -> dict[str, Any]:
    from ..configuration import MAX_OBJECTS
    return await run_tagger(
        state, "objects",
        instructions="Select all visible objects and subjects. For hierarchical categories, return the child values (e.g. santa, reindeer, ribbon).",
        max_tags=MAX_OBJECTS,
    )


async def tag_colors(state: ImageTaggingState) -> dict[str, Any]:
    from ..configuration import MAX_COLORS
    return await run_tagger(
        state, "dominant_colors",
        instructions="Select up to 5 dominant colors. Return the specific shade names (e.g. crimson, navy).",
        max_tags=MAX_COLORS,
    )


async def tag_design(state: ImageTaggingState) -> dict[str, Any]:
    return await run_tagger(
        state, "design_elements",
        instructions="Select all applicable patterns, textures, layout features, and typography.",
    )


async def tag_occasion(state: ImageTaggingState) -> dict[str, Any]:
    return await run_tagger(
        state, "occasion",
        instructions="Select all applicable occasions or use cases.",
    )


async def tag_mood(state: ImageTaggingState) -> dict[str, Any]:
    return await run_tagger(
        state, "mood",
        instructions="Select all applicable moods or tones.",
    )


async def tag_product(state: ImageTaggingState) -> dict[str, Any]:
    return await run_tagger(
        state, "product_type",
        instructions="Select the single most likely product type. Return one specific child value (e.g. gift_bag_medium, wrapping_paper_roll).",
        max_tags=1,
    )


TAGGER_NODE_NAMES = [
    "season_tagger", "theme_tagger", "objects_tagger", "color_tagger",
    "design_tagger", "occasion_tagger", "mood_tagger", "product_tagger",
]

ALL_TAGGERS = {
    "season_tagger": tag_season,
    "theme_tagger": tag_theme,
    "objects_tagger": tag_objects,
    "color_tagger": tag_colors,
    "design_tagger": tag_design,
    "occasion_tagger": tag_occasion,
    "mood_tagger": tag_mood,
    "product_tagger": tag_product,
}
