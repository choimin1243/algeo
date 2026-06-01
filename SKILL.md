---
name: algeomath
description: Use when working with AlgeoMath Kids 2D shapes or 3D stack blocks, especially when inferring stack-block coordinates from images and placing them in AlgeoMath.
---

# AlgeoMath

Route AlgeoMath Kids work while keeping the default context small.

## Routing

- 3D stack blocks, cubes, layer counts, or image-based block placement: read `references/stackblocks-coordinate.md`.
- Running scripts or browser injection: read `references/execution.md`.
- 2D points, lines, polygons, or coordinate-plane drawings: read `algeo2d.md`.

## Stack-Block Core

- Always determine `left/right/front/back/up` before creating coordinates.
- Author coordinates are `x` left to right, `y` front to back, `z` upward.
- Layer counts are validation only.
- Prefer exact `--blocks '[[x,y,z], ...]'` injection when accuracy matters.

## Image Workflow

1. Read `references/stackblocks-coordinate.md`.
2. Count both footprint width and footprint depth.
3. Build a height map `[[x,y,h], ...]` or explicit block list `[[x,y,z], ...]`.
4. Verify top/front/side views before injection.
5. Inject through `scripts/stackblocks_harness.py`.
6. Screenshot and compare to the input image.

## Known Pattern

Triangular staircase pyramid, 10 blocks:

```json
[[0,0,3],[1,0,2],[2,0,1],[0,1,2],[1,1,1],[0,2,1]]
```

Top view:

```text
3 2 1
2 1 0
1 0 0
```

Front and side views are both `[3,2,1]`.
