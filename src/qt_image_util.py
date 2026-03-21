"""Pillow-free conversion utilities for Qt images and NumPy arrays."""

import numpy as np
from PyQt5.QtGui import QImage, QPixmap


def qimage_to_ndarray(image: QImage) -> np.ndarray:
    """Return a detached RGBA NumPy copy of *image*."""
    if image.isNull():
        raise ValueError("Cannot convert a null QImage")

    rgba_image = image.convertToFormat(QImage.Format_RGBA8888)
    height = rgba_image.height()
    width = rgba_image.width()
    bytes_per_line = rgba_image.bytesPerLine()
    buffer = rgba_image.bits()
    buffer.setsize(bytes_per_line * height)
    rows = np.frombuffer(buffer, dtype=np.uint8).reshape(height, bytes_per_line)
    return rows[:, : width * 4].reshape(height, width, 4).copy()


def qpixmap_to_ndarray(pixmap: QPixmap) -> np.ndarray:
    """Return a detached RGBA NumPy copy of *pixmap*."""
    if pixmap.isNull():
        raise ValueError("Cannot convert a null QPixmap")
    return qimage_to_ndarray(pixmap.toImage())


def qpixmap_to_bgr_ndarray(pixmap: QPixmap) -> np.ndarray:
    """Return a detached three-channel BGR array for OpenCV OCR models."""
    rgba = qpixmap_to_ndarray(pixmap)
    return rgba[:, :, :3][:, :, ::-1].copy()


def ndarray_to_qimage(array: np.ndarray) -> QImage:
    """Convert an RGB or RGBA uint8 NumPy array into an owning QImage."""
    if array.dtype != np.uint8 or array.ndim != 3 or array.shape[2] not in (3, 4):
        raise ValueError("Expected a uint8 NumPy array with RGB or RGBA channels")

    image = np.ascontiguousarray(array)
    height, width, channels = image.shape
    image_format = QImage.Format_RGB888 if channels == 3 else QImage.Format_RGBA8888
    return QImage(image.data, width, height, image.strides[0], image_format).copy()


def ndarray_to_qpixmap(array: np.ndarray, device_pixel_ratio: float = 1.0) -> QPixmap:
    """Convert an RGB or RGBA array into a QPixmap with its scale preserved."""
    pixmap = QPixmap.fromImage(ndarray_to_qimage(array))
    pixmap.setDevicePixelRatio(device_pixel_ratio)
    return pixmap