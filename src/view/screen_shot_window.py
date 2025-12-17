# coding=utf-8
from canvas_item import *
from common import *
from misc import *


class ScreenShotWindow(QWidget):
    snipedSignal = pyqtSignal(QRectF, QPixmap)
    closedSignal = pyqtSignal()

    Unknown = 0
    TopLeft = 1
    TopMid = 2
    TopRight = 3
    LeftMid = 4
    RightMid = 5
    BottomLeft = 6
    BottomMid = 7
    BottomRight = 8
    Center = 9

    def __init__(self):
        super().__init__()
        self.defaultFlag()

        self.mousePos: QPointF = QCursor.pos()
        self.previewRect = QRect()
        self._mouseHitType = ScreenShotWindow.Unknown
        self.showColorMode = 0  # 0：Hex 1：RGB 2：HSV
        self._pt_start = QPointF()  # 划定截图区域时鼠标左键按下的位置（topLeft）
        self._pt_end = QPointF()  # 划定截图区域时鼠标左键松开的位置（bottomRight）
        self._pixelFactor = 20
        self.initPainterTool()
        self.initActions()
        self.initFindRectManager()
        # self.setWindowOpacity(0.5)

    def initActions(self):
        actions = [
            QAction(parent=self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            QAction(parent=self, triggered=self.snip, shortcut="ctrl+t"),
            QAction(parent=self, triggered=self.cancelScreenShot, shortcut="esc"),
            QAction(parent=self, triggered=self.pickUpScreenColor, shortcut="c"),
        ]
        self.addActions(actions)

    def initFindRectManager(self):
        self.findRectMgr = FindRectManager()

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

    def copyToClipboard(self):
        cropRect = self.normalizeRectF(self._pt_start, self._pt_end)
        if cropRect.size() == QSizeF(0, 0) and cfg.get(cfg.isAutoFindWindow):
            cropRect = QRectF(self.previewRect)
        self.clearScreenShot(False)
        self.close()
        if cropRect.size() != QSize(0, 0):
            self.snipedSignal.emit(cropRect, QPixmap())

    def snip(self):
        cropRect = self.normalizeRectF(self._pt_start, self._pt_end)
        if not self.hasScreenShot:
            if cfg.get(cfg.isAutoFindWindow):
                cropRect = QRectF(self.previewRect)
        realCropRect = self.physicalRectF(cropRect, False).toRect()
        if realCropRect.size() != QSize(0, 0):
            cropPixmap = self.screenPixmap.copy(realCropRect)
            screenPoint = self.mapToGlobal(cropRect.topLeft().toPoint())
            cropRect.moveTo(screenPoint)
            cropImage = cropPixmap.toImage().convertToFormat(
                QImage.Format.Format_RGB888
            )
            cropPixmap = QPixmap.fromImage(cropImage)
            self.snipedSignal.emit(cropRect, cropPixmap)
            self.clearScreenShot(False)
            self.close()

    def initPainterTool(self):
        self.painter = QPainter()
        self.color_transparent = Qt.GlobalColor.transparent
        self.color_black = QColor(0, 0, 0, 150)  # 黑色背景
        self.color_lightBlue = QColor(
            30, 120, 255, 255
        )  # 浅蓝色。深蓝色Qt.GlobalColor.blue
        self.color_lightWhite = QColor(
            255, 255, 255, 255
        )  # 浅蓝色。深蓝色Qt.GlobalColor.blue
        self.font_normal = QtGui.QFont("Times New Roman", 11, QtGui.QFont.Weight.Normal)
        self.font_textInput = QtGui.QFont(
            "微软雅黑", 16, QtGui.QFont.Weight.Normal
        )  # 工具条文字工具默认字体
        self.pen_transparent = QPen(Qt.PenStyle.NoPen)  # 没有笔迹，画不出线条
        self.pen_white = QPen(Qt.GlobalColor.white)
        self.pen_SolidLine_lightBlue = QPen(self.color_lightBlue)  # 实线，浅蓝色
        self.pen_SolidLine_lightBlue.setStyle(
            Qt.PenStyle.SolidLine
        )  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_SolidLine_lightBlue.setWidthF(4)  # 0表示线宽为1
        self.pen_SolidLine_lightWhite = QPen(self.color_lightWhite)  # 实线，浅蓝色
        self.pen_SolidLine_lightWhite.setStyle(
            Qt.PenStyle.SolidLine
        )  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_SolidLine_lightWhite.setWidthF(2)  # 0表示线宽为1

    def clearScreenShot(self, isGotoScreeShot=True):
        self.screenColor = None
        self.hasScreenShot = False  # 是否已通过拖动鼠标左键划定截图区域
        self.isCapturing = False  # 正在拖动鼠标左键选定截图区域时
        self.isMoving = False  # 在截图区域内拖动时
        self.isAdjusting = False  # 在截图区域的边框按住鼠标左键调整大小时
        pos = QPointF()
        self.setCenterArea(pos, pos)
        self.update()
        if isGotoScreeShot:
            self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def expandScreenShotArea(self, pos):
        """根据所处的非截图区域的朝向，拓展已划定的截取区域"""
        finalPolygon = QPolygonF(self.normalizeRectF(self._pt_start, self._pt_end))
        finalPolygon.append(pos)
        finalRect = finalPolygon.boundingRect()
        self.setCenterArea(finalRect.topLeft(), finalRect.bottomRight())
        self.update()

    def reShow(self):
        if self.isActiveWindow():
            return
        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        self.screenPixmap = finalPixmap
        self.setGeometry(finalGeometry)
        self.clearScreenShot()
        self.show()
        self.activateWindow()

    def normalizeRectF(self, topLeftPoint, bottomRightPoint):
        return QRectF(topLeftPoint, bottomRightPoint).normalized()

    def paintMagnifyingGlassPixmap(self, pos, glassSize):
        """绘制放大镜内的图像(含纵横十字线)
        pos:鼠标光标位置
        glassSize:放大镜边框大小"""
        pixmapRect = QRect(
            0, 0, self._pixelFactor, self._pixelFactor
        )  # 以鼠标光标为中心的正方形区域，最好是偶数
        pixmapRect.moveCenter(pos)
        glassPixmap = self.screenPixmap.copy(self.physicalRectF(pixmapRect).toRect())
        glassPixmap.setDevicePixelRatio(1.0)
        glassPixmap = glassPixmap.scaled(
            glassSize, glassSize, Qt.AspectRatioMode.KeepAspectRatio
        )
        screenColor = glassPixmap.toImage().pixelColor(glassPixmap.rect().center())
        # 在放大后的QPixmap上画纵横十字线
        if not hasattr(self, "_painter"):
            self._painter = QPainter()
        self._painter.begin(glassPixmap)
        halfWidth = glassPixmap.width() / 2
        halfHeight = glassPixmap.height() / 2
        self._painter.setPen(self.pen_SolidLine_lightBlue)
        self._painter.drawLine(
            QPointF(0, halfHeight), QPointF(glassPixmap.width(), halfHeight)
        )
        self._painter.drawLine(
            QPointF(halfWidth, 0), QPointF(halfWidth, glassPixmap.height())
        )
        self._painter.end()
        return glassPixmap, screenColor

    def paintMagnifyingGlass(self, glassSize=150, offset=30, labelHeight=60):
        if self.hasScreenShot or self.isCapturing:
            return
        screenSizeF = QSizeF(
            self.screenPixmap.width() / self.screenPixmap.devicePixelRatioF(),
            self.screenPixmap.height() / self.screenPixmap.devicePixelRatioF(),
        )
        pos = self.mousePos
        glassPixmap, screenColor = self.paintMagnifyingGlassPixmap(
            pos, glassSize
        )  # 画好纵横十字线后的放大镜内QPixmap
        self.screenColor = screenColor
        # 限制放大镜显示不超出屏幕外
        glassRect = glassPixmap.rect()
        if (pos.x() + glassSize + offset) < screenSizeF.width():
            if (pos.y() + offset + glassSize + labelHeight) < screenSizeF.height():
                glassRect.moveTo(pos + QPoint(offset, offset))
            else:
                glassRect.moveBottomLeft(pos + QPoint(offset, -offset))
        else:
            if (pos.y() + offset + glassSize + labelHeight) < screenSizeF.height():
                glassRect.moveTopRight(pos + QPoint(-offset, offset))
            else:
                glassRect.moveBottomRight(pos + QPoint(-offset, -offset))
        self.painter.drawPixmap(glassRect.topLeft(), glassPixmap)
        tempRect = QRectF(QPointF(0, 0), pos)
        physicalPoint = self.physicalRectF(tempRect, False).toRect().bottomRight()
        labelRectF = QRectF(
            glassRect.bottomLeft().x(),
            glassRect.bottomLeft().y(),
            glassSize,
            labelHeight,
        )
        finalFrame = QRegion()
        finalFrame.setRects([glassRect, labelRectF.toRect()])
        self.painter.setPen(self.pen_transparent)
        self.painter.fillRect(labelRectF, self.color_black)
        self.painter.setPen(self.pen_white)
        self.painter.setFont(self.font_normal)
        labelRectF = labelRectF - QMarginsF(12, 10, 12, 10)
        self.painter.drawText(
            labelRectF,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            f"({physicalPoint.x()}, {physicalPoint.y()})",
        )

        self.painter.drawText(
            labelRectF,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            self.getScreenColorStr(),
        )

        labelRectF = labelRectF + QMarginsF(0, 5, 0, 5)
        self.painter.setBrush(Qt.NoBrush)
        self.painter.setPen(QPen(screenColor, 3))
        self.painter.drawRect(labelRectF)

        self.painter.setPen(QPen(self.color_black, 2, Qt.SolidLine))
        self.painter.drawRect(finalFrame.boundingRect() + QMargins(1, 1, 1, 1))

    def getScreenColorStr(self):
        return OsHelper.getColorStrByQColor(self.screenColor, self.showColorMode)

    def paintCenterArea(self):
        (
            rt_center,
            pt_centerTopMid,
            pt_centerBottomMid,
            pt_centerLeftMid,
            pt_centerRightMid,
        ) = self.getCenterInfos()

        # 绘制已选定的截图区域
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # 1.绘制矩形线框
        self.painter.setPen(self.pen_SolidLine_lightBlue)
        self.painter.setBrush(self.color_transparent)
        self.painter.drawRect(rt_center)

        # 2.绘制矩形线框4个端点和4条边框的中间点
        if rt_center.width() >= 100 and rt_center.height() >= 100:
            # 选区操作点
            points = [
                rt_center.topLeft(),
                rt_center.topRight(),
                rt_center.bottomLeft(),
                rt_center.bottomRight(),
                pt_centerLeftMid,
                pt_centerRightMid,
                pt_centerTopMid,
                pt_centerBottomMid,
            ]
            blueDotRadius = QPointF(5, 5)  # 椭圆蓝点
            self.painter.setPen(self.pen_SolidLine_lightWhite)
            self.painter.setBrush(self.color_lightBlue)
            for point in points:
                self.painter.drawEllipse(
                    QRectF(point - blueDotRadius, point + blueDotRadius)
                )

        # 显示截图区域宽高
        if rt_center.topLeft().y() > 20:
            labelPos = rt_center.topLeft() + QPointF(5, -5)
        else:
            labelPos = rt_center.topLeft() + QPointF(5, 15)
        self.painter.setPen(self.pen_white)
        self.painter.setFont(self.font_normal)
        physicalCenterRect = self.physicalRectF(rt_center).toRect()
        self.painter.drawText(
            labelPos, f"{physicalCenterRect.width()} x {physicalCenterRect.height()}"
        )

    def setCenterArea(self, start, end):
        self._pt_start = start
        self._pt_end = end

    def squareAreaByCenter(self, pointf):
        """以QPointF为中心的正方形QRectF"""
        rectf = QRectF(0, 0, 15, 15)
        rectf.moveCenter(pointf)
        return rectf

    def squareAreaByHorizontal(self, pointf, width):
        """以QPointF为中心的矩形QRectF"""
        rectf = QRectF(0, 0, width, 15)
        rectf.moveCenter(pointf)
        return rectf

    def squareAreaByVertical(self, pointf, height):
        """以QPointF为中心的矩形QRectF"""
        rectf = QRectF(0, 0, 15, height)
        rectf.moveCenter(pointf)
        return rectf

    def setBeginDragPoint(self, pointf):
        """计算开始拖拽位置距离截图区域左上角的向量"""
        rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        self._drag_vector = pointf - rt_center.topLeft()

    def getNewPosAfterDrag(self, pointf):
        """计算拖拽后截图区域左上角的新位置"""
        return pointf - self._drag_vector

    def moveCenterAreaTo(self, pointf):
        """限制拖拽不能超出屏幕范围"""
        rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        rt_center.moveTo(self.getNewPosAfterDrag(pointf))
        startPointF = rt_center.topLeft()
        if startPointF.x() < 0:
            rt_center.moveTo(0, startPointF.y())
            startPointF = rt_center.topLeft()
        if startPointF.y() < 0:
            rt_center.moveTo(startPointF.x(), 0)
        endPointF = rt_center.bottomRight()
        if endPointF.x() > self.rect().width():
            rt_center.moveBottomRight(QPointF(self.rect().width(), endPointF.y()))
            endPointF = rt_center.bottomRight()
        if endPointF.y() > self.rect().height():
            rt_center.moveBottomRight(QPointF(endPointF.x(), self.rect().height()))
        self.setCenterArea(rt_center.topLeft(), rt_center.bottomRight())

    def setBeginAdjustPoint(self, pointf):
        """判断开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），用于判断调整大小的意图方向"""
        self._mouseHitType = self.getMousePosBy(pointf, self._pt_start, self._pt_end)

    def getMousePosBy(self, pointf: QPointF, pt_start: QPointF, pt_end: QPointF):
        (
            rt_center,
            square_topLeft,
            square_topRight,
            square_bottomLeft,
            square_bottomRight,
            square_topMid,
            square_bottomMid,
            square_leftMid,
            square_rightMid,
        ) = self.getSquareInfos()

        if square_topLeft.contains(pointf):
            return ScreenShotWindow.TopLeft
        elif square_topMid.contains(pointf):
            return ScreenShotWindow.TopMid
        elif square_topRight.contains(pointf):
            return ScreenShotWindow.TopRight
        elif square_leftMid.contains(pointf):
            return ScreenShotWindow.LeftMid
        elif square_rightMid.contains(pointf):
            return ScreenShotWindow.RightMid
        elif square_bottomLeft.contains(pointf):
            return ScreenShotWindow.BottomLeft
        elif square_bottomMid.contains(pointf):
            return ScreenShotWindow.BottomMid
        elif square_bottomRight.contains(pointf):
            return ScreenShotWindow.BottomRight
        elif rt_center.contains(pointf):
            return ScreenShotWindow.Center
        else:
            return ScreenShotWindow.Unknown

    def adjustCenterAreaBy(self, pointf):
        """根据开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），判断调整大小的意图方向，判定新的开始、结束位置"""
        rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        startPointF = rt_center.topLeft()
        endPointF = rt_center.bottomRight()
        if self._mouseHitType == ScreenShotWindow.TopLeft:
            startPointF = pointf
        elif self._mouseHitType == ScreenShotWindow.TopMid:
            startPointF.setY(pointf.y())
        elif self._mouseHitType == ScreenShotWindow.TopRight:
            startPointF.setY(pointf.y())
            endPointF.setX(pointf.x())
        elif self._mouseHitType == ScreenShotWindow.LeftMid:
            startPointF.setX(pointf.x())
        elif self._mouseHitType == ScreenShotWindow.RightMid:
            endPointF.setX(pointf.x())
        elif self._mouseHitType == ScreenShotWindow.BottomLeft:
            startPointF.setX(pointf.x())
            endPointF.setY(pointf.y())
        elif self._mouseHitType == ScreenShotWindow.BottomMid:
            endPointF.setY(pointf.y())
        elif self._mouseHitType == ScreenShotWindow.BottomRight:
            endPointF = pointf
        else:  # 'ScreenShotWindow.Unknown'
            return
        self.setCenterArea(startPointF, endPointF)

    def getCenterInfos(self):
        if cfg.get(cfg.isAutoFindWindow) and self._pt_start == self._pt_end:
            rt_center = QRectF(self.previewRect)
        else:
            rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        # 中央区域上下左右边框的中点，用于调整大小
        pt_centerTopMid = (rt_center.topLeft() + rt_center.topRight()) / 2
        pt_centerBottomMid = (rt_center.bottomLeft() + rt_center.bottomRight()) / 2
        pt_centerLeftMid = (rt_center.topLeft() + rt_center.bottomLeft()) / 2
        pt_centerRightMid = (rt_center.topRight() + rt_center.bottomRight()) / 2
        return (
            rt_center,
            pt_centerTopMid,
            pt_centerBottomMid,
            pt_centerLeftMid,
            pt_centerRightMid,
        )

    def getSquareInfos(self):
        (
            rt_center,
            pt_centerTopMid,
            pt_centerBottomMid,
            pt_centerLeftMid,
            pt_centerRightMid,
        ) = self.getCenterInfos()

        # 以截图区域左上、上中、右上、左中、右中、左下、下中、右下为中心的正方形区域，用于调整大小
        square_topLeft = self.squareAreaByCenter(rt_center.topLeft())
        square_topRight = self.squareAreaByCenter(rt_center.topRight())
        square_bottomLeft = self.squareAreaByCenter(rt_center.bottomLeft())
        square_bottomRight = self.squareAreaByCenter(rt_center.bottomRight())

        # 挪到四侧边缘操作检测区域，而不是采用边缘中心点的方式
        square_topMid = self.squareAreaByHorizontal(pt_centerTopMid, rt_center.width())
        square_bottomMid = self.squareAreaByHorizontal(
            pt_centerBottomMid, rt_center.width()
        )
        square_leftMid = self.squareAreaByVertical(pt_centerLeftMid, rt_center.height())
        square_rightMid = self.squareAreaByVertical(
            pt_centerRightMid, rt_center.height()
        )

        return (
            rt_center,
            square_topLeft,
            square_topRight,
            square_bottomLeft,
            square_bottomRight,
            square_topMid,
            square_bottomMid,
            square_leftMid,
            square_rightMid,
        )

    def getMouseShapeBy(self, pointf):
        (
            rt_center,
            square_topLeft,
            square_topRight,
            square_bottomLeft,
            square_bottomRight,
            square_topMid,
            square_bottomMid,
            square_leftMid,
            square_rightMid,
        ) = self.getSquareInfos()

        """根据鼠标位置返回对应的鼠标样式"""
        if rt_center.contains(pointf):
            return Qt.CursorShape.SizeAllCursor  # 十字有箭头
        elif square_topLeft.contains(pointf) or square_bottomRight.contains(pointf):
            return Qt.CursorShape.SizeFDiagCursor  # ↖↘
        elif square_topMid.contains(pointf) or square_bottomMid.contains(pointf):
            return Qt.CursorShape.SizeVerCursor  # ↑↓
        elif square_topRight.contains(pointf) or square_bottomLeft.contains(pointf):
            return Qt.CursorShape.SizeBDiagCursor  # ↙↗
        elif square_leftMid.contains(pointf) or square_rightMid.contains(pointf):
            return Qt.CursorShape.SizeHorCursor  # ←→
        else:
            return Qt.CursorShape.CrossCursor  # 十字无箭头

    def isMousePosInCenterRectF(self, pointf):
        return self.normalizeRectF(self._pt_start, self._pt_end).contains(pointf)

    def paintMaskLayer(self, fullScreen=True):
        if fullScreen:  # 全屏遮罩层
            maskPixmap = QPixmap(self.rect().size())
            maskPixmap.fill(self.color_black)
            self.painter.drawPixmap(0, 0, maskPixmap)
        else:  # 绘制截图区域的周边区域遮罩层，以凸显截图区域
            if cfg.get(cfg.isAutoFindWindow) and self._pt_start == self._pt_end:
                cropRect = self.previewRect
            else:
                cropRect = self.normalizeRectF(self._pt_start, self._pt_end).toRect()
            fullScreenRegion = QRegion(self.rect())
            cropRegion = QRegion(cropRect)
            finalRegion = fullScreenRegion.subtracted(cropRegion)
            finalPath = QPainterPath()
            finalPath.addRegion(finalRegion)
            self.painter.fillPath(finalPath, self.color_black)

    def paintEvent(self, event):
        canvasPixmap = self.screenPixmap.copy()
        self.painter.begin(canvasPixmap)

        if self.hasScreenShot or cfg.get(cfg.isAutoFindWindow):
            # 绘制截图区域的周边区域遮罩层
            self.paintMaskLayer(fullScreen=False)
            # 绘制中央截图区域
            self.paintCenterArea()
        else:
            self.paintMaskLayer()
        self.paintMagnifyingGlass()

        self.painter.end()

        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, canvasPixmap)
        self.painter.end()

    def wheelEvent(self, a0):
        if a0.angleDelta().y() > 0:
            self._pixelFactor = self._pixelFactor - 2
        else:
            self._pixelFactor = self._pixelFactor + 2

        self._pixelFactor = max(4, min(self._pixelFactor, 60))
        self.update()
        return super().wheelEvent(a0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.hasScreenShot:
                if self.isMousePosInCenterRectF(pos):
                    self.isMoving = True  # 进入拖拽移动模式
                    self.setBeginDragPoint(pos)
                else:
                    self.isAdjusting = True  # 进入调整大小模式
                    self.setBeginAdjustPoint(pos)

                    # 如果在非截图区进行点击，那么直接拓展截图区
                    if self._mouseHitType == ScreenShotWindow.Unknown:
                        self.expandScreenShotArea(pos)
            else:
                self.setCenterArea(pos, pos)
                self.isCapturing = True  # 进入划定截图区域模式
        if event.button() == Qt.MouseButton.RightButton:
            self.cancelScreenShot()

    def pickUpScreenColor(self):
        text = self.getScreenColorStr()
        QApplication.clipboard().setText(text)
        self.clearScreenShot(False)
        self.close()

    def cancelScreenShot(self):
        if self.hasScreenShot or self.isCapturing:  # 清空已划定的的截图区域
            self.clearScreenShot()
        else:
            self.close()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.isCapturing = False
            self.isMoving = False
            self.isAdjusting = False

            if cfg.get(cfg.isAutoFindWindow) and self._pt_start == self._pt_end:
                self.setCenterArea(
                    self.previewRect.topLeft(),
                    self.previewRect.bottomRight() + QPoint(1, 1),
                )
                self.hasScreenShot = True
                self.isAdjusting = True
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.pos()
        if self.isVisible():
            self.mousePos: QPointF = pos
        if self.isCapturing:
            self.hasScreenShot = True
            self._pt_end = pos
        elif self.isMoving:
            self.moveCenterAreaTo(pos)
        elif self.isAdjusting:
            self.adjustCenterAreaBy(pos)
        if cfg.get(cfg.isAutoFindWindow):
            self.previewRect = self.findRectMgr.findTargetRect(self.mousePos)
        self.update()
        if self.hasScreenShot:
            self.setCursor(self.getMouseShapeBy(pos))
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isMousePosInCenterRectF(event.pos()):
                self.close()

    def physicalRectF(self, rectf: QRectF, isExpand=True):
        pixelRatio = self.screenPixmap.devicePixelRatio()
        return QRectF(
            rectf.x() * pixelRatio,
            rectf.y() * pixelRatio,
            rectf.width() * pixelRatio,
            rectf.height() * pixelRatio,
        )

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.closedSignal.emit()
        return super().closeEvent(a0)

    def keyPressEvent(self, event: QKeyEvent):
        if int(event.modifiers()) == Qt.Modifier.SHIFT:
            self.switchColorMode()
            self.update()
        self.moveMouseWithArrowKeys(event)
        super().keyPressEvent(event)

    def moveMouseWithArrowKeys(self, event: QKeyEvent):
        lastPos = QCursor.pos()
        if event.key() == Qt.Key_Up:
            QCursor.setPos(lastPos + QPoint(0, -1))
        elif event.key() == Qt.Key_Down:
            QCursor.setPos(lastPos + QPoint(0, 1))
        elif event.key() == Qt.Key_Left:
            QCursor.setPos(lastPos + QPoint(-1, 0))
        elif event.key() == Qt.Key_Right:
            QCursor.setPos(lastPos + QPoint(1, 0))

    def switchColorMode(self):
        self.showColorMode += 1
        if self.showColorMode > 2:
            self.showColorMode = 0
