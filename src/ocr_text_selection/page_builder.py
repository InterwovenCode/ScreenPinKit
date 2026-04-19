"""Build an OCR page model from the JSON that ScreenPinKit's OCR loaders return.

Loaders answering with :class:`~ocr_loader.ocr_loader_interface.EnumOcrReturnType`
``Json`` produce a structure shaped like::

    {
        "code": 100,
        "data": [
            {"text": "hello", "box": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], "score": 0.97},
            ...
        ],
    }

Box corners are expressed in source-image pixels. Dividing them by ``dpiScale``
maps them onto the canvas scene, whose background pixmap is scaled by that same
factor, so the resulting :class:`OcrPage` is usable directly as scene geometry.
"""

from __future__ import annotations

from collections.abc import Iterable

from .model import OcrPage, OcrToken, Rect

# Same threshold the previous text layer used to drop unreliable boxes.
DEFAULT_MIN_CONFIDENCE = 0.5


def build_page_from_ocr_json(
    ocrResult: dict,
    pageWidth: float,
    pageHeight: float,
    dpiScale: float = 1.0,
    minConfidence: float = DEFAULT_MIN_CONFIDENCE,
) -> OcrPage:
    """Turn one OCR result into a page model in scene coordinates.

    ``pageWidth`` / ``pageHeight`` are the scene size of the annotated image,
    and ``dpiScale`` converts the loader's source pixels into scene units.
    """
    scale = float(dpiScale) if dpiScale else 1.0
    tokens: list[OcrToken] = []
    for info in iterOcrItems(ocrResult):
        text = str(info.get("text") or "")
        if not text:
            continue
        score = info.get("score")
        confidence = 1.0 if score is None else float(score)
        if confidence <= minConfidence:
            continue
        rect = boundingRectFromBox(info.get("box"), scale)
        if rect is None:
            continue
        order = len(tokens)
        tokens.append(
            OcrToken(
                id=f"ocr-{order}",
                order=order,
                text=text,
                rect=rect,
                confidence=confidence,
            )
        )
    # The geometry is already in scene units, so the page carries no extra scale.
    return OcrPage(float(pageWidth), float(pageHeight), 1.0, 0, tokens)


def iterOcrItems(ocrResult: dict) -> Iterable[dict]:
    """Yield the ``data`` entries of an OCR result, tolerating a bare list."""
    if isinstance(ocrResult, dict):
        data = ocrResult.get("data")
    else:
        data = ocrResult
    if not data:
        return []
    return [item for item in data if isinstance(item, dict)]


def boundingRectFromBox(box, scale: float) -> Rect | None:
    """Return the axis-aligned rect of a box polygon in scene units."""
    points = []
    for point in box or []:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        points.append((float(point[0]) / scale, float(point[1]) / scale))
    if not points:
        return None
    left = min(point[0] for point in points)
    top = min(point[1] for point in points)
    right = max(point[0] for point in points)
    bottom = max(point[1] for point in points)
    if right <= left or bottom <= top:
        return None
    return Rect(left, top, right - left, bottom - top)