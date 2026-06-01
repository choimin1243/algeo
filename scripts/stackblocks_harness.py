#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reusable AlgeoMath Kids 3D stackblock injection harness.

Coordinate convention for authoring:
  x = left to right from the viewer's front-facing image
  y = front to back, where y=0 is closest to the viewer
  h = column height
"""

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright


DEFAULT_COLORS = {1: 0xD89A52, 2: 0xD8893C, 3: 0xC9792F, 4: 0xB96828, 5: 0xA95A20}


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


def normalize_height_map(height_map):
    if not height_map:
        return {}
    min_x = min(x for x, _ in height_map)
    min_y = min(y for _, y in height_map)
    return {(x - min_x, y - min_y): h for (x, y), h in height_map.items() if h > 0}


def build_objects(height_map, colors=None):
    colors = colors or DEFAULT_COLORS
    max_y = max((y for _, y in height_map), default=0)
    layout = [
        (x, max_y - y, z)
        for (x, y), height in sorted(height_map.items())
        for z in range(1, height + 1)
    ]
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


def inject(height_map, screenshot=None, log_path=None, keep_open=True):
    log_file = Path(log_path) if log_path else None

    def log(message):
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with log_file.open("a", encoding="utf-8") as f:
                f.write(message + "\n")
        else:
            print(message)

    height_map = normalize_height_map(height_map)
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
        base["scene"]["objectDatas"] = build_objects(height_map)
        frame.evaluate("(d) => window.AlgeomathPoly.api.load(d)", base)
        time.sleep(1)

        if screenshot:
            Path(screenshot).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=screenshot, full_page=True)

        log("status=ready")
        log(f"height_map={height_map}")
        log(f"views={views}")
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
        "--height-map",
        required=True,
        help='JSON: [[x,y,h], ...] or {"x,y": h}; y=0 is the viewer-facing front row',
    )
    parser.add_argument("--screenshot", help="Optional screenshot path.")
    parser.add_argument("--log", help="Optional log path.")
    parser.add_argument("--close", action="store_true", help="Close browser after injection.")
    args = parser.parse_args()

    try:
        inject(
            parse_height_map(args.height_map),
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
