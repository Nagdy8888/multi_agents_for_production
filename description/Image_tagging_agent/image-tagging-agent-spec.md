# Technical Spec: Image Tagging Agent (LangGraph)

> **Purpose:** Automatically tag product images (gift bags, gift cards, etc.) on upload to power a standardized, tag-based internal search engine.
> **Version:** 1.0 | **Status:** Draft

---

## 1. Overview

When an image is uploaded to the artwork database, this agent processes it through a multi-category tagging pipeline and writes structured, predefined tags back to the record. Tags are strictly enum-based — no free-form values — ensuring consistency across data entry, dropdowns, and search.

### 1.1 Key Constraints

- All tag values are **predefined enums** (no free-form text)
- Some categories are **hierarchical** (parent → child) — both levels are indexed for search
- Tags include a **confidence score** (0.0–1.0); low-confidence tags are flagged for human review
- The agent is designed for **batch and single-image** workflows

---

## 2. System Architecture

### 2.1 High-Level Flow

```
Image Upload
    │
    ▼
[image_preprocessor]      Validate, resize, extract metadata
    │
    ▼
[vision_analyzer]         Single LLM vision pass → rich structured description
    │
    ├──────────────────────────────────────────────────────┐
    ▼                                                      ▼
[Parallel Tagging Subgraph — via LangGraph Send API]
    │
    ├── [season_tagger]
    ├── [theme_tagger]
    ├── [objects_tagger]
    ├── [color_tagger]
    ├── [design_tagger]
    ├── [occasion_tagger]
    ├── [mood_tagger]
    └── [product_tagger]
    │
    ▼
[tag_validator]           Validate all tags against taxonomy enums
    │
    ▼
[confidence_filter]       Flag tags below threshold for human review
    │
    ▼
[tag_aggregator]          Assemble final TagRecord output
    │
    ▼
Database Write / Search Index
```

### 2.2 LangGraph Graph Definition (Pseudocode)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

builder = StateGraph(ImageTaggingState)

builder.add_node("image_preprocessor", preprocess_image)
builder.add_node("vision_analyzer", analyze_image)
builder.add_node("season_tagger", tag_season)
builder.add_node("theme_tagger", tag_theme)
builder.add_node("objects_tagger", tag_objects)
builder.add_node("color_tagger", tag_colors)
builder.add_node("design_tagger", tag_design)
builder.add_node("occasion_tagger", tag_occasion)
builder.add_node("mood_tagger", tag_mood)
builder.add_node("product_tagger", tag_product)
builder.add_node("tag_validator", validate_tags)
builder.add_node("confidence_filter", filter_by_confidence)
builder.add_node("tag_aggregator", aggregate_tags)

builder.add_edge(START, "image_preprocessor")
builder.add_edge("image_preprocessor", "vision_analyzer")

# Fan-out to all parallel taggers
builder.add_conditional_edges(
    "vision_analyzer",
    fan_out_to_taggers,  # returns list of Send() calls
    ["season_tagger", "theme_tagger", "objects_tagger",
     "color_tagger", "design_tagger", "occasion_tagger",
     "mood_tagger", "product_tagger"]
)

# All taggers fan-in to validator
for tagger in TAGGER_NODES:
    builder.add_edge(tagger, "tag_validator")

builder.add_edge("tag_validator", "confidence_filter")
builder.add_edge("confidence_filter", "tag_aggregator")
builder.add_edge("tag_aggregator", END)

graph = builder.compile()
```

---

## 3. State Schema

```python
from typing import Annotated
from langgraph.graph.message import add_messages
import operator

class ImageTaggingState(TypedDict):
    # Input
    image_id: str
    image_url: str                        # S3 or CDN URL
    image_base64: Optional[str]           # For direct upload
    metadata: dict                        # File size, dimensions, format

    # Vision pass output
    vision_description: str               # Rich textual description from LLM
    vision_raw_tags: dict                 # Raw LLM output before validation

    # Per-tagger partial results (merged via reducer)
    partial_tags: Annotated[list[TagResult], operator.add]

    # Post-validation
    validated_tags: dict[str, list[ValidatedTag]]
    flagged_tags: list[FlaggedTag]        # Below confidence threshold

    # Final output
    tag_record: TagRecord
    processing_status: Literal["pending", "complete", "needs_review", "failed"]
    error: Optional[str]


class TagResult(TypedDict):
    category: str
    tags: list[str]
    confidence_scores: dict[str, float]   # {tag_value: 0.0–1.0}


class ValidatedTag(TypedDict):
    value: str
    confidence: float
    parent: Optional[str]                 # For hierarchical tags


