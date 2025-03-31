# coding=utf-8
from extend_widgets import *
from canvas_editor import *
from canvas_item import *
import typing


class CanvasItemToolBar(CommandBarView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.canvasItem = None
        self.initDefaultStyle()
        self.initUI()
        self.refreshStyleUI()
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

    def initDefaultStyle(self):
        raise NotImplementedError("子类需要重写该函数")

    def bindCanvasItem(
        self, canvasItem: CanvasShapeItem, sceneUserNotifyEnum: SceneUserNotifyEnum
    ):
        """
        绑定操作图元
        @note 存在多种情况

              1. 在选择模式下，各个图元选中切换时，此时各选项采取该图元的实际值来刷新
              2. 刚进入到绘图模式并且首次选择绘图工具，此时绑定图元为None，各选项按默认值初始化
              3. 在选择模式下，操作完当前工具对应图元之后，打算继续绘制新同类图元时，将各选项赋值到新图元上
        """
        if canvasItem != None:
            # 移除旧的绑定
            if self.canvasItem != None:
                if hasattr(self.canvasItem, "setWheelEventCallBack"):
                    self.canvasItem.setWheelEventCallBack(None)
            self.canvasItem = canvasItem

            if sceneUserNotifyEnum == SceneUserNotifyEnum.SelectItemChangedEvent:
                # 重新选中图元时，刷新各选项
                if hasattr(self.canvasItem, "setWheelEventCallBack") and hasattr(self.canvasItem, "onWheelZoom"):
                # if hasattr(self.canvasItem, "setWheelEventCallBack"):
                    self.canvasItem.setWheelEventCallBack(self.canvasItem.onWheelZoom)

                # QGraphicsItem.opacity()数值范围是：[0, 1]，滑块数值范围设定为：[0, 100]，这里需要转换下
                self.opacity = int(self.canvasItem.opacity() * 100)
                self.selectItemChangedHandle(self.canvasItem)
            elif sceneUserNotifyEnum == SceneUserNotifyEnum.StartDrawedEvent:
                self.refreshAttachItem()
        else:
            self.opacity = 100

        self.refreshStyleUI()

    def selectItemChangedHandle(self, canvasItem: QGraphicsItem):
        """刚切到该图元时"""
        # raise NotImplementedError("子类需要重写该函数")
        self.styleMap = self.canvasItem.styleAttribute.getValue().value()

        # QGraphicsItem.opacity()数值范围是：[0, 1]，滑块数值范围设定为：[0, 100]，这里需要转换下
        self.opacity = int(self.canvasItem.opacity() * 100)

    @typing.overload
    def refreshStyleUI(self):
        """根据styleMap刷新该UI"""
        raise NotImplementedError("子类需要重写该函数")

    @typing.overload
    def initUI(self):
        """初始化UI"""
        raise NotImplementedError("子类需要重写该函数")

    @typing.overload
    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.resetStyle(self.styleMap.copy())

    def initColorOptionUI(self, optionName: str, defaultColor: QColor):
        """颜色选项"""
        colorPickerButton = ColorPickerButtonEx(
            defaultColor, optionName, self, enableAlpha=True
        )
        colorPickerButton.setCheckable(True)
        colorPickerButton.setFixedSize(30, 30)

        self.initTemplateOptionUI(optionName, colorPickerButton)
        return colorPickerButton

    def initColorOptionUILite(self, defaultColor: QColor):
        """颜色选项"""
        colorPickerButton = ColorPickerButtonEx(
            defaultColor, "", self, enableAlpha=True
        )
        colorPickerButton.setCheckable(True)
        colorPickerButton.setFixedSize(30, 30)

        self.initTemplateOptionUILite(colorPickerButton)
        return colorPickerButton

    def initFontOptionUI(self, optionName: str, defaultFont: QFont):
        """字体选项"""
        fontPickerButton = FontPickerButtonPlus(defaultFont, optionName, self)
        fontPickerButton.setToolTip(self.tr("Change FontFamily"))

        self.initTemplateOptionUI(optionName, fontPickerButton)
        return fontPickerButton

    def initSliderOptionUI(
        self,
        optionName: str,
        defaultValue: int = 0,
        minValue: int = 0,
        maxValue: int = 100,
    ):
        """滑块选项"""
        opacitySlider = Slider(Qt.Horizontal)
        opacitySlider.setRange(minValue, maxValue)
        opacitySlider.setValue(defaultValue)
        self.initTemplateOptionUI(optionName, opacitySlider)
        return opacitySlider

    def initComboBoxOptionUI(
        self, optionName: str, optionDatas: list, defaultValue: any
    ):
        """
        下拉列表选项

        optionDatas:[(text, userData), ...]
        """
        comboBox = ComboBox(self)
        defaultIndex = -1
        tempIndex = 0
        for text, userData in optionDatas:
            if defaultValue == userData:
                defaultIndex = tempIndex
            comboBox.addItem(text=text, userData=userData)
            tempIndex = tempIndex + 1

        comboBox.setCurrentIndex(defaultIndex)

        self.initTemplateOptionUI(optionName, comboBox)
        return comboBox

    def initTemplateOptionUI(self, optionName: str, optionWidget: QWidget):
        """模板选项"""
        optionView = QWidget()
        optionLayout = QHBoxLayout()
        optionView.setLayout(optionLayout)
        optionLayout.addWidget(QLabel(optionName))
        optionLayout.addWidget(optionWidget)
        self.addWidget(optionView)
        return optionWidget

    def initTemplateOptionUILite(self, optionWidget: QWidget):
        """模板选项"""
        optionView = QWidget()
        optionLayout = QHBoxLayout()
        optionLayout.setContentsMargins(1, 1, 1, 1)
        optionView.setLayout(optionLayout)
        optionLayout.addWidget(optionWidget)
        self.addWidget(optionView)
        return optionWidget

    def showEvent(self, a0: QShowEvent) -> None:
        self.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        self.setIconSize(QSize(20, 20))
        self.resizeToSuitableWidth()
        self.adjustSize()
        return super().showEvent(a0)
