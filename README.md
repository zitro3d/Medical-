# MRI DICOM Web Viewer

**Live:** https://zitro3d.github.io/mri-viewer/

A single-file MRI viewer. No install, no build step, no server, no internet.
Open the page, drag your folder of DICOMs in, view.

---

## Use it

**Online:** open https://zitro3d.github.io/mri-viewer/

**Offline:** download `index.html` from the repo, double-click it. Works in
any browser (Chrome, Edge, Firefox, Safari) directly from `file://`.

Then:

1. Drag a folder of `.dcm` files onto the window — or click **Pick Folder**.
2. If the study has multiple series, pick one from the left sidebar.
3. Scroll with the wheel or arrow keys.

Parsing and rendering happen entirely in the browser. No upload, no network
call. Patient identifiers are never displayed.

---

## Controls

| Key / Action       | Effect                          |
| ------------------ | ------------------------------- |
| `↑` / `↓`          | Previous / next slice           |
| Mouse wheel        | Scroll slices                   |
| `Ctrl` + wheel     | Zoom                            |
| `Alt` + drag       | Pan                             |
| Drag (no modifier) | Brightness (Y) / Contrast (X)   |
| `R` or dbl-click   | Reset view                      |
| `I`                | Toggle metadata panel           |
| `C`                | Toggle compare mode             |
| `?`                | Toggle help                     |

In compare mode, **Set Reference** locks the left panel so you can scrub
the right panel against a fixed slice.

The right-edge **heatmap strip** colors each slice by mean brightness —
click or drag to jump. Notable slices (top 15% bright = yellow, top 5% =
red) are flagged on the bottom slider and listed in the **Notable** panel.

---

## What it can read

- Uncompressed DICOM (Implicit / Explicit VR Little / Big Endian) — covers
  virtually all MRI and CT exports.
- JPEG-Lossless (`1.2.840.10008.1.2.4.57` / `.70`) — the default for most
  clinical MRI/CT.
- RLE Lossless (`1.2.840.10008.1.2.5`).
- Files with or without a `.dcm` extension. Non-DICOM files are skipped.

If anything else is encountered, the drop screen prints which transfer
syntaxes were skipped so a decoder can be added.

---

## Privacy

Everything stays on your machine. The page reads your folder via the
browser's File API — no upload, no remote API calls. The DICOM parser
(`dicom-parser`) and JPEG-Lossless decoder (`jpeg-lossless-decoder-js`)
are bundled inline in `index.html`. Patient identifiers parsed from the
DICOMs are intentionally not displayed; the metadata panel shows only
study, series, modality, geometry, and windowing.
