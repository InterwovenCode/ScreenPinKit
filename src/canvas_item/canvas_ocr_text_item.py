# coding=utf-8
"""Canvas OCR item backed by the ported native SVG text-selection model."""

from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from ocr_text_selection.model import OcrPage, OcrToken, Rect
from ocr_text_selection.ui.canvas_item import CanvasOcrTextLayerItem


class CanvasOcrTextItem(CanvasOcrTextLayerItem):
    """Keep the canvas OCR entry point while using native text selection.

    An OcrPage shares one selection across all recognized lines. The original
    (rect, text, parent) constructor remains available for single text boxes.
    No web view or proxy widget is needed by the selection implementation.
    """

    def __init__(
        self,
        rect: QRectF | OcrPage,
        text: str = "",
        parent: QGraphicsItem = None,
        enabled: bool = True,
    ) -> None:
        if isinstance(rect, OcrPage):
            page = rect
            position = None
        else:
            position = rect.topLeft()
            page = OcrPage(
                rect.width(),
                rect.height(),
                tokens=[
                    OcrToken("ocr-0", 0, text, Rect(0, 0, rect.width(), rect.height()))
                ] if text else [],
            )
        super().__init__(page, parent=parent, enabled=enabled)
        if position is not None:
            self.setPos(position)

    def setDefaultFlag(self):
        self.setSelectionEnabled(True)