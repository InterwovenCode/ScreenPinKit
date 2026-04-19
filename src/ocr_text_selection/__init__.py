"""Selectable OCR text layer, ported from the ``pyside6-ocr-text-selection`` project.

The module turns OCR results into a text layer that can be drag-selected and
copied inside a screenshot canvas:

* :mod:`.model` - ``Rect`` / ``OcrToken`` / ``OcrPage`` data model.
* :mod:`.page_builder` - adapter for ScreenPinKit's OCR JSON results.
* :mod:`.layout.selection` - reading order, line clustering and hit testing.
* :mod:`.ui.canvas_item` - the scene item that draws the selection highlight.
* :mod:`.ui.svg_widget` - the standalone SVG viewer from the upstream project.
"""

from .model import OcrPage, OcrToken, Rect
from .page_builder import build_page_from_ocr_json
from .ui.canvas_item import CanvasOcrTextLayerItem

__all__ = [
    "CanvasOcrTextLayerItem",
    "OcrPage",
    "OcrToken",
    "Rect",
    "build_page_from_ocr_json",
]