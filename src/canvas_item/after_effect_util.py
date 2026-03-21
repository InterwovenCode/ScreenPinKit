# coding=utf-8
from enum import Enum
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np
from qt_image_util import ndarray_to_qpixmap, qpixmap_to_ndarray


class AfterEffectType(Enum):
    """
    图像后处理效果类型
    """

    Unknown = "Unknown"
    Blur = "Blur"
    Mosaic = "Mosaic"
    Detail = "Detail"
    Find_Edges = "Find_Edges"
    Contour = "Contour"
    Invert = "Invert"
    Darken = "Darken"


class AfterEffectUtilByPIL:
    """
    基于PIL实现的图像后处理效果
    """

    @staticmethod
    def gaussianBlur(pixmap: QPixmap, blurRadius=5):
        """高斯模糊"""
        image = qpixmap_to_ndarray(pixmap)
        kernel_size = max(3, int(blurRadius) * 2 + 1)
        result = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        result[:, :, 3] = image[:, :, 3]
        return ndarray_to_qpixmap(result, pixmap.devicePixelRatioF())

    @staticmethod
    def mosaic(pixmap: QPixmap, blockSize=2, pixelateFactor=1):
        """
        马赛克效果
        由于那种逐个像素遍历的处理太低效了，最终采取了网友分享的思路：
        https://blog.csdn.net/qq_38563206/article/details/136030277
        """
        if blockSize <= 0 or pixelateFactor <= 0:
            raise ValueError("blockSize and pixelateFactor must be positive")

        image = qpixmap_to_ndarray(pixmap)
        height, width = image.shape[:2]
        reduced_size = (max(width // blockSize, 1), max(height // blockSize, 1))
        reduced = cv2.resize(image, reduced_size, interpolation=cv2.INTER_LINEAR)
        pixelated_size = (
            max(width // pixelateFactor, 1),
            max(height // pixelateFactor, 1),
        )
        pixelated = cv2.resize(reduced, pixelated_size, interpolation=cv2.INTER_NEAREST)
        result = cv2.resize(pixelated, (width, height), interpolation=cv2.INTER_NEAREST)
        result[:, :, 3] = image[:, :, 3]
        return ndarray_to_qpixmap(result, pixmap.devicePixelRatioF())

    @staticmethod
    def detail(pixmap: QPixmap):
        """图像突出"""
        return AfterEffectUtilByPIL._apply_cv_effect(pixmap, "detail")

    @staticmethod
    def findEdges(pixmap: QPixmap):
        """边缘提取"""
        return AfterEffectUtilByPIL._apply_cv_effect(pixmap, "edges")

    @staticmethod
    def contour(pixmap: QPixmap):
        """轮廓提取"""
        return AfterEffectUtilByPIL._apply_cv_effect(pixmap, "contour")

    @staticmethod
    def invert(pixmap: QPixmap):
        """反色"""
        img:QImage = pixmap.toImage()
        img.invertPixels()
        return QPixmap.fromImage(img)

    @staticmethod
    def darken(pixmap: QPixmap, factor=0.5):
        """变暗"""
        result = QPixmap(pixmap.size())
        result.setDevicePixelRatio(pixmap.devicePixelRatio())
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.drawPixmap(0, 0, pixmap)

        brush = QBrush(QColor(0, 0, 0, int(255 * (1 - factor))))
        painter.fillRect(pixmap.rect(), brush)
        painter.end()
        return result

    # @staticmethod
    # def mosaic2(pixmap:QPixmap, blockSize = 16):
    #     '''马赛克效果(效率太低，废弃)'''
    #     width = pixmap.width()
    #     height = pixmap.height()
    #     tempImage = pixmap.toImage()
    #     if tempImage.format() != QImage.Format.Format_RGB32:
    #         tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

    # Pillow-based mosaic implementation was removed.

    #     # finalImage = image.copy()
    #     finalImage = Image.new("RGB", (width, height), (0, 0, 0))
    #     # 在新的图片上绘制马赛克块
    #     draw = ImageDraw.Draw(finalImage)
    #     # 循环遍历图片中的每个块
    #     for x in range(0, width, blockSize):
    #         for y in range(0, height, blockSize):
    #             # 截取当前块的区域
    #             box = (x, y, x+blockSize, y+blockSize)
    #             block = image.crop(box)
    #             # 计算当前块的平均颜色
    #             r, g, b = block.resize((1, 1)).getpixel((0, 0))
    #             color = (r, g, b)
    #             draw.rectangle(box, fill=color)

    #     return QPixmap.fromImage(QImage(finalImage.tobytes(), width, height, 3*width, QImage.Format.Format_RGB888))

    @staticmethod
    def _apply_cv_effect(pixmap: QPixmap, effect: str):
        image = qpixmap_to_ndarray(pixmap)
        rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        if effect == "detail":
            result = cv2.detailEnhance(rgb)
        elif effect == "edges":
            edges = cv2.Canny(rgb, 100, 200)
            result = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        elif effect == "contour":
            result = cv2.filter2D(rgb, -1, np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]))
        else:
            raise ValueError(f"Unsupported effect: {effect}")
        rgba = np.dstack((result, image[:, :, 3]))
        return ndarray_to_qpixmap(rgba, pixmap.devicePixelRatioF())

    @staticmethod
    def effectDemos(pixmap: QPixmap):
        # 图像模糊
        # return ImageEffectUtil.effectUtilByPIL(pixmap, ImageFilter.BLUR)

        # 图像突出
        # return ImageEffectUtil.effectUtilByPIL(pixmap, ImageFilter.DETAIL)

        # 边缘提取
        # return ImageEffectUtil.effectUtilByPIL(pixmap, ImageFilter.FIND_EDGES)

        # 轮廓提取
        return AfterEffectUtilByPIL._apply_cv_effect(pixmap, "contour")


# class AfterEffectUtilByCv:
#     '''
#     基于OpenCv实现的图像后处理效果，依赖重遂放弃
#     '''
#     @staticmethod
#     def gaussianBlur(pixmap:QPixmap, blurRadius=5):
#         return AfterEffectUtilByCv.gaussianBlurEffectByCv(pixmap, blurRadius)

#     def mosaic(pixmap:QPixmap, blockSize=3):
#         return AfterEffectUtilByCv.mosaicEffectByCv(pixmap, blockSize)

#     @staticmethod
#     def _mosaicEffectByCv(ndArray:np.ndarray, x, y, w, h, neighbor=2):
#         import cv2
#         fh, fw = ndArray.shape[0], ndArray.shape[1]
#         if (y + h > fh) or (x + w > fw):
#             return
#         for i in range(0, h - neighbor, neighbor):  # 关键点0 减去neightbour 防止溢出
#             for j in range(0, w - neighbor, neighbor):
#                 rect = [j + x, i + y, neighbor, neighbor]
#                 color = ndArray[i + y][j + x].tolist()  # 关键点1 tolist
#                 left_up = (rect[0], rect[1])
#                 right_down = (rect[0] + neighbor - 1, rect[1] + neighbor - 1)  # 关键点2 减去一个像素
#                 cv2.rectangle(ndArray, left_up, right_down, color, -1)

#     @staticmethod
#     def mosaicEffectByCv(pixmap:QPixmap, blockSize = 3):
#         '''马赛克效果'''
#         tempImage = pixmap.toImage()
#         if tempImage.format() != QImage.Format.Format_RGB32:
#             tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

#         image = qpixmap_to_ndarray(tempImage)
#         width, height = pixmap.width(), pixmap.height()
#         ndArray = np.array(image)

#         AfterEffectUtilByCv._mosaicEffectByCv(ndArray, 0, 0, width, height, blockSize)

#         return QPixmap.fromImage(QImage(ndArray, width, height, 3*width, QImage.Format.Format_RGB888))

#     @staticmethod
#     def gaussianBlurEffectByCv(pixmap:QPixmap, blurRadius=5):
#         import cv2
#         '''高斯模糊效果'''
#         tempImage = pixmap.toImage()
#         if tempImage.format() != QImage.Format.Format_RGB32:
#             tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

#         image = qpixmap_to_ndarray(tempImage)
#         width, height = pixmap.width(), pixmap.height()
#         ndArray = np.array(image)

#         blurred = cv2.GaussianBlur(ndArray, (blurRadius, blurRadius), 0)
#         return QPixmap.fromImage(QImage(blurred.data, width, height, 3*width, QImage.Format.Format_RGB888))


class EffectWorker(QThread):
    """图像后处理线程"""

    effectFinishedSignal = pyqtSignal(QPixmap)
    isRunning = 0

    def __init__(self) -> None:
        super().__init__()
        self.setStackSize(1024 * 1024)

    def startEffect(
        self, effectType: AfterEffectType, sourcePixmap: QPixmap, value: int, minValue:int, maxValue:int
    ):
        if self.isRunning:
            return
        self.effectType = effectType
        self.sourcePixmap = sourcePixmap
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue
        self.start()

    def run(self):
        self.isRunning = 1
        try:
            if self.effectType == AfterEffectType.Blur:
                finalPixmap = AfterEffectUtilByPIL.gaussianBlur(
                    self.sourcePixmap, self.value
                )
            elif self.effectType == AfterEffectType.Mosaic:
                finalPixmap = AfterEffectUtilByPIL.mosaic(
                    self.sourcePixmap, 5, self.value
                )
            elif self.effectType == AfterEffectType.Darken:
                factor = (self.maxValue - self.value)/(self.maxValue - self.minValue)
                finalPixmap = AfterEffectUtilByPIL.darken(self.sourcePixmap, factor)
            elif self.effectType == AfterEffectType.Detail:
                finalPixmap = AfterEffectUtilByPIL.detail(self.sourcePixmap)
            elif self.effectType == AfterEffectType.Find_Edges:
                finalPixmap = AfterEffectUtilByPIL.findEdges(self.sourcePixmap)
            elif self.effectType == AfterEffectType.Contour:
                finalPixmap = AfterEffectUtilByPIL.contour(self.sourcePixmap)
            elif self.effectType == AfterEffectType.Invert:
                finalPixmap = AfterEffectUtilByPIL.invert(self.sourcePixmap)
            else:
                pass
            self.effectFinishedSignal.emit(finalPixmap)
            self.isRunning = 0
        except Exception as e:
            print(e)
            self.isRunning = 0
            raise