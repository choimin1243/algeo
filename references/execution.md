# AlgeoMath Execution Reference

Open this only when you need to run the local scripts.

## Stack Blocks

Preferred flow: compute exact block coordinates first, then inject them directly.

Inject explicit block coordinates:

```powershell
pythonw "C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py" `
  --blocks '[[x,y,z], ...]' `
  --screenshot "$env:TEMP\algeomath_stack.png" `
  --log "$env:TEMP\algeomath_stack.log"
```

Coordinate check:

```powershell
python "C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py" --preset reference-pyramid --print-coordinates
```

Inject preset:

```powershell
pythonw "C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py" `
  --preset reference-pyramid `
  --screenshot "$env:TEMP\algeomath_stack.png" `
  --log "$env:TEMP\algeomath_stack.log"
```

Inject custom height map:

```powershell
pythonw "C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py" `
  --height-map '[[x,y,h], ...]' `
  --screenshot "$env:TEMP\algeomath_stack.png" `
  --log "$env:TEMP\algeomath_stack.log"
```

## 2D

Use `scripts/algeo2d.py` and `algeo2d.md` only for flat AlgeoMath Kids 2D point, line, polygon, and coordinate-plane work.
