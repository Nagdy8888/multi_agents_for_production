"""Vision analyzer node: single LLM vision pass → vision_description + vision_raw_tags (spec 4.2)."""
import asyncio
import json
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..prompts.system import VISION_ANALYZER_PROMPT
from ..schemas.states import ImageTaggingState
from ..settings import OPENAI_API_KEY, OPENAI_MODEL


def _parse_vision_response(text: str) -> tuple[str, dict]:
    """Extract JSON from response; return (visual_description, raw_dict)."""
    description = ""
    raw = {}
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    try:
        raw = json.loads(stripped)
        description = raw.get("visual_description", "")
    except json.JSONDecodeError:
        description = stripped
    return description, raw


async def vision_analyzer(state: ImageTaggingState) -> dict[str, Any]:
    """Run GPT-4o vision on image_base64; return vision_description and vision_raw_tags."""
    image_base64 = state.get("image_base64")
    if not image_base64:
        return {
            "vision_description": "",
            "vision_raw_tags": {},
            "processing_status": "failed",
            "error": "Missing image_base64",
        }

    mime = "image/jpeg"
    data_uri = f"data:{mime};base64,{image_base64}"

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
    messages = [
        SystemMessage(content=VISION_ANALYZER_PROMPT),
        HumanMessage(
            content=[
                {"type": "text", "text": "Analyze this image and return the JSON object."},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ]
        ),
    ]

    for attempt in range(3):
        try:
            response = await llm.ainvoke(messages)
            text = response.content if isinstance(response.content, str) else str(response.content)
            break
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(1 * (2**attempt))
            else:
                return {
                    "vision_description": "",
                    "vision_raw_tags": {},
                    "processing_status": "failed",
                    "error": str(e),
                }

    description, raw = _parse_vision_response(text)
    return {
        "vision_description": description,
        "vision_raw_tags": raw,
    }
