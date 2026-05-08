# MRI DICOM Web Viewer

A self-contained, single-page MRI viewer that reads a folder of DICOM files,
converts them to PNGs with a small Python script, and serves them through a
single `index.html` with brightness/contrast, zoom/pan, compare mode, an
auto-generated heatmap, and notable-slice flagging.

No build step. No frameworks. Vanilla JS + a Python converter.

---

## Setup

```bash
pip install pydicom pillow numpy
```

Drop your DICOM files into `./dicoms/`:

```
dicoms/
├── IM0001.dcm
├── IM0002.dcm
└── ...
```

## Convert

```bash
python convert_dicoms.py
```

This will:

- Sort by `InstanceNumber` (falls back to filename)
- Apply DICOM windowing (`WindowCenter` / `WindowWidth`) or auto-window via
  1%–99% percentile clipping
- Save `slices/slice_0001.png`, `slice_0002.png`, … (zero-padded, 4 digits)
- Write `slices/metadata.json` with study info
- **Strip patient identifiers** (`PatientName`, `PatientBirthDate`, `PatientID`
  → `"ANON"`)

Output ends with:

```
⚠️  Patient identifiers removed from metadata.json
✅ Converted XX slices → ./slices/ — open index.html to view
```

## View Locally

```bash
python -m http.server 8080
```

Then open <http://localhost:8080/>.

(Opening `index.html` directly via `file://` will not work because the page
fetches `slices/metadata.json` over HTTP.)

---

## Deploy to GitHub Pages

```bash
git add slices/ index.html
git commit -m "MRI viewer"
git push
```

In your repo: **Settings → Pages → Deploy from main /root**.

Visit `https://<your-username>.github.io/<your-repo>/`.

> **Privacy:** medical images are present. Keep the repo private or serve
> locally only. The converter strips patient identifiers from metadata, but
> pixel data may still be identifying.

---

## Controls

| Key / Action      | Effect                          |
| ----------------- | ------------------------------- |
| `↑` / `↓`         | Previous / next slice           |
| Mouse wheel       | Scroll slices                   |
| `Ctrl` + wheel    | Zoom                            |
| `Alt` + drag      | Pan                             |
| Drag (no mod)     | Brightness (Y) / Contrast (X)   |
| `R` or dbl-click  | Reset view                      |
| `I`               | Toggle metadata panel           |
| `C`               | Toggle compare mode             |
| `?`               | Toggle help                     |

In compare mode, **Set Reference** locks the left panel to the current slice
while you scrub the right panel.

The right-edge **heatmap strip** colors each slice by mean brightness — click
or drag to jump. Notable slices (top 15% bright = yellow, top 5% = red) are
flagged on the bottom slider and listed in the **Notable** panel.

---

## File Layout

```
/
├── CLAUDE.md
├── README.md
├── convert_dicoms.py
├── index.html
├── dicoms/        ← drop .dcm files here
└── slices/        ← generated PNGs + metadata.json
```
