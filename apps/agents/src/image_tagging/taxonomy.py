"""
Single source of truth for all tag taxonomy enums.
Values from image-tagging-agent-spec.md sections 5.1-5.8.
"""

SEASON = [
    "christmas", "hanukkah", "kwanzaa", "new_years", "valentines_day",
    "st_patricks_day", "easter", "mothers_day", "fathers_day", "fourth_of_july",
    "halloween", "thanksgiving", "diwali", "eid", "birthday",
    "wedding_anniversary", "baby_shower", "graduation", "all_occasion",
]

THEME = [
    "whimsical", "traditional", "modern", "minimalist", "elegant_luxury",
    "rustic_farmhouse", "vintage_retro", "kawaii_cute", "floral_botanical",
    "tropical", "religious", "feminine", "masculine", "kids_juvenile",
    "nature_organic", "abstract", "typographic", "photorealistic",
]

OBJECTS = {
    "characters": [
        "santa", "mrs_claus", "elf", "reindeer", "snowman", "grinch", "easter_bunny",
        "witch", "ghost", "angel", "cupid", "gnome", "fairy", "mermaid", "unicorn",
        "dragon", "superhero",
    ],
    "animals": [
        "bear", "rabbit", "cat", "dog", "bird", "fox", "owl", "penguin", "deer",
        "sheep", "squirrel", "butterfly", "bee", "flamingo", "sloth", "dinosaur",
    ],
    "plants_nature": [
        "christmas_tree", "wreath", "holly", "mistletoe", "flower", "rose", "sunflower",
        "leaf", "cactus", "pumpkin", "tree", "mushroom", "rainbow", "cloud", "sun",
        "moon", "star", "snowflake", "fireworks",
    ],
    "food_drink": [
        "cake", "cupcake", "cookie", "candy", "chocolate", "wine", "champagne",
        "coffee", "gingerbread", "ice_cream", "fruit", "pie",
    ],
    "objects_items": [
        "gift_box", "ribbon", "bow", "balloon", "candle", "ornament", "stocking",
        "heart", "diamond", "crown", "key", "crayon", "pencil", "book", "camera",
        "bicycle", "car", "boat", "umbrella", "envelope", "trophy",
    ],
    "places_architecture": [
        "house", "castle", "hotel", "cityscape", "barn", "beach", "forest",
        "mountain", "space", "church",
    ],
    "symbols_icons": [
        "cross", "star_of_david", "crescent", "peace_sign", "infinity", "anchor",
        "compass", "musical_note", "sports_ball",
    ],
}

DOMINANT_COLORS = {
    "red_family": ["crimson", "scarlet", "cherry", "burgundy", "rose_red"],
    "pink_family": ["hot_pink", "blush", "coral", "salmon", "bubblegum"],
    "orange_family": ["burnt_orange", "peach", "amber", "tangerine"],
    "yellow_family": ["yellow", "gold", "mustard", "lemon", "cream_yellow"],
    "green_family": ["forest_green", "mint", "lime", "sage", "olive", "emerald"],
    "blue_family": ["navy", "sky_blue", "teal", "royal_blue", "baby_blue", "denim"],
    "purple_family": ["lavender", "violet", "plum", "lilac", "mauve"],
    "neutral_family": [
        "white", "off_white", "beige", "tan", "brown", "gray_light", "gray_dark", "black",
    ],
    "metallic_family": ["gold_metallic", "silver_metallic", "rose_gold", "bronze", "copper"],
}

DESIGN_ELEMENTS = [
    "stripes", "checkered", "plaid_tartan", "polka_dots", "argyle", "houndstooth",
    "chevron", "herringbone", "ikat", "paisley", "geometric", "abstract_pattern",
    "floral_pattern", "toile", "damask",
    "glitter_sparkle", "foil_metallic", "watercolor", "hand_drawn_sketch",
    "embossed_effect", "linen_texture", "kraft_texture",
    "all_over_print", "centered_motif", "scattered_elements", "border_frame",
    "tiled_repeat", "asymmetric", "symmetrical", "diagonal_layout",
    "handlettering", "serif_type", "sans_serif_type", "script_cursive",
    "block_letters", "no_text",
]

OCCASION = [
    "gifting_general", "gifting_premium", "corporate_branded", "party_supplies",
    "wedding_event", "kids_party", "self_gifting", "charitable_cause",
]

MOOD = [
    "joyful_fun", "elegant_sophisticated", "romantic", "nostalgic_sentimental",
    "spooky_dark", "peaceful_calm", "bold_energetic", "cozy_warm", "fresh_bright",
]

PRODUCT_TYPE = {
    "gift_bag": [
        "gift_bag_small", "gift_bag_medium", "gift_bag_large", "gift_bag_extra_large",
        "wine_bag", "bottle_bag", "tote_style",
    ],
    "gift_card_envelope": ["standard_gift_card", "money_holder", "oversized_card", "boxed_notecard"],
    "gift_wrap": ["wrapping_paper_sheet", "wrapping_paper_roll", "tissue_paper", "gift_tissue_set"],
    "gift_box": ["box_lid", "collapsible_box", "window_box"],
    "accessory": ["ribbon_spool", "bow_pack", "tag_label", "filler_shred"],
}

TAXONOMY = {
    "season": SEASON,
    "theme": THEME,
    "objects": OBJECTS,
    "dominant_colors": DOMINANT_COLORS,
    "design_elements": DESIGN_ELEMENTS,
    "occasion": OCCASION,
    "mood": MOOD,
    "product_type": PRODUCT_TYPE,
}


def get_flat_values(category: str) -> list[str]:
    """Return a flat list of all allowed values for a category (for hierarchical, all children)."""
    val = TAXONOMY.get(category)
    if val is None:
        return []
    if isinstance(val, list):
        return list(val)
    if isinstance(val, dict):
        out = []
        for children in val.values():
            out.extend(children)
        return out
    return []


def get_parent_for_child(category: str, child: str) -> str | None:
    """For hierarchical categories, return the parent key for a child value, or None."""
    val = TAXONOMY.get(category)
    if not isinstance(val, dict):
        return None
    for parent, children in val.items():
        if child in children:
            return parent
    return None
