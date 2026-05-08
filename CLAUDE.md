# CLAUDE.md — MRI DICOM Web Viewer

## Project Overview

Build a fully self-contained GitHub Pages web app that:
1. Reads a local folder of DICOM files (`.dcm`)
2. Converts them into web-viewable PNG images using a Python script
3. Generates an `index.html` that is a full MRI slice exploration tool

This is a one-time personal tool in the spirit of Tobi Lütke's approach — highly functional, no fluff.

---

## Repository Structure (Target)

```
/
├── CLAUDE.md
├── convert_dicoms.py
├── index.html
├── slices/
│   ├── slice_0001.png
│   └── metadata.json
└── dicoms/
    └── *.dcm   ← drop your files here
```

---

## Step 1 — convert_dicoms.py

Write a Python script that:

- Installs via: `pip install pydicom pillow numpy`
- Scans `./dicoms/` for all `.dcm` files
- Sorts by `InstanceNumber` DICOM tag (fallback: filename)
- For each file:
  - Extracts pixel array with `pydicom`
  - Applies windowing using `WindowCenter`/`WindowWidth` tags if present, otherwise auto-windows using 1%–99% percentile clipping
  - Normalizes to uint8 (0–255)
  - Saves to `./slices/slice_XXXX.png` (zero-padded 4 digits)
- Saves `./slices/metadata.json`:
  ```json
  {
    "total_slices": 120,
    "patient_id": "ANON",
    "study_description": "...",
    "series_description": "...",
    "modality": "MR",
    "slice_thickness": "3.0mm",
    "pixel_spacing": "0.5mm x 0.5mm",
    "rows": 512,
    "cols": 512,
    "window_center": 400,
    "window_width": 1500
  }
  ```
- **Anonymizes by default**: strips PatientName, PatientBirthDate, PatientID → replaces with "ANON"
- Prints: `⚠️  Patient identifiers removed from metadata.json`
- Handles corrupt files gracefully (skip + log)
- Ends with: `✅ Converted XX slices → ./slices/ — open index.html to view`

---

## Step 2 — index.html

Single self-contained file. All CSS and JS inline. No build step.

### Visual Design

```
Background:   #0a0a0a
Surface:      #141414
Border:       #2a2a2a
Accent:       #00e5ff  (cyan)
Warn:         #ffcc00
Danger:       #ff3b3b
Text:         #e8e8e8
Muted:        #666666
Font:         'JetBrains Mono', monospace
```

No rounded corners on image panels. Subtle scanline texture overlay on image area
(`repeating-linear-gradient` at 3% opacity). Flat minimal controls.

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  [Compare] [Notable] [Info]              MRI VIEWER  Slice 42/120 │
├─────────────┬─────────────────────────────────────────┬──────────┤
│             │                                         │  Heat    │
│  Metadata   │         Main Image Canvas               │  Map     │
│  Panel      │         (two panels in compare mode)    │  Strip   │
│  (collapse) │                                         │          │
├─────────────┴─────────────────────────────────────────┴──────────┤
│  < [════════════════●═══════════════════] >   Slice 42 / 120     │
└──────────────────────────────────────────────────────────────────┘
```

### Navigation
- Mouse wheel scrolls slices (preventDefault scroll)
- Arrow Up/Down navigate slices
- Bottom slider scrubs position
- `Slice 42 / 120` counter updates in real-time

### Image Controls
- Click+drag on image: horizontal = contrast, vertical = brightness (CSS filter)
- Ctrl+scroll: zoom in/out
- Alt+drag: pan when zoomed
- Double-click or R: reset all transforms

### Compare Mode (C key or button)
- Splits into two panels
- Left: locked reference slice ("Set Reference" button)
- Right: actively scrollable
- Shared zoom/level settings

### Auto Annotation
- After load: sample each slice brightness with offscreen canvas
- Top 15% brightness → yellow dot on slider
- Top 5% → red dot
- Right-side heatmap strip: one pixel row per slice, colored by brightness
- Hover heatmap → jump to that slice
- "Notable Slices" panel: clickable list of flagged slices

### Metadata Panel
- Collapsible sidebar, toggle with I key or info button
- Shows all metadata.json fields
- Monospace font, clean layout

### Keyboard Help (? key)
```
↑ / ↓         Previous / Next slice
Mouse Wheel   Scroll slices
Ctrl+Wheel    Zoom
Alt+Drag      Pan
R             Reset view
I             Toggle info panel
C             Toggle compare mode
?             Show/hide help
```

### JavaScript Architecture (vanilla JS only)

```javascript
const state = {
  currentSlice: 0,
  totalSlices: 0,
  zoom: 1,
  panX: 0,
  panY: 0,
  brightness: 100,
  contrast: 100,
  compareMode: false,
  referenceSlice: 0,
  metadata: {},
  sliceBrightness: [],
}
```

- Preload sliding window: current slice ±20
- Image paths: `./slices/slice_${String(n).padStart(4, '0')}.png`
- Load metadata.json on startup to get total_slices and study info

### Deployment comment block at top of index.html:
```
DEPLOYMENT:
1. python convert_dicoms.py
2. git add slices/ index.html && git commit -m "MRI viewer" && git push
3. Settings > Pages > Deploy from main /root
4. Visit: https://yourusername.github.io/yourrepo/

LOCAL: python -m http.server 8080

PRIVACY: Medical images present. Keep repo private or serve locally only.
```

---

## Deliverables

1. `convert_dicoms.py` — working converter, anonymizes patient data
2. `index.html` — complete single-file viewer, all features above
3. `README.md` — setup: pip install, drop dicoms, run script, serve locally, deploy to Pages

Write complete working code. No placeholder stubs. No TODO comments.
