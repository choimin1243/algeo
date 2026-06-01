#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reusable AlgeoMath Kids 3D stackblock injection harness.

Coordinate convention for authoring:
  x = left to right from the viewer's front-facing image
  y = front to back, where y=0 is closest to the viewer
  h = column height

Block coordinate convention:
  (x, y, z) means left/right, front/back, up/down in author space
  x grows to the right, y grows toward the back, z grows upward from 1
"""

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright


DEFAULT_COLORS = {1: 0xD89A52, 2: 0xD8893C, 3: 0xC9792F, 4: 0xB96828, 5: 0xA95A20}

PRESETS = {
    # Matches the common reference image: a front-facing 1-2-3-2-1 pyramid.
    # Author-space coordinates:
    #   x: left -> right
    #   y: front -> back
    #   z: bottom -> top
    "reference-pyramid": {
        (0, 0): 1,
        (1, 0): 2,
        (2, 0): 3,
        (3, 0): 2,
        (4, 0): 1,
    },
    "sample-pyramid": {
        (0, 0): 1,
        (1, 0): 2,
        (2, 0): 3,
        (3, 0): 2,
        (4, 0): 1,
    },
    # Triangular staircase pyramid: 10 blocks, 3×3 footprint, tall at front-left.
    # Front view: [3,2,1]  Side view: [3,2,1]  Top: [[3,2,1],[2,1,0],[1,0,0]]
    # Correct answer for the standard Korean isometric pyramid image.
    "triangular-staircase": {
        (0, 0): 3,
        (1, 0): 2,
        (2, 0): 1,
        (0, 1): 2,
        (1, 1): 1,
        (0, 2): 1,
    },
}


def parse_height_map(raw):
    """Parse [[x,y,h], ...] or {"x,y": h, ...} into {(x, y): h}."""
    data = json.loads(raw)
    height_map = {}
    if isinstance(data, list):
        for item in data:
            if not (isinstance(item, list) and len(item) == 3):
                raise ValueError("list height map items must be [x, y, h]")
            x, y, h = item
            height_map[(int(x), int(y))] = int(h)
    elif isinstance(data, dict):
        for key, value in data.items():
            if "," not in key:
                raise ValueError("dict height map keys must look like 'x,y'")
            x, y = key.split(",", 1)
            height_map[(int(x), int(y))] = int(value)
    else:
        raise ValueError("height map must be a list or dict")

    for (x, y), h in height_map.items():
        if x < 0 or y < 0 or h < 0:
            raise ValueError(f"invalid column {(x, y)} -> {h}")
    return height_map


def parse_blocks(raw):
    """Parse [[x,y,z], ...] into author-space blocks."""
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("blocks must be a list of [x, y, z] items")
    blocks = []
    for item in data:
        if not (isinstance(item, list) and len(item) == 3):
            raise ValueError("block items must be [x, y, z]")
        x, y, z = (int(item[0]), int(item[1]), int(item[2]))
        if x < 0 or y < 0 or z < 1:
            raise ValueError(f"invalid block {(x, y, z)}")
        blocks.append((x, y, z))
    return sorted(set(blocks))


def normalize_height_map(height_map):
    if not height_map:
        return {}
    min_x = min(x for x, _ in height_map)
    min_y = min(y for _, y in height_map)
    return {(x - min_x, y - min_y): h for (x, y), h in height_map.items() if h > 0}


def normalize_blocks(blocks):
    if not blocks:
        return []
    min_x = min(x for x, _, _ in blocks)
    min_y = min(y for _, y, _ in blocks)
    return sorted({(x - min_x, y - min_y, z) for x, y, z in blocks})


def columns_to_blocks(height_map):
    """Expand {(x, y): h} columns to author-space (x, y, z) blocks."""
    return [
        (x, y, z)
        for (x, y), height in sorted(height_map.items())
        for z in range(1, height + 1)
    ]


def blocks_to_height_map(blocks):
    height_map = {}
    for x, y, z in blocks:
        height_map[(x, y)] = max(height_map.get((x, y), 0), z)
    return height_map


def to_algeomath_grid(block, max_y):
    """Convert author-space (x, y, z) to AlgeoMath grid (col, row, layer)."""
    x, y, z = block
    return x, max_y - y, z


def build_objects_from_blocks(blocks, max_y=None, colors=None):
    colors = colors or DEFAULT_COLORS
    if max_y is None:
        max_y = max((y for _, y, _ in blocks), default=0)
    layout = [to_algeomath_grid(block, max_y) for block in sorted(blocks)]
    return [
        {
            "id": 100 + i,
            "typeName": "STACK_CUBE",
            "name": "stackCube",
            "is2DObject": False,
            "color": colors.get(z, colors[max(colors)]),
            "measurementType": None,
            "visible": True,
            "position": {"x": x + 0.5, "y": -(y + 0.5), "z": z - 0.5},
            "rotation": {"_x": 0, "_y": 0, "_z": 0, "_order": "XYZ"},
            "scale": {"x": 1, "y": 1, "z": 1},
        }
        for i, (x, y, z) in enumerate(layout)
    ]


def build_objects(height_map, colors=None):
    return build_objects_from_blocks(columns_to_blocks(height_map), colors=colors)


def describe_views(height_map):
    if not height_map:
        return {
            "top": [],
            "front": [],
            "back": [],
            "left": [],
            "right": [],
            "layer_counts": {},
            "total_blocks": 0,
        }
    max_x = max(x for x, _ in height_map)
    max_y = max(y for _, y in height_map)
    max_h = max(height_map.values())
    front = [max(height_map.get((x, y), 0) for y in range(max_y + 1)) for x in range(max_x + 1)]
    back = list(reversed(front))
    left = [max(height_map.get((x, y), 0) for x in range(max_x + 1)) for y in range(max_y + 1)]
    right = list(reversed(left))
    top = [
        [height_map.get((x, y), 0) for x in range(max_x + 1)]
        for y in range(max_y + 1)
    ]
    return {
        "top": top,
        "front": front,
        "back": back,
        "left": left,
        "right": right,
        "layer_counts": {
            layer: sum(1 for h in height_map.values() if h >= layer)
            for layer in range(1, max_h + 1)
        },
        "total_blocks": sum(height_map.values()),
    }


def describe_coordinates(height_map):
    """Return author coordinates and the exact AlgeoMath positions that will be loaded."""
    max_y = max((y for _, y in height_map), default=0)
    author_blocks = columns_to_blocks(height_map)
    return [
        {
            "author_xyz": [x, y, z],
            "author_xyz_1_indexed": [x + 1, y + 1, z],
            "direction": {
                "left_right": x,
                "front_back": y,
                "up": z,
            },
            "algeomath_grid": list(to_algeomath_grid((x, y, z), max_y)),
            "algeomath_position": {
                "x": to_algeomath_grid((x, y, z), max_y)[0] + 0.5,
                "y": -(to_algeomath_grid((x, y, z), max_y)[1] + 0.5),
                "z": z - 0.5,
            },
        }
        for x, y, z in author_blocks
    ]


def describe_block_coordinates(blocks):
    """Return explicit author blocks and the exact AlgeoMath positions that will be loaded."""
    max_y = max((y for _, y, _ in blocks), default=0)
    return [
        {
            "author_xyz": [x, y, z],
            "author_xyz_1_indexed": [x + 1, y + 1, z],
            "direction": {
                "left_right": x,
                "front_back": y,
                "up": z,
            },
            "algeomath_grid": list(to_algeomath_grid((x, y, z), max_y)),
            "algeomath_position": {
                "x": to_algeomath_grid((x, y, z), max_y)[0] + 0.5,
                "y": -(to_algeomath_grid((x, y, z), max_y)[1] + 0.5),
                "z": z - 0.5,
            },
        }
        for x, y, z in sorted(blocks)
    ]


def find_poly_frame(page):
    for frame in page.frames:
        try:
            has_api = frame.evaluate(
                "() => !!(window.AlgeomathPoly && window.AlgeomathPoly.api && "
                "window.AlgeomathPoly.api.save && window.AlgeomathPoly.api.load)"
            )
        except Exception:
            has_api = False
        if has_api:
            return frame
    raise RuntimeError("AlgeomathPoly API frame not found")


def inject(height_map=None, blocks=None, screenshot=None, log_path=None, keep_open=True):
    log_file = Path(log_path) if log_path else None

    def log(message):
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with log_file.open("a", encoding="utf-8") as f:
                f.write(message + "\n")
        else:
            print(message)

    if blocks is not None:
        blocks = normalize_blocks(blocks)
        height_map = blocks_to_height_map(blocks)
        coordinates = describe_block_coordinates(blocks)
    else:
        height_map = normalize_height_map(height_map or {})
        blocks = columns_to_blocks(height_map)
        coordinates = describe_coordinates(height_map)
    views = describe_views(height_map)

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    try:
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(
            "https://www.algeomath.kr/kids/algeomath/poly/make",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        time.sleep(6)
        frame = find_poly_frame(page)
        base = json.loads(frame.evaluate("() => JSON.stringify(window.AlgeomathPoly.api.save())"))
        base["scene"]["objectDatas"] = build_objects_from_blocks(blocks)
        frame.evaluate("(d) => window.AlgeomathPoly.api.load(d)", base)
        time.sleep(1)

        if screenshot:
            Path(screenshot).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=screenshot, full_page=True)

        log("status=ready")
        log(f"height_map={height_map}")
        log(f"views={views}")
        log(f"coordinates={json.dumps(coordinates, ensure_ascii=False)}")
        if screenshot:
            log(f"screenshot={screenshot}")

        while keep_open:
            time.sleep(60)
    finally:
        if not keep_open:
            browser.close()
            p.stop()


def main():
    parser = argparse.ArgumentParser(description="Inject AlgeoMath Kids 3D stackblocks.")
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        help="Use a built-in height map. reference-pyramid matches the provided sample image.",
    )
    parser.add_argument(
        "--height-map",
        required=False,
        help='JSON: [[x,y,h], ...] or {"x,y": h}; y=0 is the viewer-facing front row',
    )
    parser.add_argument(
        "--blocks",
        required=False,
        help="JSON: explicit author-space blocks [[x,y,z], ...]. Bypasses height-map expansion.",
    )
    parser.add_argument("--screenshot", help="Optional screenshot path.")
    parser.add_argument("--log", help="Optional log path.")
    parser.add_argument("--close", action="store_true", help="Close browser after injection.")
    parser.add_argument(
        "--print-coordinates",
        action="store_true",
        help="Print author-space (x,y,z), converted AlgeoMath grid coordinates, and exit.",
    )
    args = parser.parse_args()

    try:
        raw_blocks = None
        if args.blocks:
            raw_blocks = parse_blocks(args.blocks)
        elif args.preset:
            raw_height_map = dict(PRESETS[args.preset])
        elif args.height_map:
            raw_height_map = parse_height_map(args.height_map)
        else:
            parser.error("provide --blocks, --height-map, or --preset")

        if raw_blocks is not None:
            blocks = normalize_blocks(raw_blocks)
            height_map = blocks_to_height_map(blocks)
        else:
            height_map = normalize_height_map(raw_height_map)
            blocks = None

        if args.print_coordinates:
            coordinates = describe_block_coordinates(blocks) if blocks is not None else describe_coordinates(height_map)
            print(json.dumps(coordinates, ensure_ascii=False, indent=2))
            return

        inject(
            height_map=height_map,
            blocks=blocks,
            screenshot=args.screenshot,
            log_path=args.log,
            keep_open=not args.close,
        )
    except Exception:
        if args.log:
            with open(args.log, "a", encoding="utf-8") as f:
                f.write("status=error\n")
                f.write(traceback.format_exc())
        else:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
