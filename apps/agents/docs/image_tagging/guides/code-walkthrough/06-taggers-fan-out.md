# Lab 06 — Taggers Fan-Out

**Estimated time:** 25 min  
**Difficulty:** Intermediate

After the vision node, the graph does not go to a single next node. It **fans out** to all 8 taggers in parallel. Each tagger receives the **same** state (with `vision_description`) and returns **one** item for `partial_tags`. LangGraph merges those 8 updates using the **reducer** so the state ends up with a list of 8 TagResults. This lab shows how that fan-out and merge work.

---

## Learning objectives

- See how **add_conditional_edges** with a function that returns a list of **Send** schedules multiple next nodes.
- Understand that each tagger gets the **same** state (the state after the vision node).
- Understand how the **reducer** (operator.add) merges 8 separate `partial_tags` updates into one list.

---

## Prerequisites

- [05-vision-calls-gpt4o.md](05-vision-calls-gpt4o.md) — state now has `vision_description` and `vision_raw_tags`; the conditional edge after vision_analyzer is about to run.

---

## Step 1 — Conditional edge after vision_analyzer

In the graph builder, the edge from the vision node is **conditional**: the next step is determined by calling a function with the current state. That function returns a list of **Send** objects.

**Snippet (lines 37–38 in graph_builder.py)**

```python
    builder.add_conditional_edges("vision_analyzer", fan_out_to_taggers)
    for name in TAGGER_NODE_NAMES:
        builder.add_edge(name, "tag_validator")
```

**What is happening**

- **add_conditional_edges("vision_analyzer", fan_out_to_taggers)** — When the vision_analyzer node finishes, LangGraph calls `fan_out_to_taggers(state)`. The return value tells it what to run next. Here we return a **list** of Send objects, so the runtime schedules **multiple** next nodes (all 8 taggers).
- **add_edge(name, "tag_validator")** for each tagger name — After **any** of the 8 taggers finishes, the next node is always `tag_validator`. The runtime waits until **all** 8 taggers have completed and their updates have been merged, then runs the validator **once** with the merged state.

**Source:** [backend/src/image_tagging/graph_builder.py](../../backend/src/image_tagging/graph_builder.py) (lines 37–39)

> **Glossary:** **fan-out** — From one node, branching to multiple next nodes that can run in parallel. **Send** — LangGraph’s way to say “run this node with this state.”

---

## Step 2 — fan_out_to_taggers returns one Send per tagger

The function receives the state (after the vision node) and returns a list of 8 Sends. Each Send targets one tagger and passes the **same** state.

**Snippet (lines 17–19 in graph_builder.py)**

```python
def fan_out_to_taggers(state: ImageTaggingState):
    """Return one Send per tagger so all 8 run in parallel."""
    return [Send(name, state) for name in TAGGER_NODE_NAMES]
```

**Snippet (lines 141–144 in taggers.py — TAGGER_NODE_NAMES)**

```python
TAGGER_NODE_NAMES = [
    "season_tagger", "theme_tagger", "objects_tagger", "color_tagger",
    "design_tagger", "occasion_tagger", "mood_tagger", "product_tagger",
]
```

**What is happening**

- **TAGGER_NODE_NAMES** — The 8 node names that were registered in the graph (they must match the keys in ALL_TAGGERS). The order determines the order in which the runtime schedules them; they may still run in parallel.
- **Send(name, state)** — Each Send says: run the node named `name` with this `state`. We pass the **same** state to every tagger: it contains `vision_description`, `vision_raw_tags`, `image_base64`, etc. No tagger sees another tagger’s output yet; they all read the same input.
- Returning a **list** of Sends tells LangGraph to run all of them. When using async, the runtime can run them concurrently. When all are done, it merges their returned state updates (using the reducer for `partial_tags`) and then runs the single next node: tag_validator.

**Source:** [backend/src/image_tagging/graph_builder.py](../../backend/src/image_tagging/graph_builder.py) (lines 17–19), [backend/src/image_tagging/nodes/taggers.py](../../backend/src/image_tagging/nodes/taggers.py) (lines 141–144)

> **State Tracker (input to each tagger):** Identical for all 8: `image_id`, `image_url`, `image_base64`, `metadata`, `vision_description`, `vision_raw_tags`, `partial_tags: []`. Each tagger only reads `vision_description` (and its category’s allowed values from the taxonomy).

