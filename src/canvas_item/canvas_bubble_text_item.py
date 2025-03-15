# coding=utf-8
from .canvas_util import *
from .canvas_text_item import CanvasTextItem


class CanvasBubbleTextItem(CanvasTextItem):
    """
    绘图工具-文本框
    @note 滚轮可以控制字体大小
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__initStyle()

    def __initStyle(self):
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        defaultFont = QFont()
        defaultFont.setPointSize(16 * self.devicePixelRatio)
        styleMap = {
            "font": defaultFont,
            "textColor": QColor(Qt.GlobalColor.red),
            "outlineColor": QColor(Qt.GlobalColor.white),
            "bubbleColor": QColor(Qt.GlobalColor.blue),
            "useShadowEffect": False,
        }
        # 隐藏原本的文本渲染
        self.setDefaultTextColor(Qt.GlobalColor.transparent)
        self.setFont(defaultFont)
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasBubbleTextItem.value

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ):
        painter.save()

        styleMap = self.styleAttribute.getValue().value()
        bubbleColor = styleMap["bubbleColor"]

        # 创建气泡路径
        path = QPainterPath()
        rect = self.boundingRect()
        path.addRoundedRect(rect, 10, 10) 

        vectorLength = 15

        # 右下角
        triangle = QPainterPath()
        triangle.moveTo(rect.right(), rect.bottom() - 10)  # 左顶点
        triangle.lineTo(max(rect.right() - 10, rect.left()), rect.bottom() - 2)  # 右顶点
        triangle.lineTo(rect.right() + vectorLength, rect.bottom() + vectorLength)  # 下顶点
        triangle.closeSubpath()
        path = path.united(triangle)

        bubbleColor.setAlpha(150)
        painter.setBrush(QBrush(bubbleColor))
        bubbleColor.setAlpha(255)
        painter.setPen(bubbleColor)
        painter.drawPath(path)

        painter.restore()
        super().paint(painter, option, widget)