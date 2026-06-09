"""Crop generated graph plots to their content bounding box.

matplotlib's ``bbox_inches="tight"`` still leaves a uniform white margin around
the conversion-graph figures. This trims that margin so the PNGs embed tightly in
the manuscript without manual cropping. It uses only numpy + matplotlib, so it
adds no Pillow dependency.

Usage::

    python eval/crop_to_content.py                       # crop the two default graphs
    python eval/crop_to_content.py a.png b.png           # crop specific files
    python eval/crop_to_content.py --padding 12 a.png    # keep a wider margin
    python eval/crop_to_content.py --suffix _cropped a.png  # write a copy, don't overwrite
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import matplotlib.image as mpimg

EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_PLOTS_DIR = EVAL_DIR / "results" / "orchestrator_outputs" / "plots"
DEFAULT_TARGETS = [
    DEFAULT_PLOTS_DIR / "conversion_graph_all_languages.png",
    DEFAULT_PLOTS_DIR / "conversion_graph_edge_robustness.png",
]


def crop_to_content(
    path: str | Path,
    out_path: str | Path | None = None,
    padding: int = 8,
    tolerance: float = 0.02,
) -> Path:
    """Crop a PNG to the bounding box of its non-white (non-transparent) content.

    ``padding`` keeps a small white margin (in pixels) around the content;
    ``tolerance`` (0..1) is how far from pure white still counts as background.
    Returns the path that was written.
    """
    path = Path(path)
    image = mpimg.imread(path)
    if image.ndim == 2:  # grayscale -> treat as RGB
        image = np.stack([image] * 3, axis=-1)

    rgb = image[..., :3]
    content = np.any(rgb < (1.0 - tolerance), axis=-1)
    if image.shape[-1] == 4:  # respect transparency: fully transparent == background
        content &= image[..., 3] > tolerance

    if not content.any():
        raise ValueError(f"{path} appears to be blank; nothing to crop.")

    rows = np.where(content.any(axis=1))[0]
    cols = np.where(content.any(axis=0))[0]
    top = max(int(rows[0]) - padding, 0)
    bottom = min(int(rows[-1]) + padding + 1, image.shape[0])
    left = max(int(cols[0]) - padding, 0)
    right = min(int(cols[-1]) + padding + 1, image.shape[1])

    cropped = image[top:bottom, left:right]
    out_path = Path(out_path) if out_path is not None else path
    mpimg.imsave(out_path, cropped)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "images",
        nargs="*",
        type=Path,
        help="PNG files to crop (default: the two conversion-graph plots).",
    )
    parser.add_argument("--padding", type=int, default=8, help="White margin to keep, in pixels.")
    parser.add_argument("--tolerance", type=float, default=0.02, help="How close to white still counts as background (0..1).")
    parser.add_argument("--suffix", default="", help="If set, write to <name><suffix>.png instead of overwriting in place.")
    args = parser.parse_args()

    targets = args.images or DEFAULT_TARGETS
    for target in targets:
        target = Path(target)
        if not target.exists():
            print(f"Skipping missing file: {target}")
            continue
        out = target.with_name(target.stem + args.suffix + target.suffix) if args.suffix else target
        h0, w0 = mpimg.imread(target).shape[:2]
        crop_to_content(target, out, padding=args.padding, tolerance=args.tolerance)
        h1, w1 = mpimg.imread(out).shape[:2]
        print(f"Cropped {target.name}: {w0}x{h0} -> {w1}x{h1} -> {out}")


if __name__ == "__main__":
    main()
