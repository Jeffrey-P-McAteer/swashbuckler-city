#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fonttools"
# ]
# ///

import os
import pathlib

import fontTools

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

SOURCE_FONTS_DIR = REPO_ROOT / "graphics" / "fonts"
BUILD_FONTS_DIR = REPO_ROOT / "build" / "fonts"
os.makedirs(BUILD_FONTS_DIR, exist_ok=True)

for font_src_dirent in os.scandir(SOURCE_FONTS_DIR):
  if not font_src_dirent.is_dir():
    continue
  font_name = font_src_dirent.name
  ttf_output_file = BUILD_FONTS_DIR / f'{font_name}.ttl'

  print(f'font_name={font_name} will be generated to {ttf_output_file}')

# GLYPHS = REPO_ROOT / "graphics" / "glyphs"



# OUTPUT = BUILD_FONTS_DIR / "SwashBTitle.ttf"

# OUTPUT.parent.mkdir(exist_ok=True)

# font = fontforge.font()

# font.encoding = "UnicodeFull"
# font.fontname = "SwashBTitle"
# font.familyname = "SwashBTitle"
# font.fullname = "Swashbucker Title"
# font.weight = "Regular"

# font.em = 1000
# font.ascent = 800
# font.descent = 200

# # Unicode character mapping
# characters = {
#     "A": 0x0041,
#     "B": 0x0042,
#     "C": 0x0043,
#     "a": 0x0061,
#     "b": 0x0062,
#     "zero": 0x0030,
# }

# for name, codepoint in characters.items():
#     glyph = font.createChar(codepoint, name)

#     svg = GLYPHS / f"{name}.svg"

#     if svg.exists():
#         glyph.importOutlines(str(svg), scale=False)

#     glyph.width = 600

# font.generate(str(OUTPUT))
# font.save(str(ROOT / "build" / "MyFont.sfd"))

