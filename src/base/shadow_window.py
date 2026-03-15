# coding=utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import *
from .mouse_through_window import *


class ShadowWindow(MouseThroughWindow):
    def __init__(self, roundRadius: int, shadowWidth: float, parent: QWidget):
        super().__init__(parent)
        self.attachParent = parent
        self.roundRadius = roundRadius
        self.shadowWidth = shadowWidth
        self.borderLineWidth = 0.5
        self.deactivedColor = QColor(125, 125, 125, 50)
        self.activedColor = QColor(255, 0, 255, 50)

        # 根据吸附的窗口大小设置阴影窗口大小
        self.margins = QMargins(
            self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth
        )
        self.setGeometry(self.attachParent.geometry() + self.margins)

        self.defaultFlag()
        self.painter = QPainter()

        self.attachParent.installEventFilter(self)
        self.setMouseThroughState(True)
        self.initBlink()
        self.show()
        self.resetRoundClip()

    def eventFilter(self, obj, event: QEvent):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(self.attachParent.geometry() + self.margins)
            self.resetRoundClip()
        elif event.type() == QEvent.Type.Move:
            self.move(
                self.attachParent.geometry().topLeft()
                - QPoint(self.shadowWidth, self.shadowWidth)
            )
        elif event.type() == QEvent.Type.WindowActivate:
            self.update()
        elif event.type() == QEvent.Type.WindowDeactivate:
            self.update()
        return super().eventFilter(obj, event)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

    def initBlink(self):
        self.blinkColors = [
            Qt.GlobalColor.red,
            Qt.GlobalColor.yellow,
            Qt.GlobalColor.green,
        ]
        self.blinkTimers = 0
        self.blinkColor = self.blinkColors[self.blinkTimers]

        self.blinkTimer = QTimer(self)
        self.blinkTimer.timeout.connect(self.onBlinkTimerTimeout)
        self.blinkTimer.start(300)

    def onBlinkTimerTimeout(self):
        if self.blinkTimers < len(self.blinkColors) - 1:
            self.blinkTimers += 1
            self.blinkColor = self.blinkColors[self.blinkTimers]
            self.update()
        else:
            self.blinkTimer.stop()
            self.blinkColor = None
            self.update()
            if self.parentWidget() != None:
                self.parentWidget().activateWindow()

    def setRoundRadius(self, value):
        self.roundRadius = value
        self.resetRoundClip()
        self.update()

    def resetRoundClip(self):
        self.applyRoundClip(self.attachParent, self.roundRadius)

    def applyRoundClip(self, targetWidget: QWidget, roundRadius):
        """裁剪窗口为圆角"""
        # 创建一个QBitmap对象，用于定义窗口的遮罩
        maskBitmap = QBitmap(targetWidget.size())
        maskBitmap.fill(Qt.GlobalColor.color0)  # 填充为黑色（透明）

        # 创建一个QPainter对象，用于绘制遮罩
        painter = QPainter(maskBitmap)
        painter.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)

        # 设置画笔和画刷
        painter.setPen(Qt.GlobalColor.color1)  # 设置画笔颜色为白色（不透明）
        painter.setBrush(Qt.GlobalColor.color1)  # 设置画刷颜色为白色（不透明）

        # 绘制圆角矩形
        rect = QRect(0, 0, targetWidget.width(), targetWidget.height())
        painter.drawRoundedRect(rect, roundRadius, roundRadius)  # 20是圆角的半径

        # 结束绘制
        painter.end()

        # 设置遮罩
        targetWidget.setMask(maskBitmap)

    def setShadowColor(self, activedColor: QColor, deactivedColor: QColor):
        self.activedColor = activedColor
        self.deactivedColor = deactivedColor
        self.update()

    def getActiveState(self) -> bool:
        return self.attachParent.getActiveState()

    def paintEvent(self, event):
        try:
            self.painter.begin(self)
            self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

            # 阴影
            path = QPainterPath()
            path.setFillRule(Qt.WindingFill)
            self.painter.fillPath(path, QBrush(Qt.white))
            if self.getActiveState():
                color = self.activedColor
            else:
                color = self.deactivedColor

            for i in range(10):
                i_path = QPainterPath()
                i_path.setFillRule(Qt.WindingFill)
                ref = QRectF(
                    self.shadowWidth - i,
                    self.shadowWidth - i,
                    self.width() - (self.shadowWidth - i) * 2,
                    self.height() - (self.shadowWidth - i) * 2,
                )
                if self.roundRadius > 0:
                    i_path.addRoundedRect(ref, self.roundRadius, self.roundRadius)
                else:
                    i_path.addRect(ref)
                color.setAlpha(int(150 - i**0.5 * 50))
                self.painter.setPen(color)
                self.painter.drawPath(i_path)

            # 绘制闪烁边框
            if self.blinkColor != None:
                blinkPen = QPen(self.blinkColor)  # 实线，浅蓝色
                blinkPen.setStyle(
                    Qt.PenStyle.SolidLine
                )  # 实线SolidLine，虚线DashLine，点线DotLine
                blinkPen.setWidthF(self.borderLineWidth)  # 0表示线宽为1
                self.painter.setPen(blinkPen)
                rect = QRect(0, 0, self.width(), self.height())
                rect = rect - self.margins
                if self.roundRadius > 0:
                    self.painter.drawRoundedRect(rect, self.roundRadius, self.roundRadius)
                else:
                    self.painter.drawRect(rect)
        except Exception:
            # 阻止绘制异常冒泡到 Qt C++ 层导致进程 abort
            pass
        finally:
            # 无论绘制逻辑是否抛异常，都必须先结束绘制
            if self.painter.isActive():
                self.painter.end()
