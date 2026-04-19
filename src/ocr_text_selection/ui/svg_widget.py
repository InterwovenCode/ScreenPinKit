"""Native SVG display with a selectable layer for horizontal SVG text.

Ported from the PySide6 ``pyside6-ocr-text-selection`` project to PyQt5 so it
can be reused alongside the rest of ScreenPinKit. ``CanvasOcrTextLayerItem``
in :mod:`.canvas_item` handles the in-scene OCR case; this module keeps the
standalone widget API (``load()`` / ``load_ocr_page()``) available.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PyQt5.QtCore import QByteArray, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QImage,
    QKeySequence,
    QPainter,
    QPainterPath,
)
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QToolBar

from ..layout.selection import (
    OcrLayout,
    SelectionRange,
    TextPosition,
)
from ..model import OcrPage, OcrToken, Rect
from ..svg.codec import build_ocr_svg

# Native SVG text is repainted over its highlight, so it must stay opaque.
DEFAULT_SELECTION_COLOR = QColor("#3264dc")
# OCR glyphs come from the raster underneath, so the highlight stays translucent.
OCR_SELECTION_COLOR = QColor(0, 120, 255, 80)


class SelectableSvgWidget(QSvgWidget):
    """QSvgWidget with drag selection, Ctrl+A/C and Escape.

    Load SVG documents through `load()` so display and selection metadata stay
    synchronized. Use `load_ocr_page()` to show OCR boxes over their source
    raster; there the OCR text is an invisible selection layer and the image
    keeps supplying the visible glyphs.

    Unsupported text remains visible, but is excluded from selection and
    reported in `selection_warnings`.
    """

    selection_changed = pyqtSignal(str)

    def __init__(self, source=None, parent=None):
        super().__init__(parent)
        self.layout_model: OcrLayout | None = None
        self.selection: SelectionRange | None = None
        self.selection_warnings: list[str] = []
        self.selection_color = QColor(DEFAULT_SELECTION_COLOR)
        self.background: QImage | None = None
        self.repaint_text_on_selection = True
        self.merge_line_bands = False
        self._text_renderer = QSvgRenderer(self)
        self._drag_start: QPointF | None = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        if source is not None:
            self.load(source)

    def load(self, source) -> None:
        """Load a file or SVG bytes. Invalid input leaves the previous SVG intact."""
        data = Path(source).read_bytes() if isinstance(source, (str, Path)) else bytes(source)
        root = ET.fromstring(data)
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Expected an SVG document")
        # IDs give access to Qt's own text bounds and ancestor transforms.
        used_ids = {e.get("id") for e in root.iter()}
        text_elements = []
        warnings = []

        def visit(element, inherited, excluded=False):
            tag = element.tag.rsplit("}", 1)[-1]
            style = dict(inherited)
            style.update(element.attrib)
            style.update(dict(re.findall(r"([\w-]+)\s*:\s*([^;]+)", element.get("style", ""))))
            excluded = excluded or tag in ("defs", "clipPath", "mask", "symbol")
            excluded = excluded or style.get("display") == "none"
            if (
                tag == "text"
                and not excluded
                and style.get("visibility") not in ("hidden", "collapse")
            ):
                if len(element) or any(
                    len(element.get(key, "").replace(",", " ").split()) > 1
                    for key in ("x", "y", "dx", "dy", "rotate")
                ):
                    warnings.append("Nested or individually positioned SVG text is not selectable.")
                elif style.get("direction") == "rtl" or style.get(
                    "writing-mode", "horizontal-tb"
                ) not in ("horizontal-tb", "lr", "lr-tb"):
                    warnings.append("Vertical or RTL SVG text is not selectable.")
                else:
                    identifier = element.get("id")
                    if not identifier:
                        identifier = f"__selection_text_{len(text_elements)}"
                        while identifier in used_ids:
                            identifier += "_"
                        element.set("id", identifier)
                        used_ids.add(identifier)
                    text_elements.append((element, style))
            for child in element:
                visit(child, style, excluded)

        visit(root, {})
        prepared = QByteArray(ET.tostring(root, encoding="utf-8"))
        renderer = QSvgRenderer(prepared)
        if not renderer.isValid() or renderer.viewBoxF().isEmpty():
            raise ValueError("SVG has no valid renderable viewport")
        view_box = renderer.viewBoxF()
        tokens = []
        fonts = {}
        for element, style in text_elements:
            identifier = element.get("id")
            text = element.text or ""
            if (
                style.get("white-space") != "pre"
                and element.get("{http://www.w3.org/XML/1998/namespace}space") != "preserve"
            ):
                text = re.sub(r"\s+", " ", text).strip()
            if not text:
                continue
            transform = renderer.transformForElement(identifier)
            # The existing selection model is horizontal. Do not silently turn
            # rotated/skewed glyphs into inaccurate axis-aligned hit targets.
            own_transform = element.get("transform", "")
            if (
                abs(transform.m12()) > 1e-6
                or abs(transform.m21()) > 1e-6
                or transform.m11() <= 0
                or transform.m22() <= 0
                or re.search(r"rotate|skew|matrix", own_transform)
            ):
                warnings.append(f"Transformed text {identifier!r} is not selectable.")
                continue
            bounds = transform.mapRect(renderer.boundsOnElement(identifier))
            bounds.translate(-view_box.x(), -view_box.y())
            if bounds.isEmpty():
                continue
            font = QFont()
            families = [
                name.strip().strip("\"'") for name in style.get("font-family", "Arial").split(",")
            ]
            if hasattr(font, "setFamilies"):
                font.setFamilies(families)
            elif families:
                font.setFamily(families[0])
            size = re.match(r"[\d.]+", style.get("font-size", "16"))
            font.setPixelSize(max(1, round(float(size.group()) if size else 16)))
            font.setBold(style.get("font-weight", "") in ("bold", "700", "800", "900"))
            font.setItalic(style.get("font-style") in ("italic", "oblique"))
            fonts[identifier] = font
            tokens.append(
                OcrToken(
                    identifier,
                    len(tokens),
                    text,
                    Rect(bounds.x(), bounds.y(), bounds.width(), bounds.height()),
                )
            )
        layout = OcrLayout(OcrPage(view_box.width(), view_box.height(), tokens=tokens))
        # Respect each text element's font instead of using the OCR default.
        for index, token in enumerate(layout.tokens):
            metrics = QFontMetricsF(fonts[token.id])
            widths = [max(metrics.horizontalAdvance(c), 0.01) for c in token.text]
            scale = token.rect.width / sum(widths)
            x = token.rect.left
            rects = []
            for width in widths:
                rects.append(QRectF(x, token.rect.top, width * scale, token.rect.height))
                x += width * scale
            layout.character_rects[index] = rects
        # Repaint original vector text over the opaque selection background.
        # Rendering the full SVG here would also repaint its background shapes.
        text_root = copy.deepcopy(root)

        def retain_text(element):
            if element.tag.rsplit("}", 1)[-1] in ("text", "defs", "style"):
                return True
            for child in list(element):
                if not retain_text(child):
                    element.remove(child)
            return len(element) > 0

        retain_text(text_root)
        self._text_renderer.load(QByteArray(ET.tostring(text_root, encoding="utf-8")))
        self._text_renderer.setAspectRatioMode(Qt.IgnoreAspectRatio)
        self.background = None
        self.repaint_text_on_selection = True
        self.merge_line_bands = False
        self.selection_color = QColor(DEFAULT_SELECTION_COLOR)
        self._install(prepared, layout, warnings)

    def load_ocr_page(self, page: OcrPage, image, *, selection_color: QColor | None = None) -> None:
        """Show OCR boxes over their source raster.

        The generated SVG text is an invisible selection layer, so the visible
        glyphs come from the raster image and the highlight stays translucent.
        Selection geometry comes from `page` directly, which keeps it exact
        instead of depending on Qt's text bounds.
        """
        if isinstance(image, (str, Path)):
            loaded = QImage(str(image))
            if loaded.isNull():
                raise ValueError(f"Unable to load image: {image}")
            image = loaded
        if image.isNull():
            raise ValueError("Unable to load image")
        prepared = QByteArray(build_ocr_svg(page).encode("utf-8"))
        self.background = image
        self.repaint_text_on_selection = False
        self.merge_line_bands = True
        self.selection_color = QColor(
            OCR_SELECTION_COLOR if selection_color is None else selection_color
        )
        self._install(prepared, OcrLayout(page), [])

    def _install(self, prepared: QByteArray, layout: OcrLayout, warnings: list[str]) -> None:
        super().load(prepared)
        self.renderer().setAspectRatioMode(Qt.IgnoreAspectRatio)
        self.layout_model = layout
        self.selection_warnings = warnings
        self.clear_selection()
        self.updateGeometry()

    def content_rect(self) -> QRectF:
        """SVG viewport in widget coordinates (aspect ratio preserved)."""
        if self.layout_model is None:
            return QRectF()
        page = self.layout_model.page
        scale = min(self.width() / page.width, self.height() / page.height)
        width, height = page.width * scale, page.height * scale
        return QRectF((self.width() - width) / 2, (self.height() - height) / 2, width, height)

    def _page_point(self, point: QPointF) -> QPointF:
        rect = self.content_rect()
        page = self.layout_model.page
        return QPointF(
            (point.x() - rect.x()) * page.width / rect.width(),
            (point.y() - rect.y()) * page.height / rect.height(),
        )

    def paintEvent(self, event) -> None:
        if self.layout_model is None:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        target = self.content_rect()
        if target.isEmpty():
            return
        if self.background is not None:
            painter.drawImage(target, self.background)
        self.renderer().render(painter, target)
        if self.selection is None:
            return
        painter.setClipRect(target)
        painter.translate(target.topLeft())
        painter.scale(
            target.width() / self.layout_model.page.width,
            target.height() / self.layout_model.page.height,
        )
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        for rect in self.selection_rects():
            path.addRect(rect)
        region = path.simplified()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.selection_color)
        painter.drawPath(region)
        if not self.repaint_text_on_selection:
            return
        # Repaint the glyphs the highlight would otherwise cover.
        painter.setClipPath(region, Qt.IntersectClip)
        self._text_renderer.render(
            painter, QRectF(0, 0, self.layout_model.page.width, self.layout_model.page.height)
        )

    def selection_rects(self) -> list[QRectF]:
        """Selected geometry: per OCR line band, or per SVG text element.

        OCR paragraphs merge each visual line into one band so that padded
        boxes do not leave striped gaps; native SVG text keeps independent
        boxes because every element is its own line.
        """
        if self.selection is None or self.layout_model is None:
            return []
        if self.merge_line_bands:
            return self.layout_model.selection_bands(self.selection)
        start, end = self.selection.normalized
        result = []
        for index in range(start.token_index, end.token_index + 1):
            chars = self.layout_model.character_rects[index]
            first = start.character_index if index == start.token_index else 0
            last = end.character_index + 1 if index == end.token_index else len(chars)
            selected = chars[first:last]
            if selected:
                rect = QRectF(selected[0])
                for character in selected[1:]:
                    rect = rect.united(character)
                result.append(rect)
        return result

    def selected_text(self) -> str:
        if self.selection is None or self.layout_model is None:
            return ""
        return self.layout_model.selected_text(self.selection)

    def _set_selection(self, selection) -> None:
        self.selection = selection
        self.selection_changed.emit(self.selected_text())
        self.update()

    def clear_selection(self) -> None:
        self._drag_start = None
        self._set_selection(None)
        self.setCursor(Qt.ArrowCursor)

    def select_all(self) -> None:
        self._drag_start = None
        if self.layout_model is not None and self.layout_model.tokens:
            last = len(self.layout_model.tokens) - 1
            self._set_selection(
                SelectionRange(
                    TextPosition(0),
                    TextPosition(last, len(self.layout_model.tokens[last].text) - 1),
                )
            )

    def copy_selection(self) -> None:
        text = self.selected_text()
        if text:
            QApplication.clipboard().setText(text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.setFocus(Qt.MouseFocusReason)
            self.clear_selection()
            if self.layout_model is not None and self.content_rect().contains(event.localPos()):
                self._drag_start = self._page_point(event.localPos())
            event.accept()
        else:
            super().mousePressEvent(event)

    def _drag_to(self, point) -> None:
        selection = None
        if self.content_rect().contains(point):
            selection = self.layout_model.selection_from_points(
                self._drag_start, self._page_point(point)
            )
        self._set_selection(selection)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_start is not None:
            self._drag_to(event.localPos())
        hit = (
            self.layout_model is not None
            and self.content_rect().contains(event.localPos())
            and self.layout_model.hit_test(self._page_point(event.localPos()), snap=False)
            is not None
        )
        self.setCursor(Qt.IBeamCursor if hit else Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._drag_start is not None:
            self._drag_to(event.localPos())
            self._drag_start = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
        elif event.matches(QKeySequence.SelectAll):
            self.select_all()
        elif event.key() == Qt.Key_Escape:
            self.clear_selection()
        else:
            super().keyPressEvent(event)
            return
        event.accept()


class SelectableSvgWindow(QMainWindow):
    """Window hosting a `SelectableSvgWidget` with copy/select-all/clear actions.

    Keyboard shortcuts stay on the widget, so they keep working while it holds
    focus; the toolbar mirrors them for discoverability and mouse-only use.
    """

    def __init__(self, widget: SelectableSvgWidget, title: str = "OCR Text Selection") -> None:
        super().__init__()
        self.widget = widget
        self.setCentralWidget(widget)
        self.setWindowTitle(title)
        toolbar = QToolBar("Selection", self)
        self.addToolBar(toolbar)
        self.copy_action = QAction("Copy", self)
        self.copy_action.triggered.connect(widget.copy_selection)
        self.select_all_action = QAction("Select All", self)
        self.select_all_action.triggered.connect(widget.select_all)
        self.clear_action = QAction("Clear", self)
        self.clear_action.triggered.connect(widget.clear_selection)
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.select_all_action)
        toolbar.addAction(self.clear_action)
        widget.selection_changed.connect(self._selection_changed)
        self._selection_changed("")
        self.resize(1000, 720)

    def _selection_changed(self, text: str) -> None:
        self.copy_action.setEnabled(bool(text))
        self.clear_action.setEnabled(bool(text))
        self.statusBar().showMessage(text.replace("\n", " ")[:160])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Native selectable SVG viewer")
    parser.add_argument("svg", type=Path)
    args = parser.parse_args(argv)
    app = QApplication.instance() or QApplication(sys.argv)
    widget = SelectableSvgWidget(args.svg)
    widget.setWindowTitle("SVG Text Selection")
    widget.resize(1000, 650)
    widget.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())