class FlaggedTag(TypedDict):
    category: str
    value: str
    confidence: float
    reason: str


class TagRecord(TypedDict):
    image_id: str
    season: list[str]
    theme: list[str]
    objects: list[HierarchicalTag]
    dominant_colors: list[HierarchicalTag]
    design_elements: list[str]
    occasion: list[str]
    mood: list[str]
    product_type: HierarchicalTag
    needs_review: bool
    processed_at: str                     # ISO timestamp


class HierarchicalTag(TypedDict):
    parent: str
    child: str
```

---

## 4. Node Specifications

### 4.1 `image_preprocessor`

**Input:** Raw image URL or base64  
**Output:** Normalized image ready for vision model

- Validate image format (JPG, PNG, WEBP)
- Resize to max 1024px on the long edge (vision model optimization)
- Extract EXIF/file metadata
- Convert to base64 if URL-based

---

### 4.2 `vision_analyzer`

**Input:** Preprocessed image  
**Output:** `vision_description` (string) + `vision_raw_tags` (dict)

Single LLM call using Claude Vision or GPT-4o. This is the only call that processes the raw image; all downstream taggers work from the text description to reduce cost and latency.

**System Prompt Template:**
```
You are a product image analyst specializing in gift products (gift bags, gift cards, wrapping paper, etc.).
Analyze the provided image and return a detailed JSON description covering:
- Overall visual impression and mood
- Visible objects, characters, and subjects
- Color palette (dominant and accent colors)
- Design patterns and decorative elements
- Seasonal or holiday indicators
- Style and artistic approach
- Text or typography present (if any)

Return ONLY valid JSON. Do not include any other text.
```

---

### 4.3 Parallel Taggers (Generic Pattern)

Each tagger node receives the `vision_description` and runs a structured extraction prompt against its specific tag taxonomy.

**Pattern for each tagger:**

```python
async def tag_season(state: ImageTaggingState) -> dict:
    result = await llm.ainvoke(
        build_tagger_prompt(
            description=state["vision_description"],
            category="season",
            allowed_values=TAXONOMY["season"],
            instructions="Select ALL seasons/holidays that apply. An image can have multiple."
        )
    )
    return {
        "partial_tags": [TagResult(
            category="season",
            tags=result.tags,
            confidence_scores=result.confidence_scores
        )]
    }
```

**Structured output schema (per tagger):**
```python
class TaggerOutput(BaseModel):
    tags: list[str]              # Must be from allowed_values only
    confidence_scores: dict[str, float]
    reasoning: str               # Brief explanation (for review/debug)
