# coding=utf-8
from .canvas_util import *


class CanvasArrowItem(CanvasCommonPathItem):
    """
    绘图工具-箭头
    @note 滚轮可以控制箭头大小
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle()

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.zoomClamp = True
        self.zoomComponent.signal.connect(self.zoomHandle)

    def __initStyle(self):
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        internalStyleMap = {
            "arrowLength": 32.0 * self.devicePixelRatio,
            "arrowAngle": 0.5,
            "arrowBodyLength": 18 * self.devicePixelRatio,
            "arrowBodyAngle": 0.2,
        }
        self.internalAttribute = CanvasAttribute()
        self.internalAttribute.setValue(QVariant(internalStyleMap))
        self.internalAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

        styleMap = {
            "brushColor": QColor(255, 0, 0, 100),
            "penColor": QColor(255, 0, 0),
            "penWidth": 2 * self.devicePixelRatio,
            "penStyle": Qt.PenStyle.SolidLine,
        }

        self.usePen = QPen()
        self.usePen.setWidthF(styleMap["penWidth"])
        self.usePen.setColor(styleMap["penColor"])
        self.usePen.setStyle(styleMap["penStyle"])

        self.useBrushColor = styleMap["brushColor"]

        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def __initEditMode(self):
        """仅保Roi操作点"""
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)
        # self.setEditMode(CanvasCommonPathItem.RoiPreviewerMode, True)

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        penColor = styleMap["penColor"]
        penWidth = styleMap["penWidth"]
        penStyle = styleMap["penStyle"]
        self.usePen.setColor(penColor)
        self.usePen.setWidthF(penWidth)
        self.usePen.setStyle(penStyle)

        self.useBrushColor = styleMap["brushColor"]

        self.update()

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    def type(self) -> int:
        return EnumCanvasItemType.CanvasArrowItem.value

    def zoomHandle(self, zoomFactor):
        oldArrowStyleMap = self.internalAttribute.getValue().value()
        oldArrowStyleMap["arrowLength"] = oldArrowStyleMap["arrowLength"] * zoomFactor
        oldArrowStyleMap["arrowBodyLength"] = (
            oldArrowStyleMap["arrowBodyLength"] * zoomFactor
        )
        self.internalAttribute.setValue(QVariant(oldArrowStyleMap))

    def customPaint(self, painter: QPainter, targetPath: QPainterPath) -> None:
        painter.setBrush(self.useBrushColor)
        painter.setPen(self.usePen)
        painter.drawPath(targetPath)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta())

    def buildShapePath(
        self, targetPath: QPainterPath, targetPolygon: QPolygonF, isClosePath: bool
    ):
        arrowStyleMap = self.internalAttribute.getValue().value()
        CanvasUtil.buildArrowPath(targetPath, targetPolygon, arrowStyleMap)
