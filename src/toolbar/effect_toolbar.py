# coding=utf-8
from common import ScreenShotIcon, cfg
from .canvas_item_toolbar import *


class EffectToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        (minValue, maxValue) = cfg.effectToolbarStrength.range
        self.styleMap = {
            "strength": cfg.get(cfg.effectToolbarStrength),
            "minStrength": minValue,
            "maxStrength": maxValue,
            "effectType": cfg.get(cfg.effectToolbarEffectType),
        }

        self.effectTypeInfos = [
            (self.tr("Blur"), ScreenShotIcon.BLUR, AfterEffectType.Blur),
            (self.tr("Mosaic"), ScreenShotIcon.IMAGE_MOSAIC, AfterEffectType.Mosaic),
            (self.tr("Darken"), ScreenShotIcon.IMAGE_DARKEN, AfterEffectType.Darken),
            (self.tr("Invert"), ScreenShotIcon.IMAGE_INVERT, AfterEffectType.Invert),
            (self.tr("Detail"), ScreenShotIcon.IMAGE_DETAIL, AfterEffectType.Detail),
            (self.tr("Find_Edges"), ScreenShotIcon.IMAGE_FIND_EDGES, AfterEffectType.Find_Edges),
            (self.tr("Contour"), ScreenShotIcon.IMAGE_CONTOUR, AfterEffectType.Contour),
        ]

    def refreshStyleUI(self):
        strength: int = self.styleMap["strength"]
        self.strengthSlider.setValue(strength)

        currentEffectType = self.styleMap["effectType"]
        currentIndex = 0
        for _, _, effectType in self.effectTypeInfos:
            if effectType == currentEffectType:
                break
            currentIndex = currentIndex + 1
        self.effectTypeComBox.setCurrentIndex(currentIndex)

    def initUI(self):
        self.effectTypeComBox = self.initEffectOptionUI()
        (minValue, maxValue) = cfg.effectToolbarStrength.range
        self.strengthSlider = self.initSliderOptionUI(
            self.tr("Effect strength"), self.styleMap["strength"], minValue, maxValue
        )
        self.addSeparator()

    def initEffectOptionUI(self):
        """特效选项"""
        effectTypeComBox = ComboBox(self)
        for text, icon, enum in self.effectTypeInfos:
            effectTypeComBox.addItem(text=text, icon=icon, userData=enum)
        self.initTemplateOptionUI(self.tr("Effect"), effectTypeComBox)
        return effectTypeComBox

    def listenerEvent(self):
        self.strengthSlider.valueChanged.connect(self.strengthValueChangedHandle)
        self.effectTypeComBox.currentIndexChanged.connect(self.effectTypeComBoxHandle)

    def onEffectTypeChanged(self, effectType: AfterEffectType):
        self.styleMap["effectType"] = effectType
        self.refreshAttachItem()

    def strengthValueChangedHandle(self, value: float):
        self.styleMap["strength"] = value
        self.refreshAttachItem()

    def effectTypeComBoxHandle(self, index):
        comBox: ComboBox = self.effectTypeComBox
        self.styleMap["effectType"] = comBox.currentData()
        self.refreshAttachItem()

    def wheelZoom(self, angleDelta: int, kwargs):
        finalValue = self.strengthSlider.value()
        (minValue, maxValue) = cfg.effectToolbarStrength.range
        if angleDelta > 1:
            finalValue = min(maxValue, finalValue + 1)
        else:
            finalValue = max(minValue, finalValue - 1)
        self.strengthSlider.setValue(finalValue)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.resetStyle(self.styleMap.copy())