```

---

### 4.4 `tag_validator`

- Checks every returned tag value against the master taxonomy enum
- Rejects any value not in the predefined list (does NOT hallucinate corrections)
- For hierarchical tags: validates both parent and child are a valid pair
- Logs all rejections to `flagged_tags`

---

### 4.5 `confidence_filter`

**Threshold:** `CONFIDENCE_THRESHOLD = 0.65` (configurable per category)

- Tags above threshold → included in `validated_tags`
- Tags below threshold → moved to `flagged_tags` with `reason: "low_confidence"`
- If ≥3 tags are flagged in any single category → set `needs_review: true`

---

### 4.6 `tag_aggregator`

Assembles the final `TagRecord` from validated tags. Sets `processing_status`:

- `complete` — all categories tagged, nothing flagged
- `needs_review` — some tags flagged, human review needed
- `failed` — critical error (e.g., image unreadable, vision model failure)

---

## 5. Tag Taxonomy

> All values below are the canonical enum lists. These same lists power the search dropdowns and data entry forms.

---

### 5.1 Season / Holiday
**Type:** Flat multi-select

| Value | Notes |
|---|---|
| `christmas` | |
| `hanukkah` | |
| `kwanzaa` | |
| `new_years` | |
| `valentines_day` | |
| `st_patricks_day` | |
| `easter` | |
| `mothers_day` | |
| `fathers_day` | |
| `fourth_of_july` | |
| `halloween` | |
| `thanksgiving` | |
| `diwali` | |
| `eid` | |
| `birthday` | |
| `wedding_anniversary` | |
| `baby_shower` | |
| `graduation` | |
| `all_occasion` | Generic, non-seasonal |

**Search behavior:** Selecting `christmas` returns images tagged with `christmas`. No implicit cross-tag inheritance (handled by object tagging — a `santa` object tag means it will also appear in christmas-related searches).

---

### 5.2 Theme / Aesthetic
**Type:** Flat multi-select

| Value | Notes |
|---|---|
| `whimsical` | Playful, cartoonish, fantastical |
| `traditional` | Classic, conventional holiday styles |
| `modern` | Clean, contemporary design sensibility |
| `minimalist` | Simple, sparse, negative space-heavy |
| `elegant_luxury` | Refined, premium, gold/metallic emphasis |
| `rustic_farmhouse` | Natural textures, country, warm tones |
| `vintage_retro` | Nostalgic, aged aesthetics |
| `kawaii_cute` | Japanese cute style, soft pastel, big-eyed characters |
| `floral_botanical` | Flowers, plants, nature patterns |
| `tropical` | Bright, summery, beach, exotic flora/fauna |
| `religious` | Faith-based imagery |
| `feminine` | Soft, pink, delicate motifs |
| `masculine` | Bold, dark, geometric |
| `kids_juvenile` | Bright primary colors, playful typography |
| `nature_organic` | Earth tones, leaves, forests, animals |
| `abstract` | Non-representational, artistic patterns |
| `typographic` | Text-driven, lettering as the primary design |
| `photorealistic` | Photographic or highly realistic illustration |

---

### 5.3 Objects & Subjects
**Type:** Hierarchical (Category → Item), multi-select at both levels

#### Category: `characters`
`santa` · `mrs_claus` · `elf` · `reindeer` · `snowman` · `grinch` · `easter_bunny` · `witch` · `ghost` · `angel` · `cupid` · `gnome` · `fairy` · `mermaid` · `unicorn` · `dragon` · `superhero`

#### Category: `animals`
`bear` · `rabbit` · `cat` · `dog` · `bird` · `fox` · `owl` · `penguin` · `deer` · `sheep` · `squirrel` · `butterfly` · `bee` · `flamingo` · `sloth` · `dinosaur`

#### Category: `plants_nature`
`christmas_tree` · `wreath` · `holly` · `mistletoe` · `flower` · `rose` · `sunflower` · `leaf` · `cactus` · `pumpkin` · `tree` · `mushroom` · `rainbow` · `cloud` · `sun` · `moon` · `star` · `snowflake` · `fireworks`

#### Category: `food_drink`
`cake` · `cupcake` · `cookie` · `candy` · `chocolate` · `wine` · `champagne` · `coffee` · `gingerbread` · `ice_cream` · `fruit` · `pie`

#### Category: `objects_items`
`gift_box` · `ribbon` · `bow` · `balloon` · `candle` · `ornament` · `stocking` · `heart` · `diamond` · `crown` · `key` · `crayon` · `pencil` · `book` · `camera` · `bicycle` · `car` · `boat` · `umbrella` · `envelope` · `trophy`

#### Category: `places_architecture`
`house` · `castle` · `hotel` · `cityscape` · `barn` · `beach` · `forest` · `mountain` · `space` · `church` · `barn`

#### Category: `symbols_icons`
`cross` · `star_of_david` · `crescent` · `peace_sign` · `infinity` · `anchor` · `compass` · `musical_note` · `sports_ball`

**Search behavior:** Both parent and child are indexed. Searching `characters` returns all items with any character. Searching `santa` returns only images with that specific tag.

---

### 5.4 Dominant Colors
**Type:** Hierarchical (Color Family → Specific Shade), up to 5 colors per image

#### `red_family`
`crimson` · `scarlet` · `cherry` · `burgundy` · `rose_red`

#### `pink_family`
`hot_pink` · `blush` · `coral` · `salmon` · `bubblegum`

#### `orange_family`
`burnt_orange` · `peach` · `amber` · `tangerine`

#### `yellow_family`
`yellow` · `gold` · `mustard` · `lemon` · `cream_yellow`

#### `green_family`
`forest_green` · `mint` · `lime` · `sage` · `olive` · `emerald`

#### `blue_family`
`navy` · `sky_blue` · `teal` · `royal_blue` · `baby_blue` · `denim`

#### `purple_family`
`lavender` · `violet` · `plum` · `lilac` · `mauve`

#### `neutral_family`
`white` · `off_white` · `beige` · `tan` · `brown` · `gray_light` · `gray_dark` · `black`

#### `metallic_family`
`gold_metallic` · `silver_metallic` · `rose_gold` · `bronze` · `copper`

**Search behavior:** Searching `red_family` returns all images with any red shade. Searching `crimson` returns only images with that specific shade.

---

### 5.5 Design Elements & Style
**Type:** Flat multi-select (can apply multiple)

#### Patterns
`stripes` · `checkered` · `plaid_tartan` · `polka_dots` · `argyle` · `houndstooth` · `chevron` · `herringbone` · `ikat` · `paisley` · `geometric` · `abstract_pattern` · `floral_pattern` · `toile` · `damask`

#### Textures & Finishes
`glitter_sparkle` · `foil_metallic` · `watercolor` · `hand_drawn_sketch` · `embossed_effect` · `linen_texture` · `kraft_texture`

#### Layout & Composition
`all_over_print` · `centered_motif` · `scattered_elements` · `border_frame` · `tiled_repeat` · `asymmetric` · `symmetrical` · `diagonal_layout`

#### Typography Present
`handlettering` · `serif_type` · `sans_serif_type` · `script_cursive` · `block_letters` · `no_text`

---

### 5.6 Occasion / Use Case *(Proposed)*
**Type:** Flat multi-select

`gifting_general` · `gifting_premium` · `corporate_branded` · `party_supplies` · `wedding_event` · `kids_party` · `self_gifting` · `charitable_cause`

**Rationale:** Helps buyers filter by use context beyond just season (e.g., filtering for "corporate" narrows to professional-appropriate designs even among Christmas items).

---

### 5.7 Mood / Tone *(Proposed)*
**Type:** Flat multi-select

`joyful_fun` · `elegant_sophisticated` · `romantic` · `nostalgic_sentimental` · `spooky_dark` · `peaceful_calm` · `bold_energetic` · `cozy_warm` · `fresh_bright`

**Rationale:** Critical for search queries like "give me something elegant for Christmas" vs. "fun whimsical Valentine's." Pairs with theme for compound filtering.

---

### 5.8 Product Type *(Proposed)*
**Type:** Hierarchical (required, single-select)

#### `gift_bag`
`gift_bag_small` *(≤6")* · `gift_bag_medium` *(6–9")* · `gift_bag_large` *(9–12")* · `gift_bag_extra_large` · `wine_bag` · `bottle_bag` · `tote_style`

#### `gift_card_envelope`
`standard_gift_card` · `money_holder` · `oversized_card` · `boxed_notecard`

#### `gift_wrap`
`wrapping_paper_sheet` · `wrapping_paper_roll` · `tissue_paper` · `gift_tissue_set`

#### `gift_box`
`box_lid` · `collapsible_box` · `window_box`

#### `accessory`
`ribbon_spool` · `bow_pack` · `tag_label` · `filler_shred`

**Rationale:** Ensures product type is always known for filtering (e.g., "show me all medium gift bags with a Christmas theme and navy color family").

---

## 6. LLM Prompt Templates

### 6.1 Vision Analyzer Prompt

```
System:
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

