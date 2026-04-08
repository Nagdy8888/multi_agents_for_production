# Lab 12 — Frontend Shows Result

**Estimated time:** 30 min  
**Difficulty:** Beginner

When the API returns, the Home page calls **setAnalysisResult(data)**. On the next render, **analysisResult** is truthy so the page shows **DashboardResult** instead of the upload form. This lab traces how the result flows from state into DashboardResult and how each sub-component (TagCategories, FlaggedTags, ConfidenceRing, JsonViewer) uses the data.

---

## Learning objectives

- See how the conditional render **!analysisResult ? upload form : DashboardResult** works.
- See how DashboardResult receives **data** (AnalyzeImageResponse) and **onReplaceImage** and derives tagsByCategory, vision fields, and overallConfidence.
- Understand what each child component receives and displays.

---

## Prerequisites

- [11-server-saves-and-responds.md](11-server-saves-and-responds.md) — the server has returned the full JSON and the frontend has called setAnalysisResult(data) in handleAnalyze (Lab 01).

---

## Step 1 — Home page: conditional render

The Home page keeps **analysisResult** in state. When it is null we show the upload UI; when it is set we show DashboardResult and pass the result as **data**.

**Snippet (lines 74–102 in page.tsx)**

```tsx
        {!analysisResult ? (
          <div className="mx-auto max-w-2xl space-y-6">
            ...
            <ImageUploader onAnalyze={handleAnalyze} disabled={isProcessing} />
            ...
          </div>
        ) : (
          <div className="mx-auto w-full max-w-6xl">
            <DashboardResult data={analysisResult} onReplaceImage={handleReplaceImage} />
          </div>
        )}
```

**What is happening**

- **!analysisResult** — Before the user has analyzed an image (or after they click "Replace Image"), analysisResult is null so we show the upload form and BulkUploader.
- **analysisResult** — After a successful fetch we set it to the API response (Lab 01). The next render has analysisResult truthy, so we render the second branch: **DashboardResult** with **data={analysisResult}** and **onReplaceImage={handleReplaceImage}**.
- **handleReplaceImage** (Lab 01) sets analysisResult to null and clears error, so the user goes back to the upload form.

**Source:** [frontend/src/app/page.tsx](../../frontend/src/app/page.tsx) (lines 74–102)

> **State Tracker (Home):** analysisResult = full API response object. isProcessing = false. error = null (on success).

---

## Step 2 — DashboardResult: props and derived data

DashboardResult receives the full **AnalyzeImageResponse** as **data** and a callback **onReplaceImage**. It pulls out tags_by_category, vision_raw_tags, and flagged_tags and computes overallConfidence and vision-derived strings.

**Snippet (lines 14–53 in DashboardResult.tsx)**

```tsx
interface DashboardResultProps {
  data: AnalyzeImageResponse;
  onReplaceImage: () => void;
}

export function DashboardResult({ data, onReplaceImage }: DashboardResultProps) {
  const tagsByCategory = data.tags_by_category ?? {};
  const vision = data.vision_raw_tags ?? {};
  const flagged = data.flagged_tags ?? [];

  const overallConfidence = useMemo(() => {
    let sum = 0;
    let n = 0;
    Object.values(tagsByCategory).forEach((list) => {
      list.forEach((t) => {
        sum += t.confidence;
        n += 1;
      });
    });
    return n > 0 ? sum / n : 0;
  }, [tagsByCategory]);

  const dominantMood = vision.dominant_mood != null && String(vision.dominant_mood) !== ""
    ? String(vision.dominant_mood) : null;
  const visibleSubjects = Array.isArray(vision.visible_subjects) ? (vision.visible_subjects as string[]) : [];
  const colorObs = ...;
  const seasonal = ...;
  const style = ...;
```

**What is happening**

- **tagsByCategory** — From the server’s tags_by_category (Lab 11). Shape: `{ season: [{ value, confidence }, ...], theme: [...], ... }`. Used by TagCategories and for overallConfidence.
- **vision** — vision_raw_tags from the vision node (e.g. dominant_mood, visible_subjects, color_observations). We coerce to safe strings or arrays for display.
- **flagged** — List of FlaggedTag dicts; passed to FlaggedTags.
- **overallConfidence** — useMemo computes the average of all confidence values across all categories. Used by ConfidenceRing. We use useMemo so we only recompute when tagsByCategory changes.

**Source:** [frontend/src/components/DashboardResult.tsx](../../frontend/src/components/DashboardResult.tsx) (lines 14–53)

> **Glossary:** **useMemo** — A React hook that memoizes a computed value; the function runs only when dependencies (here tagsByCategory) change.

---

## Step 3 — Layout: image card and "Replace Image"

The first row has two cards: the product image and the AI Analysis summary. The image card shows the uploaded image URL, a "Saved" badge when saved_to_db is true, and a **Replace Image** button that calls onReplaceImage.

**Snippet (lines 63–99 in DashboardResult.tsx)**

```tsx
      <div className="grid w-full grid-cols-1 gap-6 md:grid-cols-2">
        <section className="...">
          ...
          {data.saved_to_db && (
            <span className="...">Saved</span>
          )}
          ...
          <Button ... onClick={onReplaceImage}>Replace Image</Button>
          ...
          <Image src={data.image_url} alt="Product" fill ... />
        </section>
```

