"""A scene item that makes the OCR result selectable inside a screenshot canvas.

This is the ScreenPinKit counterpart of the standalone ``SelectableSvgWidget``:
the canvas already paints the raster screenshot as the scene background, so this
item only draws the translucent selection highlight. The glyph geometry comes
from :class:`~ocr_text_selection.layout.selection.OcrLayout`, which resolves
reading order, line grouping and per-character hit testing.

Key behaviours (all verified against Qt5):

* :meth:`shape` is limited to the OCR boxes, so the item only intercepts the
  mouse and the I-beam cursor over recognized text. Everywhere else, clicks and
  hover events reach the drawing tools underneath.
* ``shape()`` is empty while the layer is disabled, which is how the layer steps
  aside for all drawing tools except "select item".
* ``Ctrl+C`` / ``Ctrl+A`` / ``Esc`` are only consumed while they would actually
  change the selection, so copying the image and closing the window keep
  working when no text is selected.
"""

from __future__ import annotations

from PyQt5.QtCore import QEvent, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import (
    QColor,
    QKeySequence,
    QPainter,
    QPainterPath,
)
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsWidget

from ..layout.selection import OcrLayout, SelectionRange, TextPosition
from ..model import OcrPage

# OCR glyphs come from the raster underneath, so the highlight stays translucent.
OCR_SELECTION_COLOR = QColor(0, 120, 255, 80)


