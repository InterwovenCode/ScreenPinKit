# coding=utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget
from canvas_item import *
from canvas_item.canvas_util import CanvasUtil
from base import *

class ScreenShotView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initStyle()

    def initStyle(self):
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border:0px;")
        self.setRenderHint(QPainter.Antialiasing)

class ScreenShotScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sceneRectChanged.connect(self.onSceneRectChanged)
        self.maskLayer = None
        self.pathItem = None
        self.lastAddItem = None

    def reset(self):
        if self.lastAddItem != None:
            self.clear()
            self.lastAddItem = None
            self.maskLayer = None
            self.onSceneRectChanged(QRectF())

    def isCapturing(self):
        return self.lastAddItem != None

    def onSceneRectChanged(self, _rect:QRectF):
        rect = self.sceneRect()
        if self.maskLayer == None:
            self.maskLayer = CanvasMaskItem(QColor(0, 0, 0, 64))
            self.addItem(self.maskLayer)
        self.maskLayer.setRect(rect)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self.pathItem != None:
            targetPos = event.scenePos()
            self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
            self.pathItem.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        item = None
        itemList = self.items(event.scenePos())
        if len(itemList) > 0:
            item = itemList[0]

        isSkip = False
        if item == self.lastAddItem and item != None:
            isSkip = True
        if item != None and CanvasUtil.isRoiItem(item):
            isSkip = True
        if self.lastAddItem != None:
            isSkip = True

        if isSkip:
            if event.button() == Qt.MouseButton.RightButton:
                self.cancelScreenShot()
            return super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            targetPos = event.scenePos()
            if self.pathItem == None:
                self.pathItem = CanvasPasteImageItem(bgBrush=self.backgroundBrush())
                self.pathItem.setEditableState(True)
                self.addItem(self.pathItem)
                self.pathItem.polygon.append(targetPos)
                self.pathItem.polygon.append(targetPos)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if self.pathItem != None:
            if event.button() == Qt.RightButton:
                self.removeItem(self.pathItem)
                self.pathItem = None
            elif event.button() == Qt.LeftButton:
                if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                    self.removeItem(self.pathItem)
                else:
                    self.pathItem.completeDraw()
                    self.pathItem.setFocus(Qt.FocusReason.OtherFocusReason)
                    self.lastAddItem = self.pathItem
                self.pathItem = None
        super().mouseReleaseEvent(event)

    def cancelScreenShot(self):
        if self.lastAddItem != None:  # 清空已划定的的截图区域
            self.reset()
        else:
            self.close()

class ScreenShotWindow(QWidget):
    snipedSignal = pyqtSignal(QPoint, QPixmap)
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()
        self.painter = QPainter()
        self.snipedSignal.connect(self.onSnip)

    def onSnip(self, point:QPoint, pixmap:QPixmap):
        print(f"======> {point} / {pixmap.size()}")

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def initUI(self):
        self.scene = ScreenShotScene()
        self.view = ScreenShotView(self.scene)
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.addWidget(self.view)

    def initActions(self):
        actions = [
            QAction(parent=self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            QAction(parent=self, triggered=self.snip, shortcut="ctrl+t"),
            QAction(parent=self, triggered=self.cancelScreenShot, shortcut="esc"),
        ]
        self.addActions(actions)

    def toPhysicalRectF(self, rectf:QRectF):
        '''计算划定的截图区域的（缩放倍率1.0的）原始矩形（会变大）
        rectf：划定的截图区域的矩形。可为QRect或QRectF'''
        pixelRatio = self.screenPixmap.devicePixelRatio()
        return QRectF(rectf.x() * pixelRatio, rectf.y() * pixelRatio,
                      rectf.width() * pixelRatio, rectf.height() * pixelRatio)

    def copyToClipboard(self):
        if not self.scene.isCapturing():
            return
        cropRect = self.toPhysicalRectF(self.scene.lastAddItem.sceneBoundingRect()).toRect()
        cropPixmap = self.screenPixmap.copy(cropRect)
        QApplication.clipboard().setPixmap(cropPixmap)
        self.close()

    def snip(self):
        if not self.scene.isCapturing():
            return
        rect = self.scene.lastAddItem.sceneBoundingRect()
        cropRect = self.toPhysicalRectF(rect).toRect()
        cropPixmap = self.screenPixmap.copy(cropRect)
        screenPoint = self.mapToGlobal(rect.topLeft().toPoint())
        self.snipedSignal.emit(screenPoint, cropPixmap)

    def cancelScreenShot(self):
        if self.scene.isCapturing():
            self.scene.cancelScreenShot()
        else:
            self.close()

    def reShow(self):
        if self.isActiveWindow():
            return
        finalPixmap, finalGeometry = CanvasUtil.grabScreens()
        self.screenPixmap = finalPixmap
        self.setGeometry(finalGeometry)
        rect = QRectF(0, 0, finalGeometry.width(), finalGeometry.height())
        self.scene.setSceneRect(rect)
        sceneBrush = QBrush(self.screenPixmap.copy())
        transform = QtGui.QTransform()
        transform.scale(1/finalPixmap.devicePixelRatioF(), 1/finalPixmap.devicePixelRatioF())
        sceneBrush.setTransform(transform)
        self.scene.setBackgroundBrush(sceneBrush)
        self.scene.reset()
        self.show()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.close()