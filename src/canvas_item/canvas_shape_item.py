# coding=utf-8
from .canvas_util import *


class CanvasShapeEnum(Enum):
    Ellipse = "Ellipse"
    Triangle = "Triangle"
    Rectangle = "Rectangle"
    Star = "Star"
    # NPolygon = "N边形"


class CanvasShapeItem(CanvasCommonPathItem):
    """
    绘图工具-闭合形状
    @note 滚轮可以控制描边宽度
    """

    def __init__(
        self,
        parent: QWidget = None,
        shapeType: CanvasShapeEnum = CanvasShapeEnum.Rectangle,
    ) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle(shapeType)
        self.sides = 3

    def __initStyle(self, shapeType: CanvasShapeEnum):
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        styleMap = {
            "brushColor": QColor(255, 0, 0, 100),
            "penColor": QColor(255, 0, 0),
            "penWidth": 2,
            "penStyle": Qt.PenStyle.SolidLine,
            "shape": shapeType,
        }

        self.usePen = QPen()
        self.usePen.setWidthF(styleMap["penWidth"] * self.devicePixelRatio)
        self.usePen.setColor(styleMap["penColor"])
        self.usePen.setStyle(styleMap["penStyle"])

        self.useBrushColor = styleMap["brushColor"]
        self.useShape = styleMap["shape"]

        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasClosedShapeItem.value

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    def __initEditMode(self):
        """仅保Roi操作点"""
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        penColor = styleMap["penColor"]
        penWidth = styleMap["penWidth"]
        penStyle = styleMap["penStyle"]
        self.usePen.setColor(penColor)
        self.usePen.setWidthF(penWidth * self.devicePixelRatio)
        self.usePen.setStyle(penStyle)

        self.useBrushColor = styleMap["brushColor"]
        self.useShape = styleMap["shape"]

        self.update()

    def customPaint(self, painter: QPainter, targetPath: QPainterPath) -> None:
        painter.setBrush(self.useBrushColor)
        painter.setPen(self.usePen)
        painter.drawPath(targetPath)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        if int(event.modifiers()) == Qt.ControlModifier:
            # if self.useShape == CanvasShapeEnum.NPolygon:
            #     if event.delta() > 0:
            #         self.sides = min(30, self.sides + 1)
            #     else:
            #         self.sides = max(0, self.sides - 1)
            #     self.update()
            pass
        else:
            finalStyleMap = self.styleAttribute.getValue().value()
            finalWidth = finalStyleMap["penWidth"]
            if event.delta() > 0:
                finalWidth = finalWidth + 1
            else:
                finalWidth = max(0, finalWidth - 1)

            finalStyleMap["penWidth"] = finalWidth
            self.styleAttribute.setValue(QVariant(finalStyleMap))

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(
        self, targetPath: QPainterPath, targetPolygon: QPolygonF, isClosePath: bool
    ):
        shapeType = self.useShape
        if shapeType == CanvasShapeEnum.Ellipse:
            CanvasUtil.buildEllipsePath(targetPath, targetPolygon)
        elif shapeType == CanvasShapeEnum.Rectangle:
            CanvasUtil.buildRectanglePath(targetPath, targetPolygon)
        elif shapeType == CanvasShapeEnum.Triangle:
            CanvasUtil.buildTrianglePath(targetPath, targetPolygon)
        # elif shapeType == CanvasShapeEnum.NPolygon:
        #     CanvasUtil.buildNPolygonPath(targetPath, targetPolygon, self.sides)
        elif shapeType == CanvasShapeEnum.Star:
            CanvasUtil.buildStarPath(targetPath, targetPolygon)

    def forceSquare(self):
        if self.polygon.count() == 2:
            begin = self.polygon.at(0)
            end = self.polygon.at(self.polygon.count() - 1)

            finalRect = QRectF(begin, end).normalized()
            maxLength = max(finalRect.width(), finalRect.height())

            if end.x() - begin.x() > 0:
                endPosX = begin.x() + maxLength
            else:
                endPosX = begin.x() - maxLength

            if end.y() - begin.y() > 0:
                endPosY = begin.y() + maxLength
            else:
                endPosY = begin.y() - maxLength

            end = QPointF(endPosX, endPosY)
            self.polygon.replace(1, end)
