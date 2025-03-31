# coding=utf-8
from .canvas_util import *
from .canvas_text_item import CanvasTextItem

class BubbleDirectionEnum(Enum):
    Null = ""
    TopLeft = "⇖"
    TopRight = "⇗"
    BottomLeft = "⇙"
    BottomRight = "⇘"
    Left = "⇐"
    Right = "⇒"

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
        bubbleDirection = BubbleDirectionEnum.BottomLeft
        styleMap = {
            "font": defaultFont,
            "textColor": QColor(Qt.GlobalColor.red),
            "outlineColor": QColor(Qt.GlobalColor.transparent), #让文本描边透明
            "penColor": QColor(Qt.GlobalColor.green),
            "brushColor": QColor(Qt.GlobalColor.blue),
            "useShadowEffect": False,
            "direction": bubbleDirection,
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
        penColor = styleMap["penColor"]
        brushColor = styleMap["brushColor"]
        bubbleDirection = styleMap["direction"]

        # 创建气泡路径
        path = QPainterPath()
        rect = self.boundingRect()
        path.addRoundedRect(rect, 10, 10) 

        vectorLength = 15

        if bubbleDirection == BubbleDirectionEnum.BottomRight:
            # 右下角
            triangle = QPainterPath()
            triangle.moveTo(rect.right(), rect.bottom() - 10)
            triangle.lineTo(max(rect.right() - 10, rect.left()), rect.bottom() - 2)
            triangle.lineTo(rect.right() + vectorLength, rect.bottom() + vectorLength)
            triangle.closeSubpath()
            path = path.united(triangle)
        elif bubbleDirection == BubbleDirectionEnum.BottomLeft:
            # 左下角
            triangle = QPainterPath()
            triangle.moveTo(rect.left(), rect.bottom() - 10)
            triangle.lineTo(min(rect.left() + 10, rect.right()), rect.bottom() - 2)
            triangle.lineTo(rect.left() - vectorLength, rect.bottom() + vectorLength)
            triangle.closeSubpath()
            path = path.united(triangle)
        elif bubbleDirection == BubbleDirectionEnum.TopLeft:
            # 左上角
            triangle = QPainterPath()
            triangle.moveTo(rect.left(), rect.top() + 10)
            triangle.lineTo(min(rect.left() + 10, rect.right()), rect.top() + 2)
            triangle.lineTo(rect.left() - vectorLength, rect.top() - vectorLength)
            triangle.closeSubpath()
            path = path.united(triangle)
        elif bubbleDirection == BubbleDirectionEnum.TopRight:
            # 右上角
            triangle = QPainterPath()
            triangle.moveTo(rect.right(), rect.top() + 10)
            triangle.lineTo(max(rect.right() - 10, rect.left()), rect.top() + 2)
            triangle.lineTo(rect.right() + vectorLength, rect.top() - vectorLength)
            triangle.closeSubpath()
            path = path.united(triangle)
        elif bubbleDirection == BubbleDirectionEnum.Left:
            # 左侧
            triangle = QPainterPath()
            triangle.moveTo(rect.left() + 4, max(rect.center().y() - vectorLength/2, rect.top()))
            triangle.lineTo(rect.left() + 4, min(rect.center().y() + vectorLength/2, rect.bottom()))
            triangle.lineTo(rect.left() - vectorLength, rect.center().y())
            triangle.closeSubpath()
            path = path.united(triangle)
        elif bubbleDirection == BubbleDirectionEnum.Right:
            # 右侧
            triangle = QPainterPath()
            triangle.moveTo(rect.right() - 4, max(rect.center().y() - vectorLength/2, rect.top()))
            triangle.lineTo(rect.right() - 4, min(rect.center().y() + vectorLength/2, rect.bottom()))
            triangle.lineTo(rect.right() + vectorLength, rect.center().y())
            triangle.closeSubpath()
            path = path.united(triangle)

        painter.setBrush(QBrush(brushColor))
        painter.setPen(QPen(penColor, 2 * self.devicePixelRatio))
        painter.drawPath(path)

        painter.restore()
        super().paint(painter, option, widget)