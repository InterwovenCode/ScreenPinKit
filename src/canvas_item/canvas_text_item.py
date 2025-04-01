# coding=utf-8
from .canvas_util import *


class CanvasTextItem(QGraphicsTextItem):
    """
    绘图工具-文本框
    @note 滚轮可以控制字体大小
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__initStyle()

        self.transformComponent = TransformComponent()
        self.onWheelEvent = None

    def applyShadow(self):
        self.shadowEffect = QGraphicsDropShadowEffect()
        self.shadowEffect.setBlurRadius(20)  # 阴影的模糊半径
        self.shadowEffect.setColor(QColor(0, 0, 0, 100))  # 阴影的颜色和透明度
        self.shadowEffect.setOffset(5, 5)  # 阴影的偏移量
        self.setGraphicsEffect(self.shadowEffect)

    def removeShadow(self):
        self.setGraphicsEffect(None)
        if hasattr(self, "shadowEffect"):
            delattr(self, "shadowEffect")

    def setWheelEventCallBack(self, callback):
        self.onWheelEvent = callback

    def __initStyle(self):
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        defaultFont = QFont()
        defaultFont.setPointSize(16 * self.devicePixelRatio)
        styleMap = {
            "font": defaultFont,
            "textColor": QColor(Qt.GlobalColor.red),
            "outlineColor": QColor(Qt.GlobalColor.white),
            "useShadowEffect": False,
        }
        # 隐藏原本的文本渲染
        self.setDefaultTextColor(Qt.GlobalColor.transparent)
        self.setFont(defaultFont)
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def contextMenuEvent(self, event: QContextMenuEvent):
        pressEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
        releaseEvent = QKeyEvent(QEvent.KeyRelease, Qt.Key_Escape, Qt.NoModifier)
        
        QApplication.postEvent(self.scene().views()[0], pressEvent)
        QApplication.postEvent(self.scene().views()[0], releaseEvent)
        event.accept()

    def type(self) -> int:
        return EnumCanvasItemType.CanvasTextItem.value

    def styleAttributeChanged(self):
        originPos = self.pos()
        originSize = self.boundingRect().size()

        styleMap = self.styleAttribute.getValue().value()
        # 更新光标大小
        font = styleMap["font"]
        self.setFont(font)

        finalSize = self.boundingRect().size()
        finalPos = originPos + QPointF(
            (originSize.width() - finalSize.width()) / 2,
            (originSize.height() - finalSize.height()) / 2,
        )
        self.setPos(finalPos)

        maybeUseShadowEffect = styleMap["useShadowEffect"]
        if not hasattr(self, "useShadowEffect"):
            self.useShadowEffect = False

        if self.useShadowEffect != maybeUseShadowEffect:
            if maybeUseShadowEffect:
                self.applyShadow()
            else:
                self.removeShadow()
        self.useShadowEffect = maybeUseShadowEffect

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    # 设置默认模式
    def setDefaultFlag(self):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        # self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlags(
            QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)

    # 取消文本选中状态
    def cancelSelectedText(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def isCanEditable(self):
        """是否可编辑"""
        return (
            self.textInteractionFlags() | Qt.TextEditorInteraction
        ) == self.textInteractionFlags()

    def switchEditableBox(self, event: QGraphicsSceneMouseEvent = None):
        self.clearFocus()
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()

        if event == None:
            return

        pos = self.mapToText(event.pos())  # 让光标移到当前鼠标所在位置
        # pos = math.ceil(len(self.toPlainText())/2) # 让光标移到文本中间
        textCursor = self.textCursor()
        textCursor.setPosition(pos)
        self.setTextCursor(textCursor)

    def mapToText(self, pos):
        return self.document().documentLayout().hitTest(QPointF(pos), Qt.FuzzyHit)

    def focusInEvent(self, event: QFocusEvent) -> None:
        if (
            event.reason() != Qt.PopupFocusReason
        ):  # 注意右键菜单在此进入焦点时不保存原始文本
            self.m_store_str = self.toPlainText()  # 保存原始文本
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if (
            event.reason() == Qt.MouseFocusReason
            and QApplication.mouseButtons() == Qt.RightButton
        ):
            # 右键点击其他地方失去焦点，定义为取消操作，恢复原始文本
            self.setPlainText(self.m_store_str)
            self.setTextInteractionFlags(Qt.NoTextInteraction)  # 恢复不能编辑状态
        elif event.reason() == Qt.PopupFocusReason:
            # 右键弹出菜单时不做处理
            pass
        else:
            # 其他情况，包括下面点击回车的情况，编辑成功，发送信号给父对象
            self.cancelSelectedText()
            self.setDefaultFlag()
            # self.mySignal.emit(self.toPlainText())
        if len(self.toPlainText()) == 0:
            # 如果文本为空，则删除这个图元
            self.scene().removeItem(self)
        return super().focusOutEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.oldPos = self.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.pos() != self.oldPos:
            self.transformComponent.movedSignal.emit(self, self.oldPos, self.pos())
        return super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if not self.isCanEditable():
                # 左键双击进入可编辑状态并打开焦点
                self.switchEditableBox(event)
                return

        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.onWheelZoom(event.delta())
        if self.onWheelEvent != None:
            self.onWheelEvent(event.delta())

    def onWheelZoom(self, angleDelta: int):
        finalStyleMap = self.styleAttribute.getValue().value()
        finalFont = finalStyleMap["font"]
        finalFontSize = finalFont.pointSize()
        if angleDelta > 1:
            # 放大
            finalFontSize = finalFontSize + 2
        else:
            # 缩小
            finalFontSize = max(1, finalFontSize - 2)
        finalFont.setPointSize(finalFontSize)

        finalStyleMap["font"] = finalFont
        self.styleAttribute.setValue(QVariant(finalStyleMap))

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ):
        painter.save()

        styleMap = self.styleAttribute.getValue().value()
        finalFont = styleMap["font"]
        textColor = styleMap["textColor"]
        outlineColor = styleMap["outlineColor"]

        fm = QFontMetrics(finalFont)

        path = QPainterPath()
        block = self.document().firstBlock()

        while block.isValid():
            line_path = QPainterPath()
            line_path.addText(0, 0, finalFont, block.text())

            # 计算每行文本的偏移量
            line_metrics = self.document().documentLayout().blockBoundingRect(block)
            line_path.translate(line_metrics.topLeft())

            path.addPath(line_path)

            block = block.next()

        # 平移路径到正确的位置
        topLeft = self.boundingRect().topLeft()
        topLeft.setY(topLeft.y() + fm.ascent())
        path.translate(topLeft)

        # 绘制轮廓
        outlineWidth = math.ceil(finalFont.pointSize() / 10.0)
        painter.strokePath(path, QPen(outlineColor, outlineWidth))

        # 绘制文本
        painter.fillPath(path, QBrush(textColor))
        painter.restore()

        option.state = option.state & ~QStyle.StateFlag.State_Selected
        option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, widget)

    def handlePasteEvent(self):
        '''保证粘贴的文本是纯文本，不包含html标签'''
        clipboard = QApplication.clipboard()
        mimeData = clipboard.mimeData()
        
        if mimeData.hasText():
            plainText = mimeData.text()
            plainText = plainText.replace('\r\n', '\n').replace('\r', '\n')
            cursor = self.textCursor()
            
            # 移除当前选中的文本
            if cursor.hasSelection():
                cursor.removeSelectedText()
            
            cursor.insertText(plainText)
            self.setTextCursor(cursor)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.clearFocus()
            event.accept()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            self.handlePasteEvent()
            event.accept()
            return
        return super().keyPressEvent(event)

    def setEditableState(self, isEditable: bool):
        """设置可编辑状态"""
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)

    def completeDraw(self):
        pass
