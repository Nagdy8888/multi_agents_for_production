# Tag taxonomy

Single source of truth: `backend/src/image_tagging/taxonomy.py`. Used by taggers (allowed values), validator, and aggregator (hierarchical mapping).

## Categories

- **Flat (list of strings):** season, theme, design_elements, occasion, mood.
- **Hierarchical (parent → list of children):** objects, dominant_colors, product_type.

## Reference

| Category | Type | Notes |
|----------|------|--------|
| season | flat | 19 values (e.g. christmas, valentines_day, all_occasion) |
| theme | flat | 18 values (e.g. whimsical, modern, floral_botanical) |
| objects | hierarchical | Parents: characters, animals, plants_nature, food_drink, objects_items, places_architecture, symbols_icons |
| dominant_colors | hierarchical | Parents: red_family, pink_family, …, metallic_family |
| design_elements | flat | 33 values (stripes, polka_dots, glitter_sparkle, …) |
| occasion | flat | 8 values (gifting_general, wedding_event, …) |
| mood | flat | 9 values (joyful_fun, elegant_sophisticated, …) |
| product_type | hierarchical | Parents: gift_bag, gift_card_envelope, gift_wrap, gift_box, accessory |

## Helpers

- `get_flat_values(category)` — Returns all allowed values (for flat: the list; for hierarchical: all children).
- `get_parent_for_child(category, child)` — For hierarchical categories, returns the parent key for a child value, or None.

Full enum definitions are in `taxonomy.py` (SEASON, THEME, OBJECTS, DOMINANT_COLORS, DESIGN_ELEMENTS, OCCASION, MOOD, PRODUCT_TYPE, TAXONOMY).
