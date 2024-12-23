# coding=utf-8
from .canvas_util import *
from base import *

class CanvasNumberMarkerItem(QGraphicsRectItem):
    """
    绘图工具-索引标识
    @note 滚轮可以改变索引值
    """

    markderIndex = 0

    def __init__(self, rect: QRectF, parent: QGraphicsItem = None) -> None:
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        rect.setWidth(rect.width() * self.devicePixelRatio)
        rect.setHeight(rect.height() * self.devicePixelRatio)
        super().__init__(rect, parent)
        self.__initStyle()
        self.setDefaultFlag()
        CanvasNumberMarkerItem.markderIndex = self.markderIndex + 1
        self.index = CanvasNumberMarkerItem.markderIndex
        self.transformComponent = TransformComponent()
        self.zoomComponent = ZoomComponent()
        self.zoomComponent.zoomClamp = False
        self.zoomComponent.signal.connect(self.zoomHandle)

    def applyShadow(self):
        self.shadowEffect = QGraphicsDropShadowEffect()
        self.shadowEffect.setBlurRadius(20)  # 阴影的模糊半径
        self.shadowEffect.setColor(QColor(0, 0, 0, 100))  # 阴影的颜色和透明度
        self.shadowEffect.setOffset(5 * self.devicePixelRatio, 5 * self.devicePixelRatio)  # 阴影的偏移量
        self.setGraphicsEffect(self.shadowEffect)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        if(event.button() == Qt.MouseButton.LeftButton):
            self.textDialog = TextModifyDialog(f"{self.index}", self.scene().views()[0])
            self.textDialog.finalTextChanged.connect(self.__finalTextChanged)
            self.textDialog.exec()
            return
        return super().mouseDoubleClickEvent(event)

    def __finalTextChanged(self, text: str):
        try:
            self.textDialog.close()
            self.index = int(text)
            self.update()
        except Exception as e:
            pass

    def removeShadow(self):
        self.setGraphicsEffect(None)
        delattr(self, "shadowEffect")

    def __initStyle(self):
        defaultFont = QFont()
        styleMap = {
            "font": defaultFont,
            "textColor": QColor(Qt.GlobalColor.white),
            "penColor": QColor(Qt.GlobalColor.red),
            "size": 20,
            "penStyle": Qt.PenStyle.SolidLine,
            "brushColor": QColor(Qt.GlobalColor.red),
            "useShadowEffect": False,
        }

        self.usePen = QPen()
        self.usePen.setColor(styleMap["penColor"])
        self.usePen.setStyle(styleMap["penStyle"])
        self.useBrushColor = styleMap["brushColor"]
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasMarkerItem.value

    @property
    def showText(self):
        return f"{self.index}"

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        penColor = styleMap["penColor"]
        penStyle = styleMap["penStyle"]

        center = self.mapToScene(self.rect().center())
        rect = self.rect()
        size = styleMap["size"] * self.devicePixelRatio
        rect.setWidth(size)
        rect.setHeight(size)
        self.setRect(rect)
        self.setPos(center - self.rect().center())

        self.usePen.setColor(penColor)
        penWidth = math.ceil(self.rect().width() / 14.0)
        self.usePen.setWidth(penWidth)
        self.usePen.setStyle(penStyle)

        self.useBrushColor = styleMap["brushColor"]

        maybeUseShadowEffect = styleMap["useShadowEffect"]
        if not hasattr(self, "useShadowEffect"):
            self.useShadowEffect = False

        if self.useShadowEffect != maybeUseShadowEffect:
            if maybeUseShadowEffect:
                self.applyShadow()
            else:
                self.removeShadow()
        self.useShadowEffect = maybeUseShadowEffect

        self.update()

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ):
        styleMap = self.styleAttribute.getValue().value()
        font = styleMap["font"]
        textColor = styleMap["textColor"]

        painter.save()
        painter.setBrush(self.useBrushColor)
        painter.setPen(self.usePen)
        painter.drawEllipse(self.boundingRect())

        painter.setPen(textColor)

        offset = 5
        tempRect2 = self.boundingRect() - QMarginsF(offset, offset, offset, offset)
        CanvasUtil.adjustFontSizeToFit(self.showText, font, tempRect2, 1, 100)
        painter.setFont(font)

        align = Qt.AlignHCenter | Qt.AlignVCenter
        painter.drawText(self.rect(), align, self.showText)

        painter.restore()

    def setEditableState(self, isEditable: bool):
        """设置可编辑状态"""
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.oldPos = self.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.pos() != self.oldPos:
            self.transformComponent.movedSignal.emit(self, self.oldPos, self.pos())
        return super().mouseReleaseEvent(event)

    def completeDraw(self):
        pass

    def zoomHandle(self, zoomFactor:float, kwargs):
        wheelEvent:QGraphicsSceneWheelEvent = kwargs["wheelEvent"]
        finalStyleMap = self.styleAttribute.getValue().value()
        if int(wheelEvent.modifiers()) == Qt.ControlModifier:
            finalIndex = self.index
            if zoomFactor > 1:
                finalIndex = finalIndex + 1
            else:
                finalIndex = finalIndex - 1
            self.index = finalIndex
            finalStyleMap["index"] = self.index
        else:
            finalStyleMap = self.styleAttribute.getValue().value()
            finalWidth = finalStyleMap["size"]
            if zoomFactor > 1:
                finalWidth = finalWidth + 2
            else:
                finalWidth = max(finalWidth - 2, 1)
            finalStyleMap["size"] = finalWidth
        self.styleAttribute.setValue(QVariant(finalStyleMap))

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta(), wheelEvent=event)