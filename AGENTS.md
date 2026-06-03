# AlgeoMath Skills — Codex Agent Instructions

This skill controls AlgeoMath Kids directly in the browser using Playwright.

## When to use this skill

- **3D stack blocks** (쌓기나무): cubes, layers, top/front/side views, image-based block placement
- **2D shapes** (도형): points, lines, triangles, circles, polygons, coordinate-plane drawings

## Stack Blocks — Site Access and Injection

**Target site:** https://www.algeomath.kr/kids/algeomath/poly/make  
**Harness script:** `C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py`

### Step 1 — Determine coordinates

- `x`: left to right in the image
- `y`: front to back; `y=0` is closest to viewer
- `z`: bottom to top; `z=1` is floor layer
- Never create floating cubes

For image input: identify front/back/left/right/up first, then build height map.

### Step 2 — Reset the site first (mandatory)

Before injecting any blocks, always reset the AlgeoMath scene to clear existing blocks. The harness does this automatically — never skip this step or add blocks on top of an existing scene.

### Step 3 — Inject blocks (choose one)

Explicit block list (most accurate):
```powershell
$env:PYTHONUTF8 = "1"
pythonw "C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py" `
  --blocks '[[x,y,z], ...]' `
  --screenshot "$env:TEMP\algeomath_stack.png" `
  --log "$env:TEMP\algeomath_stack.log"
```

Height map (when heights are given per column):
```powershell
$env:PYTHONUTF8 = "1"
pythonw "C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py" `
  --height-map '[[x,y,h], ...]' `
  --screenshot "$env:TEMP\algeomath_stack.png" `
  --log "$env:TEMP\algeomath_stack.log"
```

Coordinate check (dry run, no browser):
```powershell
python "C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py" `
  --blocks '[[x,y,z], ...]' --print-coordinates
```

### Step 4 — Verify

After injection, check the log for `blocks`, `views`, `screenshot` entries.

## 2D Shapes — Site Access

**Target site:** https://www.algeomath.kr/kids/algeomath/app/make  
**Script:** `C:\Users\choi2\.codex\skills\algeomath-skills\scripts\algeo2d.py`

See `algeo2d.md` for full usage.

## Reference files

| File | When to read |
|------|-------------|
| `references/stackblocks-coordinate.md` | Coordinate rules and image analysis protocol |
| `references/execution.md` | Full execution command reference |
| `algeo2d.md` | 2D shape commands |

## Known pattern — Triangular staircase pyramid (10 blocks)

```json
[[0,0,3],[1,0,2],[2,0,1],[0,1,2],[1,1,1],[0,2,1]]
```

Top view:
```
3 2 1
2 1 0
1 0 0
```
Front and side views are both `[3, 2, 1]`.
