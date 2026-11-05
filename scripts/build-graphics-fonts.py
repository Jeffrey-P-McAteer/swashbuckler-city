#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fonttools",
#   "json-five",
# ]
# ///

import os
import pathlib
import shutil
import xml.etree.ElementTree

import fontTools
import json5

import fontTools.fontBuilder
import fontTools.pens.ttGlyphPen
import fontTools.pens.cu2quPen
import fontTools.pens.transformPen
import fontTools.svgLib.path
import fontTools.misc.transform

def build_font(source: pathlib.Path, output: pathlib.Path):
    config = json5.loads(
        (source / "font-config.json").read_text()
    )

    upm = config.get("unitsPerEm", 1000)

    glyph_order = [".notdef"]
    glyphs = {}
    cmap = {}
    metrics = {}

    # Required empty glyph.
    pen = fontTools.pens.ttGlyphPen.TTGlyphPen(None)
    glyphs[".notdef"] = pen.glyph()
    metrics[".notdef"] = (upm, 0)

    for svg_file in sorted( source.glob("*.svg") ):
        print(f'Loading {svg_file}')
        root = xml.etree.ElementTree.parse(svg_file).getroot()

        metadata = {}

        for element in root.iter():
            name = element.tag.split("}")[-1]

            if element.text and name in (
                "unicode", "advanceWidth"
            ):
                metadata[name] = element.text.strip()

        print(f'metadata = {metadata}')

        viewbox = list(map(
            float, root.attrib["viewBox"].replace(",", " ").split()
        ))

        x, y, width, height = viewbox
        scale = upm / width

        name = svg_file.stem
        glyph_order.append(name)

        pen = fontTools.pens.ttGlyphPen.TTGlyphPen(None)

        # SVG uses downward-positive Y coordinates.
        transform = fontTools.misc.transform.Transform(
            scale, 0, 0, -scale,
            -x * scale, (y + height) * scale
        )

        output_pen = fontTools.pens.cu2quPen.Cu2QuPen(pen, max_err=1)
        output_pen = fontTools.pens.transformPen.TransformPen(output_pen, transform)

        for element in root.iter():
            if element.tag.split("}")[-1] == "path":
                if element.get("d"):
                    fontTools.svgLib.path.parse_path(element.get("d"), output_pen)

        output_pen = None

        glyphs[name] = pen.glyph()

        advance = float(metadata.get("advanceWidth", upm))
        metrics[name] = (advance, 0)

        if "unicode" in metadata:
            codepoint = int(
                metadata["unicode"].replace("U+", ""), 16
            )
            cmap[codepoint] = name

    fb = fontTools.fontBuilder.FontBuilder(upm, isTTF=True)

    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)

    fb.setupHorizontalHeader(
        ascent=config.get("ascender", 800),
        descent=config.get("descender", -200),
    )

    family = config.get("family", os.path.basename(source))

    fb.setupNameTable({
        "familyName": family,
        "styleName": config.get("style", "Regular"),
        "uniqueFontIdentifier": family,
        "fullName": family,
        "psName": family.replace(" ", ""),
        "version": config.get("version", "Version 1.0"),
    })

    fb.setupOS2(
        sTypoAscender=config.get("ascender", 800),
        sTypoDescender=config.get("descender", -200),
        usWinAscent=config.get("ascender", 800),
        usWinDescent=abs(config.get("descender", -200)),
    )

    fb.setupPost()
    fb.setupMaxp()

    output.parent.mkdir(parents=True, exist_ok=True)
    fb.save(output)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

SOURCE_FONTS_DIR = REPO_ROOT / "graphics" / "fonts"
BUILD_FONTS_DIR = REPO_ROOT / "build" / "fonts"
os.makedirs(BUILD_FONTS_DIR, exist_ok=True)

for font_src_dirent in os.scandir(SOURCE_FONTS_DIR):
  if not font_src_dirent.is_dir():
    continue
  font_name = font_src_dirent.name
  ttf_output_file = BUILD_FONTS_DIR / f'{font_name}.ttf'

  print(f'font_name={font_name} will be generated to {ttf_output_file}')

  build_font(pathlib.Path(font_src_dirent.path), ttf_output_file)


# Finally, for every built font file copy to the web "fonts" folder
WEB_FONTS_DIR = REPO_ROOT / "docs" / "fonts"
os.makedirs(WEB_FONTS_DIR, exist_ok=True)
for built_font_file in os.scandir(BUILD_FONTS_DIR):
  if built_font_file.is_file():
    shutil.copyfile(built_font_file, WEB_FONTS_DIR / os.path.basename(built_font_file) )


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