### 6.2 Category Tagger Prompt Template

```
System:
You are a product tagging assistant. Based on the image description below,
select the most applicable tags for the "{category}" category.

Rules:
- Only use values from the provided allowed_values list
- Return tags as a JSON object with this exact structure:
  {"tags": ["value1", "value2"], "confidence_scores": {"value1": 0.95, "value2": 0.72}, "reasoning": "..."}
- Include a tag only if confidence > 0.5
- For confidence: 0.9+ = clearly visible, 0.7–0.9 = likely present, 0.5–0.7 = possibly present
- Return ONLY valid JSON, no markdown

Allowed values: {allowed_values}

Image description:
{vision_description}
```

---

## 7. Configuration

```python
# config.py

CONFIDENCE_THRESHOLD = 0.65       # Minimum to include a tag in final record
NEEDS_REVIEW_THRESHOLD = 3        # Number of low-conf tags before flagging record
MAX_COLORS = 5                    # Max dominant colors to tag per image
MAX_OBJECTS = 10                  # Max object tags per image
VISION_MODEL = "claude-opus-4"    # Or "gpt-4o" — vision pass only
TAGGER_MODEL = "claude-sonnet-4"  # Cheaper model for structured extraction

CATEGORY_CONFIDENCE_OVERRIDES = {
    "product_type": 0.80,         # Higher bar — product type should be certain
    "season": 0.60,               # Lower bar — seasonal hints still useful
}
```

---

## 8. Input / Output Contract

### 8.1 Input

```json
{
  "image_id": "artwork_00423",
  "image_url": "https://s3.amazonaws.com/nalm-artwork/artwork_00423.jpg",
  "metadata": {
    "filename": "GiftBag_Christmas_Plaid.jpg",
    "format": "JPEG",
    "width": 2400,
    "height": 3000
  }
}
```

### 8.2 Output (`TagRecord`)