class CanvasOcrTextLayerItem(QGraphicsWidget):
    """Selectable OCR text layer drawn over the screenshot background.

    The item spans the whole page but only claims the area of the OCR boxes.
    While selection is enabled it accepts left clicks, the I-beam cursor follows
    the OCR boxes, and Ctrl+A / Ctrl+C / Esc operate on the current selection.
    """

    selectionChanged = pyqtSignal(str)
    escPressed = pyqtSignal(bool)

    def __init__(
        self,
        page: OcrPage,
        parent: QGraphicsItem = None,
        enabled: bool = True,
    ) -> None:
        super().__init__(parent)
        self.page = page
        self.layoutModel = OcrLayout(page)
        self.selection: SelectionRange | None = None
        self.selectionColor = QColor(OCR_SELECTION_COLOR)
        self._dragStart: QPointF | None = None
        self._selectionEnabled = False
        self._shapePath: QPainterPath | None = None
        self.setAcceptHoverEvents(True)
        # The screenshot is a scene background, so the text layer sits above it
        # but below every drawn item.
        self.setZValue(-1)
        self.setGeometry(QRectF(0, 0, page.width, page.height))
        self.setSelectionEnabled(enabled)

    # ------------------------------------------------------------------ setup

    def setSelectionEnabled(self, enabled: bool) -> None:
        """Toggle whether this layer reacts to mouse and keyboard input."""
        self._selectionEnabled = enabled
        self.setAcceptedMouseButtons(Qt.LeftButton if enabled else Qt.NoButton)
        self.setAcceptHoverEvents(enabled)
        self.setFlag(QGraphicsItem.ItemIsFocusable, enabled)
        if not enabled:
            if self.hasFocus():
                self.clearFocus()
            self.setCursor(Qt.ArrowCursor)
            self.clearSelection()

    def setSelectionColor(self, color: QColor) -> None:
        self.selectionColor = QColor(color)
        self.update()

    # --------------------------------------------------------------- geometry

    def shape(self) -> QPainterPath:
        """Restrict hit testing to the OCR boxes.

        Qt uses ``shape()`` for hit testing, so the layer never steals clicks or
        hover events from the drawing tools outside the recognized text.
        """
        if not self._selectionEnabled:
            return QPainterPath()
        if self._shapePath is None:
            path = QPainterPath()
            path.setFillRule(Qt.WindingFill)
            for token in self.layoutModel.tokens:
                rect = token.rect
                path.addRect(QRectF(rect.left, rect.top, rect.width, rect.height))
            self._shapePath = path.simplified()
        return self._shapePath

    # --------------------------------------------------------------- painting

    def paint(self, painter: QPainter, option, widget=None) -> None:
        if self.selection is None:
            return
        bands = self.selectionRects()
        if not bands:
            return
        painter.save()
        painter.setClipRect(self.rect())
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        for band in bands:
            path.addRect(band)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.selectionColor)
        painter.drawPath(path.simplified())
        painter.restore()

    # -------------------------------------------------------------- selection

    def selectionRects(self) -> list[QRectF]:
        """One highlight band per selected line, so padded boxes merge."""
        if self.selection is None:
            return []
        return self.layoutModel.selection_bands(self.selection)

    def selectedText(self) -> str:
        if self.selection is None:
            return ""
        return self.layoutModel.selected_text(self.selection)

    def hasSelection(self) -> bool:
        return bool(self.selectedText())

    def setSelection(self, selection: SelectionRange | None) -> None:
        self.selection = selection
        self.selectionChanged.emit(self.selectedText())
        self.update()

    def clearSelection(self) -> None:
        self._dragStart = None
        if self.selection is None:
            return
        self.setSelection(None)

    def selectAll(self) -> None:
        self._dragStart = None
        tokens = self.layoutModel.tokens
        if not tokens:
            return
        last = len(tokens) - 1
        self.setSelection(
            SelectionRange(TextPosition(0), TextPosition(last, len(tokens[last].text) - 1))
        )

    def copySelection(self) -> bool:
        """Copy the selected text to the clipboard. Returns whether text existed."""
        text = self.selectedText()
        if not text:
            return False
        QApplication.clipboard().setText(text)
        return True

    # ------------------------------------------------------------------ input

    def mousePressEvent(self, event) -> None:
        if not self._selectionEnabled or event.button() != Qt.LeftButton:
            event.ignore()
            return
        self.setFocus(Qt.MouseFocusReason)
        self.clearSelection()
        self._dragStart = event.pos()
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._dragStart is not None:
            self._dragTo(event.pos())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def hoverMoveEvent(self, event) -> None:
        hit = self.layoutModel.hit_test(event.pos(), snap=False) is not None
        self.setCursor(Qt.IBeamCursor if hit else Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._dragStart is not None:
            self._dragTo(event.pos())
            self._dragStart = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def _dragTo(self, point: QPointF) -> None:
        selection = None
        if self.rect().contains(point):
            selection = self.layoutModel.selection_from_points(self._dragStart, point)
        self.setSelection(selection)

    def keyPressEvent(self, event) -> None:
        """Handle the text shortcuts, and pass through anything else.

        Ignoring a key that would have no effect lets it propagate to the
        enclosing window, which is what keeps image copy (Ctrl+C) and window
        close (Esc) working while this layer holds focus.
        """
        if event.matches(QKeySequence.Copy):
            if not self.copySelection():
                event.ignore()
                return
        elif event.matches(QKeySequence.SelectAll):
            if not self.layoutModel.tokens:
                event.ignore()
                return
            self.selectAll()
        elif event.key() == Qt.Key_Escape:
            if not self.hasSelection():
                event.ignore()
                return
            self.clearSelection()
            self.escPressed.emit(True)
        else:
            super().keyPressEvent(event)
            return
        event.accept()

    def sceneEvent(self, event) -> bool:
        """Claim the shortcuts this layer needs before window actions see them.

        The screenshot window binds Ctrl+C and Esc to QActions. Accepting the
        shortcut override keeps text copy and selection clearing working, but
        only while they would actually change the selection, so the image copy
        and Escape-to-cancel shortcuts still work when nothing is selected.
        """
        if event.type() == QEvent.ShortcutOverride:
            if event.matches(QKeySequence.SelectAll) and self.layoutModel.tokens:
                event.accept()
                return True
            if event.matches(QKeySequence.Copy) and self.hasSelection():
                event.accept()
                return True
            if event.key() == Qt.Key_Escape and self.hasSelection():
                event.accept()
                return True
        return super().sceneEvent(event)