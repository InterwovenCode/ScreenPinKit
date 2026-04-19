"""User interface pieces of the selectable OCR text layer.

``CanvasOcrTextLayerItem`` is what the screenshot canvas uses. The standalone
SVG viewer (``SelectableSvgWidget`` / ``SelectableSvgWindow``) is imported
lazily because it needs ``PyQt5.QtSvg``, which the canvas path does not.
"""

from .canvas_item import CanvasOcrTextLayerItem

__all__ = ["CanvasOcrTextLayerItem"]


def __getattr__(name):
    if name in ("SelectableSvgWidget", "SelectableSvgWindow"):
        from . import svg_widget

        return getattr(svg_widget, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")