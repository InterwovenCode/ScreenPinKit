# coding=utf-8
from .canvas_util import *


class CanvasLineStripItem(CanvasCommonPathItem):
    """
    绘图工具-折线

    Note:
    对于一个非封闭的PathItem而言，为了让它的HitTest行为约束在线段内，将其
    shape()里的shapePath由相邻两点加上线条宽度构成的连续矩形合并；
    另一方面，最终显示出来的线条则是QPen直接绘制原始PathItem所得
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.__initStyle()
        self.paintPath = QPainterPath()
        self.isCompleted = False

    def __initStyle(self):
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        styleMap = {
            "penColor": QColor(0, 255, 0, 100),
            "penWidth": 5,
        }

        self.usePen = QPen(styleMap["penColor"])
        self.usePen.setWidthF(styleMap["penWidth"] * self.devicePixelRatio)
        self.usePen.setCosmetic(True)
        self.usePen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.usePen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.canvasPolygonItem.value

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        penColor = styleMap["penColor"]
        penWidth = styleMap["penWidth"]
        self.usePen.setColor(penColor)
        self.usePen.setWidthF(penWidth * self.devicePixelRatio)
        self.update()

    def getOffsetLength(self) -> int:
        """
        Note:
        由于抗锯齿等渲染技术的影响，实际渲染的宽度可能会比设置的宽度略大，
        需要拿到QPaint.device().devicePixelRatioF()来进行转换处理
        """
        finalLength = int(self.usePen.widthF() / 2) / self.devicePixelRatio
        return finalLength

    def __initEditMode(self):
        """仅保Roi操作点"""
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        # self.setEditMode(UICanvasCommonPathItem.AdvanceSelectMode, False)
        self.setEditMode(
            CanvasCommonPathItem.HitTestMode, False
        )  # 如果想要显示当前HitTest区域，注释这行代码即可

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        if not self.isCompleted:
            return
        finalStyleMap = self.styleAttribute.getValue().value()
        finalWidth = finalStyleMap["penWidth"]

        # 计算缩放比例
        if event.delta() > 0:
            finalWidth = finalWidth + 1
        else:
            finalWidth = max(1, finalWidth - 1)
        finalStyleMap["penWidth"] = finalWidth
        self.styleAttribute.setValue(QVariant(finalStyleMap))

    def customPaint(self, painter: QPainter, targetPath: QPainterPath) -> None:
        painter.setPen(self.usePen)
        painter.drawPath(self.paintPath)

        if self.isHitTestMode():
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawPath(targetPath)

    def buildShapePath(
        self, targetPath: QPainterPath, targetPolygon: QPolygonF, isClosePath: bool
    ):
        self.paintPath.clear()
        CanvasUtil.buildSegmentsPath(self.paintPath, targetPolygon, isClosePath)
        super().buildShapePath(targetPath, targetPolygon, isClosePath)

    def completeDraw(self):
        self.isCompleted = True
        super().completeDraw()
