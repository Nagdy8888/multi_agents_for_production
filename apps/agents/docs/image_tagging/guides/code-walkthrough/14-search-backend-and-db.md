# Lab 14 — Search Backend and DB

**Estimated time:** 25 min  
**Difficulty:** Intermediate

The **search-images** endpoint parses filter query params, calls the Supabase client’s **search_images_filtered**, and returns matching rows. The **available-filters** endpoint uses the same params and calls **get_available_filter_values** to return cascading options. This lab traces the server and client code and the **@>** containment query.

---

## Learning objectives

- See **_parse_filter_params**: comma-separated query params → dict category → list of values.
- See **search_images_filtered**: build flat list of values, query WHERE search_index @> array.
- See **get_available_filter_values**: run search then aggregate unique values per category from tag_record.

---

## Prerequisites

- [13-search-page-and-filters.md](13-search-page-and-filters.md) — the frontend sends GET search-images and available-filters with a query string.

---

## Step 1 — _parse_filter_params (server.py)

**Snippet (lines 202–227 in server.py)**

```python
def _parse_filter_params(
    season: str | None = None,
    theme: str | None = None,
    objects: str | None = None,
    dominant_colors: str | None = None,
    design_elements: str | None = None,
    occasion: str | None = None,
    mood: str | None = None,
    product_type: str | None = None,
) -> dict[str, list[str]]:
    """Parse comma-separated query params into filters dict."""
    filters = {}
    for key, param in [
        ("season", season),
        ("theme", theme),
        ...
    ]:
        if param:
            values = [v.strip() for v in param.split(",") if v.strip()]
            if values:
                filters[key] = values
    return filters
```

**What is happening**

- Each query param (e.g. season=christmas,hanukkah) is split by comma and stripped. We build **filters** = { category: [value1, value2, ...] }. Used by both search_images and available_filters.

**Source:** [backend/src/server.py](../../backend/src/server.py) (lines 202–227)

---

## Step 2 — search_images and search_images_filtered (client)

**Snippet (server.py, search_images endpoint)**

```python
@app.get("/api/search-images")
def search_images(season=..., theme=..., ..., limit: int = 50):
    ...
    filters = _parse_filter_params(...)
    rows = client.search_images_filtered(filters, limit=limit)
    return {"items": rows, "limit": limit}
```

**Snippet (client.py, search_images_filtered)**

```python
def search_images_filtered(self, filters: dict, limit: int = 50) -> list[dict]:
    """Return rows where search_index contains ALL specified values (AND logic)."""
    flat_values: list[str] = []
    for values in filters.values():
        ...  # collect all values into flat_values
    if not flat_values:
        return self.list_tag_images(limit=limit, offset=0)
    ...
    cur.execute(
        "SELECT ... FROM image_tags WHERE search_index @> %s::text[] ORDER BY created_at DESC LIMIT %s",
        (flat_values, limit),
    )
```

**What is happening**

- **search_index** is a TEXT[] column built from tag_record (Lab 18). **@>** is PostgreSQL “array contains”: the row’s search_index must contain **every** value in flat_values. So AND across categories: e.g. christmas + joyful_fun returns only rows that have both.

**Source:** [backend/src/server.py](../../backend/src/server.py), [backend/src/services/supabase/client.py](../../backend/src/services/supabase/client.py)

---

## Step 3 — available_filters and get_available_filter_values

**available_filters** calls **client.get_available_filter_values(filters)**. That method runs **search_images_filtered(filters, limit=500)** to get rows matching the current selection, then iterates each row’s tag_record and collects unique values per category (season, theme, objects, etc.). It returns a dict category → sorted list of values so the UI can show only options that still exist in the result set.

**Source:** [backend/src/services/supabase/client.py](../../backend/src/services/supabase/client.py) — get_available_filter_values

> **Next:** [15-search-results-and-modal.md](15-search-results-and-modal.md) — SearchResults grid and DetailModal.

---

## Lab summary

- **_parse_filter_params** turns query params into a filters dict. **search_images_filtered** builds flat_values and runs WHERE search_index @> flat_values for AND logic. **get_available_filter_values** runs search then aggregates unique values per category for cascading filters.

---

## Next lab

[15-search-results-and-modal.md](15-search-results-and-modal.md)
