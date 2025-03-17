# coding:utf-8
from enum import Enum
from canvas_item import *
from version import *
import os, shutil

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import (
    qconfig,
    QConfig,
    ConfigItem,
    OptionsConfigItem,
    BoolValidator,
    ColorConfigItem,
    OptionsValidator,
    RangeConfigItem,
    RangeValidator,
    FolderListValidator,
    EnumSerializer,
    ConfigValidator,
    FolderValidator,
    ConfigSerializer,
)

from .template_config import TEMPLATE_CONFIG


class Language(Enum):
    """Language enumeration"""

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    # CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """Language serializer"""

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """Config of application"""

    # General
    dpiScale = OptionsConfigItem(
        "General",
        "DpiScale",
        "Auto",
        OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),
        restart=True,
    )
    language = OptionsConfigItem(
        "General",
        "Language",
        Language.AUTO,
        OptionsValidator(Language),
        LanguageSerializer(),
        restart=True,
    )
    cacheFolder = ConfigItem("General", "CacheFolder", "./cache", FolderValidator())
    imageNameFormat = ConfigItem(
        "General", "ImageNameFormat", "ScreenPinKit_{0}.png", ConfigValidator()
    )
    isAutoFindWindow = ConfigItem("General", "IsAutoFindWindow", True, BoolValidator())

    pluginMarketUrl = ConfigItem("General", "PluginMarketUrl", "https://github.com/InterwovenCode/ScreenPinKit-Plugin-Examples/raw/refs/heads/main/plugin_market/extensions.json", ConfigValidator())
    pluginsFolder = ConfigItem("General", "PluginsFolder", "..", FolderValidator())

    # HotKey
    hotKeyScreenShot = ConfigItem(
        "HotKey", "ScreenShot", "", ConfigValidator(), restart=True
    )
    hotKeyRepeatScreenShot = ConfigItem(
        "HotKey", "RepeatScreenShot", "", ConfigValidator(), restart=True
    )
    hotKeyScreenPaint = ConfigItem(
        "HotKey", "ScreenPaint", "", ConfigValidator(), restart=True
    )
    hotKeyToggleMouseClickThrough = ConfigItem(
        "HotKey", "MouseThough", "", ConfigValidator(), restart=True
    )
    hotKeyShowClipboard = ConfigItem(
        "HotKey", "ShowClipboard", "", ConfigValidator(), restart=True
    )
    hotKeySwitchScreenPaintMode = ConfigItem(
        "HotKey", "SwitchScreenPaintMode", "", ConfigValidator(), restart=True
    )

    # Software Update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator()
    )
    
    # Logger
    logLevel = OptionsConfigItem(
        "Logging", "LogLevel", "INFO", 
        OptionsValidator(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    )
    enableFileLogging = ConfigItem(
        "Logging", "EnableFileLogging", True, BoolValidator()
    )

    # Toolbar
    toolbarUseWheelZoom = ConfigItem("Toolbar", "useWheelZoom", True, BoolValidator())
    toolbarApplyWheelItem = ConfigItem(
        "Toolbar", "applyWheelItem", True, BoolValidator()
    )

    # WindowShadowStyle
    windowShadowStyleFocusColor = ColorConfigItem(
        "WindowShadowStyle", "focusColor", Qt.GlobalColor.blue
    )
    windowShadowStyleUnFocusColor = ColorConfigItem(
        "WindowShadowStyle", "unFocusColor", Qt.GlobalColor.gray
    )
    windowShadowStyleRoundRadius = OptionsConfigItem(
        "WindowShadowStyle", "roundRadius", 10, OptionsValidator([0, 5, 10, 15, 20])
    )
    windowShadowStyleIsSaveWithShadow = ConfigItem(
        "WindowShadowStyle", "isSaveWithShadow", False, BoolValidator()
    )
    windowShadowStyleIsCopyWithShadow = ConfigItem(
        "WindowShadowStyle", "isCopyWithShadow", False, BoolValidator()
    )

    # TextEditToolbar
    textEditToolbarFontFamily = ConfigItem(
        "TextEditToolbar", "fontFamily", "Microsoft YaHei"
    )
    textEditToolbarFontSize = RangeConfigItem(
        "TextEditToolbar", "fontSize", 5, RangeValidator(1, 100)
    )
    textEditToolbarTextColor = ColorConfigItem("TextEditToolbar", "textColor", Qt.red)
    textEditToolbarOutlineColor = ColorConfigItem("TextEditToolbar", "outlineColor", Qt.white)
    textEditToolbarUseShadowEffect = ConfigItem("TextEditToolbar", "useShadowEffect", True, BoolValidator())

    # BubbleTextEditToolbar
    bubbleTextEditToolbarFontFamily = ConfigItem(
        "BubbleTextEditToolbar", "fontFamily", "Microsoft YaHei"
    )
    bubbleTextEditToolbarFontSize = RangeConfigItem(
        "BubbleTextEditToolbar", "fontSize", 5, RangeValidator(1, 100)
    )
    bubbleTextEditToolbarTextColor = ColorConfigItem("BubbleTextEditToolbar", "textColor", Qt.red)
    bubbleTextEditToolbarOutlineColor = ColorConfigItem("BubbleTextEditToolbar", "outlineColor", QColor(0, 0, 0, 0))
    bubbleTextEditToolbarBubbleColor = ColorConfigItem("BubbleTextEditToolbar", "bubbleColor", Qt.GlobalColor.white)
    bubbleTextEditToolbarUseShadowEffect = ConfigItem("BubbleTextEditToolbar", "useShadowEffect", True, BoolValidator())

    # EffectToolbar
    effectToolbarStrength = RangeConfigItem(
        "EffectToolbar", "strength", 5, RangeValidator(1, 15)
    )
    effectToolbarEffectType = OptionsConfigItem(
        "EffectToolbar",
        "effectType",
        AfterEffectType.Blur,
        OptionsValidator(AfterEffectType),
        EnumSerializer(AfterEffectType),
    )

    # EraseToolbar
    eraseToolbarWidth = RangeConfigItem(
        "EraseToolbar", "width", 5, RangeValidator(1, 30)
    )

    # ShapeToolbar
    shapeToolbarPenWidth = RangeConfigItem(
        "ShapeToolbar", "penWidth", 4, RangeValidator(1, 30)
    )
    shapeToolbarBrushColor = ColorConfigItem(
        "ShapeToolbar", "brushColor", Qt.GlobalColor.blue
    )
    shapeToolbarPenColor = ColorConfigItem(
        "ShapeToolbar", "penColor", Qt.GlobalColor.gray
    )
    shapeToolbarPenStyle = OptionsConfigItem(
        "ShapeToolbar",
        "penStyle",
        Qt.PenStyle.SolidLine,
        OptionsValidator([Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine]),
    )
    shapeToolbarShape = OptionsConfigItem(
        "ShapeToolbar",
        "shape",
        CanvasShapeEnum.Rectangle,
        OptionsValidator(CanvasShapeEnum),
        EnumSerializer(CanvasShapeEnum),
    )

    # ArrowToolbar
    arrowToolbarPenWidth = RangeConfigItem(
        "ArrowToolbar", "penWidth", 2, RangeValidator(1, 30)
    )
    arrowToolbarBrushColor = ColorConfigItem(
        "ArrowToolbar", "brushColor", Qt.GlobalColor.blue
    )
    arrowToolbarPenColor = ColorConfigItem(
        "ArrowToolbar", "penColor", Qt.GlobalColor.gray
    )
    arrowToolbarPenStyle = OptionsConfigItem(
        "ArrowToolbar",
        "penStyle",
        Qt.PenStyle.SolidLine,
        OptionsValidator([Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine]),
    )

    # LineStripToolbar
    lineStripToolbarPenWidth = RangeConfigItem(
        "LineStripToolbar", "penWidth", 5, RangeValidator(1, 30)
    )
    lineStripToolbarPenColor = ColorConfigItem(
        "LineStripToolbar", "penColor", Qt.GlobalColor.red
    )

    # MarkerPenToolbar
    markerPenToolbarPenWidth = RangeConfigItem(
        "MarkerPenToolbar", "penWidth", 10, RangeValidator(1, 30)
    )
    markerPenToolbarPenColor = ColorConfigItem(
        "MarkerPenToolbar", "penColor", Qt.GlobalColor.red
    )

    # PenToolbar
    penToolbarPenWidth = RangeConfigItem(
        "PenToolbar", "penWidth", 5, RangeValidator(1, 30)
    )
    penToolbarPenColor = ColorConfigItem("PenToolbar", "penColor", Qt.GlobalColor.red)

    # NumberMarkerItemToolbar
    numberMarkerItemToolbarFontFamily = ConfigItem(
        "NumberMarkerItemToolbar", "fontFamily", "Microsoft YaHei"
    )
    numberMarkerItemToolbarTextColor = ColorConfigItem(
        "NumberMarkerItemToolbar", "textColor", Qt.GlobalColor.white
    )
    numberMarkerItemToolbarSize = RangeConfigItem(
        "NumberMarkerItemToolbar", "size", 20, RangeValidator(1, 100)
    )
    numberMarkerItemToolbarPenColor = ColorConfigItem(
        "NumberMarkerItemToolbar", "penColor", Qt.GlobalColor.gray
    )
    numberMarkerItemToolbarPenStyle = OptionsConfigItem(
        "NumberMarkerItemToolbar",
        "penStyle",
        Qt.PenStyle.SolidLine,
        OptionsValidator([Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine]),
    )
    numberMarkerItemToolbarBrushColor = ColorConfigItem(
        "NumberMarkerItemToolbar", "brushColor", QColor(255, 0, 0, 128)
    )
    numberMarkerItemToolbarUseShadowEffect = ConfigItem("NumberMarkerItemToolbar", "useShadowEffect", True, BoolValidator())

    # OcrLoaderSetting
    # 注意，OCRLoader采取的是动态加载方式，这里只是用于占位
    useOcrLoaderType = OptionsConfigItem(
        "OcrLoaderConfig", "OcrLoaderType", "InternalOcrLoader_ReturnTextPlus"
    )
    ocrLoaderFolder = ConfigItem(
        "OcrLoaderConfig", "OcrLoaderFolder", "", FolderValidator()
    )

    @property
    def numberMarkerItemToolbarFont(self):
        font = QFont(self.numberMarkerItemToolbarFontFamily.value)
        return font

    @numberMarkerItemToolbarFont.setter
    def numberMarkerItemToolbarFont(self, font: QFont):
        self.numberMarkerItemToolbarFontFamily.value = font.family()
        self.save()

    @property
    def textEditToolbarFont(self):
        font = QFont(self.textEditToolbarFontFamily.value)
        return font

    @textEditToolbarFont.setter
    def textEditToolbarFont(self, font: QFont):
        self.textEditToolbarFontFamily.value = font.family()
        self.save()

    @property
    def bubbleTextEditToolbarFont(self):
        font = QFont(self.bubbleTextEditToolbarFontFamily.value)
        return font

    @textEditToolbarFont.setter
    def bubbleTextEditToolbarFont(self, font: QFont):
        self.bubbleTextEditToolbarFontFamily.value = font.family()
        self.save()


configFolder = os.path.join(os.path.expanduser("~"), f".{APP_NAME}")
configPath = os.path.join(configFolder, "config.json")
if not os.path.exists(configFolder):
    os.mkdir(configFolder)

if not os.path.exists(configPath):
    with open(configPath, "w") as f:
        f.write(TEMPLATE_CONFIG)
        f.close()

cfg = Config()
qconfig.load(configPath, cfg)
