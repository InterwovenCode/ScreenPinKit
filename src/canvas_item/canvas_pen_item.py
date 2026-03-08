# coding=utf-8
from .canvas_util import *


class CanvasPenItem(CanvasCommonPathItem):
    """
    绘图工具-画笔
    """

    def __init__(self, isSmoothCurve: bool = True, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.__initStyle()
        self.isSmoothCurve = isSmoothCurve

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
        return EnumCanvasItemType.CanvasPencilItem.value

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        penColor = styleMap["penColor"]
        penWidth = styleMap["penWidth"]
        self.usePen.setColor(penColor)
        self.usePen.setWidthF(penWidth * self.devicePixelRatio)
        self.update()

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    def __initEditMode(self):
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)
        self.setEditMode(
            CanvasCommonPathItem.HitTestMode, False
        )  # 如果想要显示当前HitTest区域，注释这行代码即可

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
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
        painter.drawPath(targetPath)

    def buildShapePath(
        self, targetPath: QPainterPath, targetPolygon: QPolygonF, isClosePath: bool
    ):
        if self.isSmoothCurve:
            CanvasUtil.polygon2BeizerPath(targetPath, targetPolygon)
        else:
            targetPath.addPolygon(targetPolygon)

    def setEditableState(self, isEditable: bool):
        """不允许绘制结束之后的重新编辑"""
        # return super().setEditableState(isEditable)
        pass
