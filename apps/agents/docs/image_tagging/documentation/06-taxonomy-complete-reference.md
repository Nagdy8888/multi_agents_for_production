# 06 — Taxonomy Complete Reference

This document lists every allowed value in every tag category (flat and hierarchical), and describes `get_flat_values(category)` and `get_parent_for_child(category, child)`.

**File:** `backend/src/image_tagging/taxonomy.py`

---

## TAXONOMY dict shape

- **Flat categories:** `TAXONOMY[category]` is a list of strings (season, theme, design_elements, occasion, mood).
- **Hierarchical categories:** `TAXONOMY[category]` is a dict of parent_key → list of child values (objects, dominant_colors, product_type).

---

## Flat categories

### season (19 values)

```
christmas, hanukkah, kwanzaa, new_years, valentines_day, st_patricks_day, easter,
mothers_day, fathers_day, fourth_of_july, halloween, thanksgiving, diwali, eid,
birthday, wedding_anniversary, baby_shower, graduation, all_occasion
```

### theme (18 values)

```
whimsical, traditional, modern, minimalist, elegant_luxury, rustic_farmhouse,
vintage_retro, kawaii_cute, floral_botanical, tropical, religious, feminine,
masculine, kids_juvenile, nature_organic, abstract, typographic, photorealistic
```

### design_elements (33 values)

```
stripes, checkered, plaid_tartan, polka_dots, argyle, houndstooth, chevron,
herringbone, ikat, paisley, geometric, abstract_pattern, floral_pattern, toile,
damask, glitter_sparkle, foil_metallic, watercolor, hand_drawn_sketch,
embossed_effect, linen_texture, kraft_texture, all_over_print, centered_motif,
scattered_elements, border_frame, tiled_repeat, asymmetric, symmetrical,
diagonal_layout, handlettering, serif_type, sans_serif_type, script_cursive,
block_letters, no_text
```

### occasion (8 values)

```
gifting_general, gifting_premium, corporate_branded, party_supplies,
wedding_event, kids_party, self_gifting, charitable_cause
```

### mood (9 values)

```
joyful_fun, elegant_sophisticated, romantic, nostalgic_sentimental, spooky_dark,
peaceful_calm, bold_energetic, cozy_warm, fresh_bright
```

---

## Hierarchical categories

### objects (7 parents)

| Parent | Children |
|--------|----------|
| characters | santa, mrs_claus, elf, reindeer, snowman, grinch, easter_bunny, witch, ghost, angel, cupid, gnome, fairy, mermaid, unicorn, dragon, superhero |
| animals | bear, rabbit, cat, dog, bird, fox, owl, penguin, deer, sheep, squirrel, butterfly, bee, flamingo, sloth, dinosaur |
| plants_nature | christmas_tree, wreath, holly, mistletoe, flower, rose, sunflower, leaf, cactus, pumpkin, tree, mushroom, rainbow, cloud, sun, moon, star, snowflake, fireworks |
| food_drink | cake, cupcake, cookie, candy, chocolate, wine, champagne, coffee, gingerbread, ice_cream, fruit, pie |
| objects_items | gift_box, ribbon, bow, balloon, candle, ornament, stocking, heart, diamond, crown, key, crayon, pencil, book, camera, bicycle, car, boat, umbrella, envelope, trophy |
| places_architecture | house, castle, hotel, cityscape, barn, beach, forest, mountain, space, church |
| symbols_icons | cross, star_of_david, crescent, peace_sign, infinity, anchor, compass, musical_note, sports_ball |

### dominant_colors (9 families)

| Parent | Children |
|--------|----------|
| red_family | crimson, scarlet, cherry, burgundy, rose_red |
| pink_family | hot_pink, blush, coral, salmon, bubblegum |
| orange_family | burnt_orange, peach, amber, tangerine |
| yellow_family | yellow, gold, mustard, lemon, cream_yellow |
| green_family | forest_green, mint, lime, sage, olive, emerald |
| blue_family | navy, sky_blue, teal, royal_blue, baby_blue, denim |
| purple_family | lavender, violet, plum, lilac, mauve |
| neutral_family | white, off_white, beige, tan, brown, gray_light, gray_dark, black |
| metallic_family | gold_metallic, silver_metallic, rose_gold, bronze, copper |

### product_type (5 parents)

| Parent | Children |
|--------|----------|
| gift_bag | gift_bag_small, gift_bag_medium, gift_bag_large, gift_bag_extra_large, wine_bag, bottle_bag, tote_style |
| gift_card_envelope | standard_gift_card, money_holder, oversized_card, boxed_notecard |
| gift_wrap | wrapping_paper_sheet, wrapping_paper_roll, tissue_paper, gift_tissue_set |
| gift_box | box_lid, collapsible_box, window_box |
| accessory | ribbon_spool, bow_pack, tag_label, filler_shred |

---

## get_flat_values(category)

**Signature:** `get_flat_values(category: str) -> list[str]`

**Behavior:**

- If `category` is not in `TAXONOMY`, returns `[]`.
- If `TAXONOMY[category]` is a **list**, returns a copy of that list.
- If `TAXONOMY[category]` is a **dict** (hierarchical), returns a single flat list of all child values (all values from all parents).

**Examples:**

- `get_flat_values("season")` → list of 19 season strings.
- `get_flat_values("theme")` → list of 18 theme strings.
- `get_flat_values("objects")` → list of all object children (e.g. santa, bear, gift_box, …).
- `get_flat_values("dominant_colors")` → list of all color shades (crimson, navy, white, …).
- `get_flat_values("product_type")` → list of all product_type children (gift_bag_small, wrapping_paper_roll, …).

Used by taggers to build the “allowed values” list for the LLM prompt.

---

## get_parent_for_child(category, child)

**Signature:** `get_parent_for_child(category: str, child: str) -> str | None`

**Behavior:**

- If `TAXONOMY[category]` is not a dict, returns `None`.
- Otherwise iterates over parent → children; if `child` is in one of the children lists, returns that **parent** key.
- If `child` is not found, returns `None`.

**Examples:**

- `get_parent_for_child("objects", "ribbon")` → `"objects_items"`.
- `get_parent_for_child("objects", "santa")` → `"characters"`.
- `get_parent_for_child("dominant_colors", "crimson")` → `"red_family"`.
- `get_parent_for_child("dominant_colors", "navy")` → `"blue_family"`.
- `get_parent_for_child("product_type", "gift_bag_medium")` → `"gift_bag"`.
- `get_parent_for_child("season", "christmas")` → `None` (flat category).
- `get_parent_for_child("objects", "invalid")` → `None`.

Used by the validator (to validate and set `parent` on ValidatedTag) and by the aggregator (to build HierarchicalTag and TagRecord).
