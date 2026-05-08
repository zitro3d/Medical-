#!/usr/bin/env python3
"""
convert_dicoms.py — Convert a folder of DICOM files into web-viewable PNGs.

Usage:
    pip install pydicom pillow numpy
    python convert_dicoms.py

Reads ./dicoms/*.dcm, sorts by InstanceNumber, applies windowing, anonymizes,
and writes ./slices/slice_XXXX.png plus ./slices/metadata.json.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image

DICOM_DIR = Path("./dicoms")
SLICE_DIR = Path("./slices")


def auto_window(pixels: np.ndarray) -> tuple[float, float]:
    """Return (center, width) using 1%–99% percentile clipping."""
    lo = np.percentile(pixels, 1)
    hi = np.percentile(pixels, 99)
    width = max(float(hi - lo), 1.0)
    center = float((hi + lo) / 2.0)
    return center, width


def apply_window(pixels: np.ndarray, center: float, width: float) -> np.ndarray:
    """Apply DICOM windowing and return uint8 array."""
    lo = center - width / 2.0
    hi = center + width / 2.0
    clipped = np.clip(pixels, lo, hi)
    if hi > lo:
        scaled = (clipped - lo) / (hi - lo) * 255.0
    else:
        scaled = np.zeros_like(clipped)
    return scaled.astype(np.uint8)


def first_value(v):
    """DICOM tags can be MultiValue; return first scalar."""
    if v is None:
        return None
    try:
        if hasattr(v, "__iter__") and not isinstance(v, (str, bytes)):
            return list(v)[0]
    except Exception:
        pass
    return v


def instance_sort_key(ds_path):
    ds, path = ds_path
    n = getattr(ds, "InstanceNumber", None)
    try:
        return (0, int(n))
    except (TypeError, ValueError):
        return (1, path.name)


def main() -> int:
    if not DICOM_DIR.exists():
        print(f"❌ {DICOM_DIR} not found. Create it and drop your .dcm files in.")
        return 1

    SLICE_DIR.mkdir(exist_ok=True)

    dcm_files = sorted(DICOM_DIR.glob("*.dcm")) + sorted(DICOM_DIR.glob("*.DCM"))
    if not dcm_files:
        print(f"❌ No .dcm files in {DICOM_DIR}.")
        return 1

    loaded = []
    for path in dcm_files:
        try:
            ds = pydicom.dcmread(str(path), force=True)
            _ = ds.pixel_array
            loaded.append((ds, path))
        except Exception as exc:
            print(f"⚠️  Skipping {path.name}: {exc}")

    if not loaded:
        print("❌ No readable DICOM files with pixel data.")
        return 1

    loaded.sort(key=instance_sort_key)

    first_ds = loaded[0][0]

    wc_tag = first_value(getattr(first_ds, "WindowCenter", None))
    ww_tag = first_value(getattr(first_ds, "WindowWidth", None))

    saved = 0
    metadata_window_center = None
    metadata_window_width = None

    for idx, (ds, path) in enumerate(loaded, start=1):
        try:
            pixels = ds.pixel_array.astype(np.float32)

            slope = float(getattr(ds, "RescaleSlope", 1) or 1)
            intercept = float(getattr(ds, "RescaleIntercept", 0) or 0)
            pixels = pixels * slope + intercept

            wc = first_value(getattr(ds, "WindowCenter", None))
            ww = first_value(getattr(ds, "WindowWidth", None))
            try:
                wc = float(wc) if wc is not None else None
                ww = float(ww) if ww is not None else None
            except (TypeError, ValueError):
                wc, ww = None, None

            if wc is None or ww is None or ww <= 0:
                wc, ww = auto_window(pixels)

            if metadata_window_center is None:
                metadata_window_center = wc
                metadata_window_width = ww

            arr8 = apply_window(pixels, wc, ww)

            photometric = str(getattr(ds, "PhotometricInterpretation", "")).strip()
            if photometric == "MONOCHROME1":
                arr8 = 255 - arr8

            img = Image.fromarray(arr8, mode="L")
            out_path = SLICE_DIR / f"slice_{idx:04d}.png"
            img.save(out_path, format="PNG", optimize=True)
            saved += 1
        except Exception as exc:
            print(f"⚠️  Failed to convert {path.name}: {exc}")

    if saved == 0:
        print("❌ Nothing converted.")
        return 1

    rows = int(getattr(first_ds, "Rows", 0) or 0)
    cols = int(getattr(first_ds, "Columns", 0) or 0)

    slice_thickness = getattr(first_ds, "SliceThickness", None)
    if slice_thickness is not None:
        slice_thickness_str = f"{float(slice_thickness):g}mm"
    else:
        slice_thickness_str = "unknown"

    pixel_spacing = getattr(first_ds, "PixelSpacing", None)
    if pixel_spacing is not None and len(pixel_spacing) >= 2:
        pixel_spacing_str = f"{float(pixel_spacing[0]):g}mm x {float(pixel_spacing[1]):g}mm"
    else:
        pixel_spacing_str = "unknown"

    metadata = {
        "total_slices": saved,
        "patient_id": "ANON",
        "study_description": str(getattr(first_ds, "StudyDescription", "") or ""),
        "series_description": str(getattr(first_ds, "SeriesDescription", "") or ""),
        "modality": str(getattr(first_ds, "Modality", "") or ""),
        "slice_thickness": slice_thickness_str,
        "pixel_spacing": pixel_spacing_str,
        "rows": rows,
        "cols": cols,
        "window_center": (
            float(wc_tag) if wc_tag not in (None, "") and _is_number(wc_tag)
            else (round(metadata_window_center, 2) if metadata_window_center is not None else None)
        ),
        "window_width": (
            float(ww_tag) if ww_tag not in (None, "") and _is_number(ww_tag)
            else (round(metadata_window_width, 2) if metadata_window_width is not None else None)
        ),
    }

    with open(SLICE_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("⚠️  Patient identifiers removed from metadata.json")
    print(f"✅ Converted {saved} slices → ./slices/ — open index.html to view")
    return 0


def _is_number(x) -> bool:
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


if __name__ == "__main__":
    sys.exit(main())