---

## Step 3 — What each tagger returns

Each tagger is an async function that calls **run_tagger** with a category name and optional instructions/max_tags. It returns a dict with **one** key: `partial_tags` containing a **list of one** TagResult (one category).

**Conceptual return from each tagger**

```python
# season_tagger returns:
{"partial_tags": [{"category": "season", "tags": ["christmas"], "confidence_scores": {"christmas": 0.92}}]}

# theme_tagger returns:
{"partial_tags": [{"category": "theme", "tags": ["traditional", "elegant_luxury"], "confidence_scores": {...}}]}
# ... and so on for all 8.
```

**What is happening**

- Each tagger returns `{"partial_tags": [one_item]}`. The item is a TagResult (category, tags, confidence_scores) as a dict (e.g. from `.model_dump()`).
- LangGraph does **not** overwrite `partial_tags` with the last tagger’s list. The state schema declares `partial_tags: Annotated[list, operator.add]`, so the **reducer** is used: each tagger’s list is **appended** to the current list. After all 8 run: `partial_tags = [] + [item1] + [item2] + ... + [item8]` = a list of 8 elements.

> **Why This Way?** Without a reducer, the last tagger to finish would overwrite the previous seven. With `operator.add`, we concatenate lists and get one entry per category.

---

## Step 4 — ALL_TAGGERS: node name to function

The graph builder registers each name with its function. When the runtime runs "season_tagger", it calls the `tag_season` function.

**Snippet (lines 146–156 in taggers.py)**

```python
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
```

**What is happening**

- In graph_builder.py we have `for name, fn in ALL_TAGGERS.items(): builder.add_node(name, fn)`. So each of these names is a node, and when the conditional edge returns `Send("season_tagger", state)`, the runtime calls `tag_season(state)` (and similarly for the others). Lab 07 walks through what **run_tagger** does inside each of these.

**Source:** [backend/src/image_tagging/nodes/taggers.py](../../backend/src/image_tagging/nodes/taggers.py) (lines 146–156)

---

## Step 5 — After all 8 finish: merge and go to validator

When every tagger has finished:

1. LangGraph merges the 8 returned dicts into the state. For `partial_tags`, it applies the reducer: the 8 lists (each of length 1) are concatenated into one list of length 8.
2. The edges from each tagger to `tag_validator` mean: the next node is the validator. The runtime runs it **once** with the merged state (including `partial_tags` with 8 items).

> **State Tracker (after all taggers, before validator):** `partial_tags` is now a list of 8 dicts: one per category (season, theme, objects, dominant_colors, design_elements, occasion, mood, product_type). Each element has `category`, `tags`, `confidence_scores`. All other state keys unchanged from after vision.

> **I/O Snapshot:** **Input to each tagger:** state with `vision_description` (and empty `partial_tags`). **Output from each tagger:** `{"partial_tags": [TagResult_dict]}`. **Merged state:** `partial_tags` = list of 8 TagResult dicts.

> **Next:** Execution continues at **tag_validator**, which reads `partial_tags` and validates every tag against the taxonomy. See [07-inside-a-tagger.md](07-inside-a-tagger.md) for what happens inside one tagger, then [08-validator-checks-tags.md](08-validator-checks-tags.md) for the validator.

---

## Lab summary

1. The **conditional edge** after vision_analyzer calls **fan_out_to_taggers(state)**, which returns a list of **Send(node_name, state)** for each of the 8 taggers.
2. All 8 taggers receive the **same** state (with `vision_description`). They run in parallel (when async). Each returns `{"partial_tags": [one_TagResult]}`.
3. The **reducer** for `partial_tags` (operator.add) **concatenates** those lists. After all 8 finish, state has `partial_tags` = 8 elements.
4. The graph then runs **tag_validator** once with that merged state.

---

## Exercises

1. Why does each tagger receive the same state instead of receiving the previous tagger’s output?
2. If we had 10 taggers and one of them returned `{"partial_tags": [a, b]}` (two items), what would the merged `partial_tags` length be?
3. What would happen if we forgot to add the edge from each tagger to tag_validator?

---

## Next lab

Go to [07-inside-a-tagger.md](07-inside-a-tagger.md) to see **run_tagger** step by step: how it gets allowed values from the taxonomy, builds the prompt, calls the LLM, parses and filters, and returns one TagResult in partial_tags.
