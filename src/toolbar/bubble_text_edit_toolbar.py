# coding=utf-8
from common import ScreenShotIcon, cfg
from .canvas_item_toolbar import *


class BubbleTextEditToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        self.opacity: int = 100
        defaultFont = QFont()
        defaultPointSize = cfg.get(cfg.textEditToolbarFontSize) * self.devicePixelRatio
        defaultFontFamily = cfg.get(cfg.textEditToolbarFontFamily)
        defaultFont.setFamily(defaultFontFamily)
        defaultFont.setPointSize(defaultPointSize)
        self.styleMap = {
            "font": defaultFont,
            "textColor": cfg.get(cfg.bubbleTextEditToolbarTextColor),
            "outlineColor": cfg.get(cfg.bubbleTextEditToolbarOutlineColor),
            "bubbleColor": cfg.get(cfg.bubbleTextEditToolbarBubbleColor),
            "useShadowEffect": cfg.get(cfg.bubbleTextEditToolbarUseShadowEffect),
        }

    def initUI(self):
        self.boldButton = self.addAction(
            Action(
                ScreenShotIcon.TEXT_BOLD,
                self.tr("Text bold"),
                triggered=self.fontExtStyleChangedHandle,
            )
        )
        self.boldButton.setCheckable(True)
        self.italicButton = self.addAction(
            Action(
                ScreenShotIcon.TEXT_ITALIC,
                self.tr("Text italic"),
            )
        )
        self.italicButton.setCheckable(True)
        self.shadowEffectButton = self.addAction(
            Action(
                ScreenShotIcon.TEXT_SHADOW,
                self.tr("Shadow effect"),
            )
        )
        self.shadowEffectButton.setCheckable(True)
        self.textColorPickerButton = self.initColorOptionUI(
            self.tr("Text color"), self.styleMap["textColor"]
        )
        self.outlineColorPickerButton = self.initColorOptionUI(
            self.tr("Outline color"), self.styleMap["outlineColor"]
        )
        self.bubbleColorPickerButton = self.initColorOptionUI(
            self.tr("Bubble color"), self.styleMap["bubbleColor"]
        )
        self.fontPickerButton = self.initFontOptionUI(
            self.tr("Font"), self.styleMap["font"]
        )
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(
            self.tr("Opacity"), self.opacity, 10, 100
        )

    def fontExtStyleChangedHandle(self):
        font: QFont = self.styleMap["font"]
        font.setBold(self.boldButton.isChecked())
        font.setItalic(self.italicButton.isChecked())

        self.fontPickerButton.setTargetFont(font)

        self.refreshAttachItem()

    def shadowEffectChangedHandle(self):
        self.styleMap["useShadowEffect"] = self.shadowEffectButton.isChecked()
        self.refreshAttachItem()

    def refreshStyleUI(self):
        font: QFont = self.styleMap["font"]
        textColor: QColor = self.styleMap["textColor"]
        outlineColor: QColor = self.styleMap["outlineColor"]
        bubbleColor: QColor = self.styleMap["bubbleColor"]
        useShadowEffect: bool = self.styleMap["useShadowEffect"]
        self.boldButton.setChecked(font.bold())
        self.italicButton.setChecked(font.italic())
        self.opacitySlider.setValue(self.opacity)
        self.textColorPickerButton.setColor(textColor)
        self.outlineColorPickerButton.setColor(outlineColor)
        self.bubbleColorPickerButton.setColor(bubbleColor)
        self.fontPickerButton.setTargetFont(font)
        self.shadowEffectButton.setChecked(useShadowEffect)

    def textColorChangedHandle(self, color: QColor):
        self.styleMap["textColor"] = color
        self.refreshAttachItem()

    def outlineColorChangedHandle(self, color: QColor):
        self.styleMap["outlineColor"] = color
        self.refreshAttachItem()

    def bubbleColorChangedHandle(self, color: QColor):
        self.styleMap["bubbleColor"] = color
        self.refreshAttachItem()

    def fontChangedHandle(self, font: QFont):
        self.styleMap["font"] = font
        self.refreshAttachItem()

    def opacityValueChangedHandle(self, value: float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def listenerEvent(self):
        self.textColorPickerButton.colorChanged.connect(self.textColorChangedHandle)
        self.outlineColorPickerButton.colorChanged.connect(self.outlineColorChangedHandle)
        self.bubbleColorPickerButton.colorChanged.connect(self.bubbleColorChangedHandle)
        self.fontPickerButton.fontChanged.connect(self.fontChangedHandle)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandle)
        self.italicButton.clicked.connect(self.fontExtStyleChangedHandle)
        self.shadowEffectButton.clicked.connect(self.shadowEffectChangedHandle)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def onWheelZoom(self, angleDelta: int):
        finalFont: QFont = self.styleMap["font"]
        (minValue, maxValue) = cfg.textEditToolbarFontSize.range

        finalFontSize = finalFont.pointSize()
        if angleDelta > 1:
            finalFontSize = min(maxValue, finalFontSize + 2)
        else:
            finalFontSize = max(minValue, finalFontSize - 2)
        finalFont.setPointSize(finalFontSize)
        self.styleMap["font"] = finalFont

    def bindCanvasItem(
        self, canvasItem: CanvasTextItem, sceneUserNotifyEnum: SceneUserNotifyEnum
    ):
        """
        绑定操作图元
        @note 存在多种情况

              1. 在选择模式下，各个图元选中切换时，此时各选项采取该图元的实际值来刷新
              2. 刚进入到绘图模式并且首次选择绘图工具，此时绑定图元为None，各选项按默认值初始化
              3. 在选择模式下，操作完当前工具对应图元之后，打算继续绘制新同类图元时，将各选项赋值到新图元上
        """
        if canvasItem != None:
            if self.canvasItem != None:
                self.canvasItem.setWheelEventCallBack(None)
            self.canvasItem = canvasItem

            if sceneUserNotifyEnum == SceneUserNotifyEnum.SelectItemChangedEvent:
                self.canvasItem.setWheelEventCallBack(self.onWheelZoom)
                self.styleMap = self.canvasItem.styleAttribute.getValue().value()

                # QGraphicsItem.opacity()数值范围是：[0, 1]，滑块数值范围设定为：[0, 100]，这里需要转换下
                self.opacity = int(self.canvasItem.opacity() * 100)
                self.selectItemChangedHandle(self.canvasItem)
            elif sceneUserNotifyEnum == SceneUserNotifyEnum.StartDrawedEvent:
                self.refreshAttachItem()
        else:
            self.opacity = 100

        self.refreshStyleUI()