**What is happening**

- **data.image_url** — The URL built by the server (e.g. http://localhost:8000/uploads/abc-123.jpg). Next.js Image component loads and displays it.
- **data.saved_to_db** — From the API response; when true we show a "Saved" badge.
- **onReplaceImage** — Resets analysisResult to null so the user sees the upload form again (Lab 01).

**Source:** [frontend/src/components/DashboardResult.tsx](../../frontend/src/components/DashboardResult.tsx) (lines 63–99)

---

## Step 4 — AI Analysis card: vision description and ConfidenceRing

The second card shows the vision description, dominant mood, visible subjects, color/seasonal/style observations, and a **ConfidenceRing** with the overall confidence value.

**Snippet (lines 103–163 in DashboardResult.tsx)**

```tsx
        <section className="...">
          <h2>AI Analysis</h2>
          {data.vision_description && (
            <div>
              <h3>Vision Analysis</h3>
              <p>{data.vision_description}</p>
            </div>
          )}
          ... dominantMood, visibleSubjects, colorObs, seasonal, style ...
          <div className="mt-6 flex justify-center">
            <ConfidenceRing
              confidence={overallConfidence}
              size={120}
              strokeWidth={8}
              showValue
              className="text-emerald-500"
            />
          </div>
        </section>
```

**What is happening**

- **data.vision_description** — The 2–3 sentence description from the vision node (used by taggers). Shown as the main "Vision Analysis" text.
- **dominantMood, visibleSubjects, etc.** — Derived from vision_raw_tags (Lab 05). Only rendered if present.
- **ConfidenceRing** — A circular progress-style component that shows overallConfidence (0–1). It helps the user see at a glance how confident the pipeline was across all categories.

**Source:** [frontend/src/components/DashboardResult.tsx](../../frontend/src/components/DashboardResult.tsx) (lines 103–163)

---

## Step 5 — Tags by Category and FlaggedTags

The next section renders **TagCategories** with tagsByCategory (so each category gets a list of tags with optional confidence), then **FlaggedTags** with the flagged list.

**Snippet (lines 166–178 in DashboardResult.tsx)**

```tsx
      <section>
        <h2>Tags by Category</h2>
        {Object.keys(tagsByCategory).length > 0 ? (
          <TagCategories tagsByCategory={tagsByCategory} showTitle={false} />
        ) : (
          <p>No tags yet.</p>
        )}
      </section>

      <section className="...">
        <FlaggedTags flagged={flagged} />
      </section>
```

**What is happening**

- **TagCategories** — Receives tagsByCategory (dict category → list of {value, confidence}). It typically renders one block per category with a label and the tags as chips. showTitle={false} may hide per-category titles if TagCategories draws its own.
- **FlaggedTags** — Receives the list of FlaggedTag dicts (category, value, confidence, reason). It renders them so the user can see which tags were dropped (low_confidence or invalid_taxonomy_value).

**Source:** [frontend/src/components/DashboardResult.tsx](../../frontend/src/components/DashboardResult.tsx) (lines 166–178)

---

## Step 6 — JsonViewer

The bottom section shows raw JSON: either tag_record (the final TagRecord from the aggregator) or vision_raw_tags if tag_record is missing.

**Snippet (line 180 in DashboardResult.tsx)**

```tsx
      <JsonViewer data={data.tag_record ?? data.vision_raw_tags} />
```

**What is happening**

- **data.tag_record** — The full TagRecord (season, theme, objects, dominant_colors, etc.). If present we show it for debugging or power users.
- **data.vision_raw_tags** — Fallback when tag_record is missing (e.g. validator returned {}). JsonViewer typically renders collapsible JSON so the user can expand and inspect.

**Source:** [frontend/src/components/DashboardResult.tsx](../../frontend/src/components/DashboardResult.tsx) (line 180)

---

## Lab summary

1. **Home page** renders DashboardResult when analysisResult is set, passing **data** (the API response) and **onReplaceImage**.
2. **DashboardResult** reads tags_by_category, vision_raw_tags, flagged_tags from data; computes **overallConfidence** with useMemo and derives vision display fields (dominantMood, visibleSubjects, etc.).
3. **Layout:** Image card (image_url, Saved badge, Replace Image button), AI Analysis card (vision_description, vision fields, ConfidenceRing), Tags by Category (TagCategories), FlaggedTags, JsonViewer (tag_record or vision_raw_tags).
4. **Replace Image** calls onReplaceImage, which clears analysisResult and returns the user to the upload form.

---

## Exercises

1. What triggers a re-render of the Home page after the fetch completes?
2. Why does DashboardResult use useMemo for overallConfidence?
3. What does the user see if the server returns tags_by_category empty but partial_tags non-empty? (Hint: Lab 11 builds tags_by_category from partial when validated is empty.)

---

## Next lab

The single-image flow is complete. Go to [13-search-page-and-filters.md](13-search-page-and-filters.md) to see the Search page: how it loads filters and results and how FilterSidebar works with the available-filters API.
