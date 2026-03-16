#!/usr/bin/env python3
"""Generate Markdown or page images from a PDF file."""

from __future__ import annotations

import argparse
import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Sequence

import fitz
import pymupdf4llm


@contextmanager
def chdir(path: Path) -> Iterator[None]:
    """Temporarily change the current working directory."""
    old_cwd = Path.cwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(str(old_cwd))


def normalize_markdown(text: str) -> str:
    """Apply small cleanup passes to generated markdown."""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    normalized = "\n".join(lines).strip() + "\n"
    return normalized


def default_asset_dir(output_path: Path) -> Path:
    """Return the default asset directory for a markdown output file."""
    return output_path.with_name("{0}_assets".format(output_path.stem))


def export_pdf_text(
    pdf_path: Path,
    output_path: Path,
    dpi: int,
    page_separators: bool,
    asset_dir: Optional[Path] = None,
) -> None:
    """Export one PDF as markdown and extracted inline image assets."""
    pdf_path = pdf_path.resolve()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    asset_dir = (asset_dir or default_asset_dir(output_path)).resolve()
    if asset_dir.exists():
        shutil.rmtree(str(asset_dir))
    asset_dir.mkdir(parents=True, exist_ok=True)

    with chdir(output_path.parent):
        markdown = pymupdf4llm.to_markdown(
            str(pdf_path),
            write_images=True,
            image_path=asset_dir.name,
            page_separators=page_separators,
            force_text=False,
            show_progress=False,
            dpi=dpi,
        )

    content = normalize_markdown(markdown)
    output_path.write_text(content, encoding="utf-8")


def _page_number_width(page_count: int) -> int:
    """Return the zero-padding width for page image filenames."""
    return max(4, len(str(page_count)))


def export_pdf_page_images(pdf_path: Path, output_dir: Path, dpi: int) -> None:
    """Export every PDF page as ``page-XXXX.png`` into ``output_dir``."""
    pdf_path = pdf_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for stale_path in output_dir.glob("page-*.png"):
        stale_path.unlink()

    with fitz.open(str(pdf_path)) as document:
        page_count = document.page_count
        width = _page_number_width(page_count)
        scale = float(dpi) / 72.0
        matrix = fitz.Matrix(scale, scale)

        for page_index in range(page_count):
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            output_path = output_dir / "page-{0:0{1}d}.png".format(page_index + 1, width)
            pixmap.save(str(output_path))


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Convert one PDF to markdown or per-page images.")
    parser.add_argument("-i", "--input-pdf", required=True, help="Input PDF file.")
    parser.add_argument(
        "-ot",
        "--output-type",
        required=True,
        choices=("text", "image"),
        help="Export mode: text or image.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output markdown file path in text mode, or output directory in image mode.",
    )
    parser.add_argument("-d", "--dpi", type=int, default=150, help="DPI for rendered or extracted images.")
    parser.add_argument(
        "-n",
        "--no-page-separators",
        action="store_true",
        help="Do not emit page separator markers into generated markdown.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entrypoint."""
    args = parse_args(argv)
    pdf_path = Path(args.input_pdf)
    if not pdf_path.is_file():
        raise FileNotFoundError("Missing input PDF: {0}".format(pdf_path))

    output_path = Path(args.output)
    if args.output_type == "text":
        print("Generating markdown for {0}".format(pdf_path))
        export_pdf_text(
            pdf_path,
            output_path,
            dpi=args.dpi,
            page_separators=not args.no_page_separators,
        )
    elif args.output_type == "image":
        print("Generating page images for {0}".format(pdf_path))
        export_pdf_page_images(
            pdf_path,
            output_path,
            dpi=args.dpi,
        )
    else:
        raise ValueError("Unsupported output type: {0}".format(args.output_type))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
