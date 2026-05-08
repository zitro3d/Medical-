# MRI DICOM Web Viewer

A single-file MRI viewer. **No install. No build step. No server.**
Double-click the HTML file, drag your folder of DICOMs in, view.

---

## Use it

1. Save / download `index.html` anywhere on your computer.
2. Double-click it. (Chrome, Edge, Firefox, or Safari.)
3. Drag a folder of `.dcm` files onto the window — or click **Pick Folder**.

That's it. Parsing happens locally in the browser — nothing is uploaded
anywhere. Patient identifiers are never displayed.

> Internet is required on first open so the page can fetch the DICOM parser
> (`daikon`) from a CDN. The browser caches it after that, so subsequent
> opens work offline.

---

## Update workflow

There is no update workflow. Open the file, drop a different folder, done.
Click **New Folder** in the top bar to load a different study without
reloading the page.

---

## Controls

| Key / Action      | Effect                          |
| ----------------- | ------------------------------- |
| `↑` / `↓`         | Previous / next slice           |
| Mouse wheel       | Scroll slices                   |
| `Ctrl` + wheel    | Zoom                            |
| `Alt` + drag      | Pan                             |
| Drag (no modifier)| Brightness (Y) / Contrast (X)   |
| `R` or dbl-click  | Reset view                      |
| `I`               | Toggle metadata panel           |
| `C`               | Toggle compare mode             |
| `?`               | Toggle help                     |

In compare mode, **Set Reference** locks the left panel so you can scrub the
right panel against a fixed slice.

The right-edge **heatmap strip** colors each slice by mean brightness — click
or drag to jump. Notable slices (top 15% bright = yellow, top 5% = red) are
flagged on the bottom slider and listed in the **Notable** panel.

---

## (Optional) Host on GitHub Pages

If you want a URL instead of a local file:

```bash
git add index.html
git commit -m "MRI viewer"
git push
```

Then **Settings → Pages → Deploy from main /root** in your repo.
The viewer never uploads or stores DICOM data — folders are read locally
even when the page is loaded from a public URL.

---

## What it can read

- Uncompressed DICOM (Implicit/Explicit VR Little Endian) — virtually all MRI
  and CT exports.
- Most JPEG-Lossless / JPEG-LS / RLE transfer syntaxes (via `daikon`).
- Files with or without a `.dcm` extension.

If a file in the folder isn't a DICOM, it's silently skipped.

---

## Privacy

Everything stays on your machine. The page reads your folder via the
browser's File API — no upload, no network call other than the one-time
fetch of the parser library. Patient identifiers parsed from the DICOMs
are intentionally not displayed; the metadata panel shows only study,
series, modality, geometry, and windowing.
