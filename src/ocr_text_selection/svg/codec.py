"""Serialize OCR results as a lightweight SVG selection layer.

The generated document keeps only the geometry the selection layer needs, so it
stays small and can be re-loaded without the original image.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ..model import OcrPage, OcrToken, Rect

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
_SVG = f"{{{SVG_NAMESPACE}}}"
_NUMBER = ".17g"
_GEOMETRY_KEYS = ("data-ocr-left", "data-ocr-top", "data-ocr-width", "data-ocr-height")

ET.register_namespace("", SVG_NAMESPACE)


def _format(value: float) -> str:
    """Format a float so that parsing restores the exact same value."""
    return f"{value:{_NUMBER}}"


def build_ocr_svg(page: OcrPage, font_family: str = "Arial") -> str:
    """Build an SVG text layer mirroring each OCR box.

    Nodes use ``fill="none"``: the raster image supplies the visible glyphs,
    while these nodes carry the selectable geometry. ``parse_ocr_svg`` restores
    the exact :class:`OcrPage` from the ``data-ocr-*`` attributes.
    """
    root = ET.Element(
        f"{_SVG}svg",
        {
            "width": _format(page.width),
            "height": _format(page.height),
            "viewBox": f"0 0 {_format(page.width)} {_format(page.height)}",
            "data-page": str(page.page_index),
            "data-dpi-scale": _format(page.dpi_scale),
        },
    )
    for token in sorted(page.tokens, key=lambda item: item.order):
        rect = token.rect
        size = max(1.0, rect.height * 0.8)
        element = ET.SubElement(
            root,
            f"{_SVG}text",
            {
                "x": _format(rect.left),
                "y": _format(rect.top + size),
                "font-family": font_family,
                "font-size": _format(size),
                "fill": "none",
                "data-ocr-id": token.id,
                "data-ocr-order": str(token.order),
                "data-confidence": _format(token.confidence),
                "data-ocr-left": _format(rect.left),
                "data-ocr-top": _format(rect.top),
                "data-ocr-width": _format(rect.width),
                "data-ocr-height": _format(rect.height),
            },
        )
        element.text = token.text
    return ET.tostring(root, encoding="unicode")


def _page_size(root: ET.Element) -> tuple[float, float]:
    width = root.get("width")
    height = root.get("height")
    if width is not None and height is not None:
        return float(width), float(height)
    view_box = (root.get("viewBox") or "").replace(",", " ").split()
    if len(view_box) != 4:
        raise ValueError("OCR SVG is missing width/height or a four-number viewBox")
    return float(view_box[2]), float(view_box[3])


def _token(element: ET.Element, fallback_order: int) -> OcrToken:
    attributes = element.attrib
    missing = [key for key in _GEOMETRY_KEYS if attributes.get(key) is None]
    if missing:
        raise ValueError(f"OCR SVG text is missing attributes: {missing}")
    values = {key: float(attributes[key]) for key in _GEOMETRY_KEYS}
    if values["data-ocr-width"] <= 0 or values["data-ocr-height"] <= 0:
        raise ValueError("OCR SVG text dimensions must be positive")
    return OcrToken(
        id=attributes.get("data-ocr-id") or f"ocr-{fallback_order}",
        order=int(attributes.get("data-ocr-order") or fallback_order),
        text="".join(element.itertext()),
        rect=Rect(
            values["data-ocr-left"],
            values["data-ocr-top"],
            values["data-ocr-width"],
            values["data-ocr-height"],
        ),
        confidence=float(attributes.get("data-confidence") or 1.0),
    )


def parse_ocr_svg(source: str | bytes) -> OcrPage:
    """Restore the :class:`OcrPage` written by :func:`build_ocr_svg`."""
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"Invalid SVG document: {error}") from error
    if root.tag != f"{_SVG}svg":
        raise ValueError("Expected an SVG document")
    try:
        width, height = _page_size(root)
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid OCR page dimensions") from error
    try:
        dpi_scale = float(root.get("data-dpi-scale") or 1)
        page_index = int(root.get("data-page") or 0)
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid OCR page metadata") from error
    tokens = []
    for element in root.iter(f"{_SVG}text"):
        tokens.append(_token(element, len(tokens)))
    return OcrPage(width, height, dpi_scale, page_index, tokens)