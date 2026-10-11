"""Keebo's indexed palette.

Every sprite is drawn with palette indices, never raw RGB, so the whole
look can be re-themed by swapping this table.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

RGB = Tuple[int, int, int]

#: Index used by layers for "no pixel here".
CLEAR = 255

VOID = 0      # background, deepest night
NIGHT = 1     # background panels
INK = 2       # outlines
SLATE = 3     # furniture, shadows
FOG = 4       # metal, light grey
SNOW = 5      # highlights, eyes, paper
MINT = 6      # Keebo top face
TEAL = 7      # Keebo body
DEEP = 8      # Keebo skirt / shade
CORAL = 9     # blush, hearts, stem
SUN = 10      # gold, sparks, stars
EMBER = 11    # orange, fire
RUBY = 12     # red, errors
SKY = 13      # blue, screens, water
GRAPE = 14    # purple, magic
COCOA = 15    # wood, popcorn bucket stripes
LILAC = 16    # Inky body
LILAC_D = 17  # Inky shade, spots
LILAC_L = 18  # Inky highlight
PINK = 19     # Axo body
PINK_D = 20   # Axo gills, shade
PINK_L = 21   # Axo belly, highlight
BLUSH = 22    # cheeks

PALETTE: List[RGB] = [
    (0x0E, 0x0B, 0x1F),
    (0x1D, 0x19, 0x3A),
    (0x29, 0x1F, 0x42),
    (0x4B, 0x44, 0x6E),
    (0x9A, 0x96, 0xB8),
    (0xF6, 0xF2, 0xFF),
    (0x7C, 0xF7, 0xCF),
    (0x2F, 0xBF, 0xA3),
    (0x1B, 0x73, 0x72),
    (0xFF, 0x6F, 0x91),
    (0xFF, 0xD8, 0x5E),
    (0xFF, 0x96, 0x3B),
    (0xE8, 0x3A, 0x52),
    (0x5C, 0xBC, 0xFF),
    (0xA0, 0x6E, 0xFF),
    (0x91, 0x5E, 0x40),
    (0xC9, 0xA7, 0xFF),
    (0x8A, 0x63, 0xD9),
    (0xE6, 0xD6, 0xFF),
    (0xFF, 0xB3, 0xC7),
    (0xE0, 0x7A, 0x9A),
    (0xFF, 0xDD, 0xE6),
    (0xFF, 0x86, 0x9E),
]

NAMES: Dict[str, int] = {
    "void": VOID, "night": NIGHT, "ink": INK, "slate": SLATE, "fog": FOG,
    "snow": SNOW, "mint": MINT, "teal": TEAL, "deep": DEEP, "coral": CORAL,
    "sun": SUN, "ember": EMBER, "ruby": RUBY, "sky": SKY, "grape": GRAPE,
    "cocoa": COCOA, "lilac": LILAC, "lilac_d": LILAC_D, "lilac_l": LILAC_L,
    "pink": PINK, "pink_d": PINK_D, "pink_l": PINK_L, "blush": BLUSH,
}

#: Cycling hues for RGB underglow, confetti and rainbow effects.
RAINBOW = [RUBY, EMBER, SUN, MINT, SKY, GRAPE, CORAL]


def flat_palette() -> List[int]:
    """Palette as the flat 768-entry list Pillow's ``putpalette`` expects."""
    flat: List[int] = []
    for rgb in PALETTE:
        flat.extend(rgb)
    flat.extend([0, 0, 0] * (256 - len(PALETTE)))
    return flat