```json
{
  "image_id": "artwork_00423",
  "season": ["christmas"],
  "theme": ["traditional", "rustic_farmhouse"],
  "objects": [
    { "parent": "plants_nature", "child": "christmas_tree" },
    { "parent": "plants_nature", "child": "holly" },
    { "parent": "objects_items", "child": "ribbon" }
  ],
  "dominant_colors": [
    { "parent": "red_family", "child": "crimson" },
    { "parent": "green_family", "child": "forest_green" },
    { "parent": "neutral_family", "child": "off_white" }
  ],
  "design_elements": ["plaid_tartan", "all_over_print"],
  "occasion": ["gifting_general"],
  "mood": ["cozy_warm", "nostalgic_sentimental"],
  "product_type": { "parent": "gift_bag", "child": "gift_bag_medium" },
  "needs_review": false,
  "processed_at": "2025-03-16T10:42:00Z"
}
```

---

## 9. Search Engine Integration

### 9.1 Tag Indexing Strategy

All tags are stored as a flat indexed array **alongside** the structured object, enabling both precision and fuzzy search:

```json
{
  "image_id": "artwork_00423",
  "search_index": [
    "christmas", "traditional", "rustic_farmhouse",
    "plants_nature", "christmas_tree", "holly",
    "objects_items", "ribbon",
    "red_family", "crimson", "green_family", "forest_green",
    "neutral_family", "off_white",
    "plaid_tartan", "all_over_print",
    "gifting_general", "cozy_warm", "nostalgic_sentimental",
    "gift_bag", "gift_bag_medium"
  ]
}
```

### 9.2 Search Query Examples

| Search Query | Matching Logic |
|---|---|
| `santa` | `objects.child = "santa"` |
| `christmas` | `season = "christmas"` OR `search_index contains "christmas"` |
| `red gift bag` | `dominant_colors.parent = "red_family"` AND `product_type.parent = "gift_bag"` |
| `whimsical halloween medium` | `theme = "whimsical"` AND `season = "halloween"` AND `product_type.child = "gift_bag_medium"` |
| `all character tags` | `objects.parent = "characters"` |

### 9.3 Implicit Tag Relationships (Search-Level, Not Agent-Level)

The agent does **not** infer relationships — it only applies explicit tags. Cross-category search relationships are handled at the search layer:

- `christmas` search → optionally also surface images where `objects` contains `santa`, `reindeer`, `christmas_tree` (configurable "expand search" UI toggle)
- `valentine` search → optionally also surface images with `hearts` object tag + `romantic` mood

---

## 10. Error Handling

| Scenario | Behavior |
|---|---|
| Image unreadable / corrupt | `status: "failed"`, error logged, no tags written |
| Vision model timeout | Retry × 2 with exponential backoff, then fail |
| All tagger nodes return empty | `needs_review: true`, partial tags saved if any |
| Tag value not in taxonomy | Rejected silently, logged to `flagged_tags` |
| Confidence below threshold | Moved to `flagged_tags`, not in final record |
| Partial tagger failure | Other taggers complete normally; failed category flagged |

---

## 11. Human Review Queue

Records with `needs_review: true` enter a review queue where an operator can:

1. **Confirm** flagged tags (promote to `validated_tags`)
2. **Reject** flagged tags (remove)
3. **Add missing tags** manually via the same dropdown lists
4. **Override** any agent-assigned tag

The review interface should display `reasoning` text from each tagger output to help the reviewer understand why a tag was or wasn't applied.

---

## 12. Future Enhancements

| Enhancement | Description |
|---|---|
| **Active Learning Loop** | Reviewer corrections feed back into few-shot examples to improve accuracy over time |
| **Artwork Similarity Search** | Use vision embeddings (e.g., CLIP) alongside tags for visual similarity ("find me more bags that look like this one") |
| **Bulk Retagging** | When taxonomy is updated (new values added), trigger a retagging job across historical records |
| **Confidence Calibration** | Track human review correction rate per category; auto-adjust thresholds |
| **License / IP Flag** | Add a tagger node that flags images containing potentially licensed characters (Mickey, Peppa Pig, etc.) for legal review |

---

## 13. Tech Stack

| Component | Choice | Rationale |
|---|---|---|
| Agent Framework | LangGraph | Native parallel fan-out, state management, interrupt/resume for review queue |
| Vision LLM | Claude claude-opus-4 | Best-in-class image understanding |
| Extraction LLM | Claude claude-sonnet-4 | Cost-efficient structured output |
| Structured Output | Pydantic + `.with_structured_output()` | Type-safe tag extraction |
| Storage | PostgreSQL (JSONB) + search index array column | Flexible tag querying |
| Search | PostgreSQL full-text + GIN index on `search_index` array | Start simple; upgrade to Elasticsearch if needed |
| Deployment | Python service on existing ECS Fargate | Aligns with Nalm Portal infra |

---

*End of Spec*
