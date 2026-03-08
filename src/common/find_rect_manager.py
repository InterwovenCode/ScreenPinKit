# coding:utf-8
# 提取自https://github.com/fandesfyf/Jamscreenshot/blob/master/jamscreenshot.py
import typing
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image
import numpy as np
from canvas_item.canvas_util import CanvasUtil


class FindRectManager:
    def __init__(self):
        super().__init__()
        finalPixmap, finalGeometry = CanvasUtil.grabScreens()
        self.pixmap = finalPixmap
        self.devicePixelRatio = self.pixmap.devicePixelRatioF()
        self.image = Image.fromqpixmap(self.pixmap)
        self.minSize = QSize(30, 20)
        self.screenRect = finalGeometry
        self.area_threshold = 200
        self.rects = self.getRectsByCv()

    def getRectsByCv(self):
        import cv2

        ndArray = np.array(self.image)
        gray = cv2.cvtColor(ndArray, cv2.COLOR_BGR2GRAY)
        th = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 2
        )  # 自动阈值
        self.contours = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]

        result = []
        for i in self.contours:
            x, y, w, h = cv2.boundingRect(i)
            area = cv2.contourArea(i)
            if (
                area > self.area_threshold
                and w > self.minSize.width()
                and h > self.minSize.height()
            ):
                result.append(
                    QRect(
                        qRound(x / self.devicePixelRatio),
                        qRound(y / self.devicePixelRatio),
                        qRound(w / self.devicePixelRatio),
                        qRound(h / self.devicePixelRatio),
                    )
                )

        result.append(self.screenRect)
        return result

    def findTargetRect(self, mousePos: typing.Union[QPointF, QPoint]):
        if isinstance(mousePos, QPointF):
            mousePos = mousePos.toPoint()
        for rect0 in self.rects:
            rect: QRect = rect0
            if rect.contains(mousePos):
                return rect0

        return QRect()
