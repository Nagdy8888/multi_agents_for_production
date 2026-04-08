# Lab 15 — Search Results and Modal

**Estimated time:** 20 min  
**Difficulty:** Beginner

**SearchResults** renders a grid of rows (image thumbnail + sample tags). When the user clicks a row, **onSelectItem(row)** is called and **DetailModal** opens with the full tag_record for that row. This lab traces SearchResults and DetailModal.

---

## Learning objectives

- See how SearchResults maps **items** (TagImageRow[]) to a grid and extracts sample tags from tag_record.
- See how **DetailModal** receives **row** (TagImageRow | null), converts tag_record to tags_by_category shape, and reuses TagCategories and FlaggedTags.

---

## Prerequisites

- [14-search-backend-and-db.md](14-search-backend-and-db.md) — results are in state and passed to SearchResults.

---

## Step 1 — SearchResults: grid and onClick

SearchResults receives **items**, **loading**, and **onSelectItem**. When loading it shows skeletons; when empty it shows an empty state; otherwise it renders a grid. Each card shows the image (from row.image_url) and sample tags (e.g. getSeasonTags, getThemeTags from tag_record). **onClick** calls **onSelectItem(row)** so the parent sets **selectedRow** and DetailModal opens.

**Source:** [frontend/src/components/SearchResults.tsx](../../frontend/src/components/SearchResults.tsx)

---

## Step 2 — DetailModal: tagRecordToTagsByCategory

DetailModal receives **row** (TagImageRow | null) and **onClose**. When row is set it shows a modal with the image, **tag_record** converted to a tags_by_category-like structure via **tagRecordToTagsByCategory**, then **TagCategories** and **FlaggedTags** (if any). So the same TagCategories component used on the analyze result is reused here for a stored row.

**Source:** [frontend/src/components/DetailModal.tsx](../../frontend/src/components/DetailModal.tsx)

> **Next:** [16-bulk-upload-and-background.md](16-bulk-upload-and-background.md) — bulk upload and background processing.

---

## Lab summary

- SearchResults renders items in a grid, shows sample tags from tag_record, and calls onSelectItem(row) on click. DetailModal shows the full row and converts tag_record to tags_by_category for TagCategories.

---

## Next lab

[16-bulk-upload-and-background.md](16-bulk-upload-and-background.md)
