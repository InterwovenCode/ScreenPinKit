# coding:utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from common import cfg, ScreenShotIcon
from qfluentwidgets import FluentIcon as FIF
from extend_widgets import *
from canvas_item.after_effect_util import AfterEffectType
from canvas_item.canvas_shape_item import CanvasShapeEnum


class ToolbarInterface(QWidget):
    """Toolbar interface"""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("""
            ToolbarInterface{background: white}
            QLabel{
                font: 20px 'Segoe UI';
                background: rgb(242,242,242);
                border-radius: 8px;
            }
        """)

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.shapeToolbarInterface = self.buildShapeToolbar()
        self.lineStripToolbarInterface = self.buildLineStripToolbar()
        self.numberMarkerItemToolbarInterface = self.buildNumberMarkerItemToolbar()
        self.arrowToolbarInterface = self.buildArrowToolbar()
        self.markerPenToolbarInterface = self.buildMarkerPenToolbar()
        self.penToolbarInterface = self.buildPenToolbar()
        self.textEditToolbarInterface = self.buildTextEditToolbar()
        self.bubbleTextEditToolbarInterface = self.buildBubbleTextEditToolbar()
        self.eraseToolbarInterface = self.buildEraseToolbar()
        self.effectToolbarInterface = self.buildEffectToolBar()

        # add items to pivot
        self.addSubInterface(
            self.shapeToolbarInterface, "shapeToolbarInterface", self.tr("ShapeToolbar")
        )
        self.addSubInterface(
            self.lineStripToolbarInterface,
            "lineStripToolbarInterface",
            self.tr("LineStripToolbar"),
        )
        self.addSubInterface(
            self.numberMarkerItemToolbarInterface,
            "numberMarkerItemToolbarInterface",
            self.tr("NumberMarkerItemToolbar"),
        )
        self.addSubInterface(
            self.arrowToolbarInterface, "arrowToolbarInterface", self.tr("ArrowToolbar")
        )
        self.addSubInterface(
            self.markerPenToolbarInterface,
            "markerPenToolbarInterface",
            self.tr("MarkerPenToolbar"),
        )
        self.addSubInterface(
            self.penToolbarInterface, "penToolbarInterface", self.tr("PenToolbar")
        )
        self.addSubInterface(
            self.textEditToolbarInterface,
            "textEditToolbarInterface",
            self.tr("TextEditToolbar"),
        )
        self.addSubInterface(
            self.bubbleTextEditToolbarInterface,
            "bubbleTextEditToolbarInterface",
            self.tr("BubbleTextEditToolbar"),
        )
        self.addSubInterface(
            self.eraseToolbarInterface, "eraseToolbarInterface", self.tr("EraseToolbar")
        )
        self.addSubInterface(
            self.effectToolbarInterface,
            "effectToolbarInterface",
            self.tr("EffectToolbar"),
        )

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.shapeToolbarInterface)
        self.pivot.setCurrentItem(self.shapeToolbarInterface.objectName())

    def __onTextEditToolbarFontCardClicked(self):
        font, isOk = QFontDialog.getFont(
            cfg.textEditToolbarFont, self.window(), self.tr("Choose font")
        )
        if isOk:
            cfg.textEditToolbarFont = font

    def __onBubbleTextEditToolbarFontCardClicked(self):
        font, isOk = QFontDialog.getFont(
            cfg.bubbleTextEditToolbarFont, self.window(), self.tr("Choose font")
        )
        if isOk:
            cfg.bubbleTextEditToolbarFont = font

    def __onNumberMarkerItemToolbarFontCardClicked(self):
        font, isOk = QFontDialog.getFont(
            cfg.numberMarkerItemToolbarFont, self.window(), self.tr("Choose font")
        )
        if isOk:
            cfg.numberMarkerItemToolbarFont = font

    def buildEffectToolBar(self):
        effectToolBarGroup = SettingCardGroupLite(self)
        effectToolBarEffectTypeCard = ComboBoxSettingCardPlus(
            cfg.effectToolbarEffectType,
            ScreenShotIcon.EFFECT_TOOLBAR,
            self.tr("Effect type"),
            None,
            options=[
                (self.tr("Blur"), AfterEffectType.Blur),
                (self.tr("Mosaic"), AfterEffectType.Mosaic),
                (self.tr("Detail"), AfterEffectType.Detail),
                (self.tr("Find_Edges"), AfterEffectType.Find_Edges),
                (self.tr("Contour"), AfterEffectType.Contour),
            ],
            parent=effectToolBarGroup,
        )
        effectToolBarStrengthCard = RangeSettingCard(
            cfg.effectToolbarStrength,
            FIF.HIGHTLIGHT,
            self.tr("Effect strength"),
            parent=effectToolBarGroup,
        )

        effectToolBarGroup.addSettingCard(effectToolBarEffectTypeCard)
        effectToolBarGroup.addSettingCard(effectToolBarStrengthCard)
        return effectToolBarGroup

    def buildNumberMarkerItemToolbar(self):
        numberMarkerItemToolbarGroup = ScrollSettingCardGroupLite(self)
        numberMarkerItemToolbarFontCard = PushSettingCard(
            self.tr("Choose font"),
            FIF.FONT,
            self.tr("Font family"),
            parent=numberMarkerItemToolbarGroup,
        )
        numberMarkerItemToolbarTextColorCard = ColorSettingCard(
            cfg.numberMarkerItemToolbarTextColor,
            ScreenShotIcon.PEN,
            self.tr("Text color"),
            parent=numberMarkerItemToolbarGroup,
            enableAlpha=True,
        )
        numberMarkerItemToolbarSizeCard = RangeSettingCard(
            cfg.numberMarkerItemToolbarSize,
            ScreenShotIcon.CHOICE_SIZE,
            self.tr("Size"),
            parent=numberMarkerItemToolbarGroup,
        )
        numberMarkerItemToolbarPenColorCard = ColorSettingCard(
            cfg.numberMarkerItemToolbarPenColor,
            ScreenShotIcon.PEN,
            self.tr("Pen color"),
            parent=numberMarkerItemToolbarGroup,
            enableAlpha=True,
        )
        numberMarkerItemToolbarPenStyleCard = ComboBoxSettingCardPlus(
            cfg.numberMarkerItemToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            None,
            options=[
                (self.tr("Solid line"), Qt.PenStyle.SolidLine),
                (self.tr("Dash line"), Qt.PenStyle.DashLine),
            ],
            parent=numberMarkerItemToolbarGroup,
        )
        numberMarkerItemToolbarBrushColorCard = ColorSettingCard(
            cfg.numberMarkerItemToolbarBrushColor,
            ScreenShotIcon.BRUSH,
            self.tr("Brush color"),
            parent=numberMarkerItemToolbarGroup,
            enableAlpha=True,
        )
        numberMarkerItemToolbarShadowEffectCard = SwitchSettingCard(
            ScreenShotIcon.SHADOW_EFFECT,
            self.tr("Shadow effect"),
            None,
            configItem=cfg.numberMarkerItemToolbarUseShadowEffect,
            parent=numberMarkerItemToolbarGroup,
        )
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarSizeCard)
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarFontCard)
        numberMarkerItemToolbarGroup.addSettingCard(
            numberMarkerItemToolbarTextColorCard
        )
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarPenColorCard)
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarPenStyleCard)
        numberMarkerItemToolbarGroup.addSettingCard(
            numberMarkerItemToolbarBrushColorCard
        )

        numberMarkerItemToolbarFontCard.clicked.connect(
            self.__onNumberMarkerItemToolbarFontCardClicked
        )
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarShadowEffectCard)
        return numberMarkerItemToolbarGroup

    def buildPenToolbar(self):
        penToolbarGroup = SettingCardGroupLite(self)
        penToolbarWidthCard = RangeSettingCard(
            cfg.penToolbarPenWidth,
            ScreenShotIcon.PEN,
            self.tr("Pen width"),
            parent=penToolbarGroup,
        )
        penToolbarColorCard = ColorSettingCard(
            cfg.penToolbarPenColor,
            ScreenShotIcon.PEN,
            self.tr("Pen color"),
            parent=penToolbarGroup,
            enableAlpha=True,
        )
        penToolbarGroup.addSettingCard(penToolbarColorCard)
        penToolbarGroup.addSettingCard(penToolbarWidthCard)
        return penToolbarGroup

    def buildMarkerPenToolbar(self):
        markerPenToolbarGroup = SettingCardGroupLite(self)
        markerPenToolbarWidthCard = RangeSettingCard(
            cfg.markerPenToolbarPenWidth,
            ScreenShotIcon.PEN,
            self.tr("Pen width"),
            parent=markerPenToolbarGroup,
        )
        markerPenToolbarColorCard = ColorSettingCard(
            cfg.markerPenToolbarPenColor,
            ScreenShotIcon.PEN,
            self.tr("Pen color"),
            parent=markerPenToolbarGroup,
            enableAlpha=True,
        )
        markerPenToolbarGroup.addSettingCard(markerPenToolbarColorCard)
        markerPenToolbarGroup.addSettingCard(markerPenToolbarWidthCard)
        return markerPenToolbarGroup

    def buildLineStripToolbar(self):
        lineStripToolbarGroup = SettingCardGroupLite(self)
        lineStripToolbarWidthCard = RangeSettingCard(
            cfg.lineStripToolbarPenWidth,
            ScreenShotIcon.PEN,
            self.tr("Pen width"),
            parent=lineStripToolbarGroup,
        )
        lineStripToolbarColorCard = ColorSettingCard(
            cfg.lineStripToolbarPenColor,
            ScreenShotIcon.PEN,
            self.tr("Pen color"),
            parent=lineStripToolbarGroup,
            enableAlpha=True,
        )
        lineStripToolbarGroup.addSettingCard(lineStripToolbarColorCard)
        lineStripToolbarGroup.addSettingCard(lineStripToolbarWidthCard)
        return lineStripToolbarGroup

    def buildArrowToolbar(self):
        arrowToolbarGroup = SettingCardGroupLite(self)
        arrowToolbarPenWidthCard = RangeSettingCard(
            cfg.arrowToolbarPenWidth,
            ScreenShotIcon.PEN,
            self.tr("Pen width"),
            parent=arrowToolbarGroup,
        )
        arrowToolbarBrushColorCard = ColorSettingCard(
            cfg.arrowToolbarBrushColor,
            ScreenShotIcon.BRUSH,
            self.tr("Brush color"),
            parent=arrowToolbarGroup,
            enableAlpha=True,
        )
        arrowToolbarPenColorCard = ColorSettingCard(
            cfg.arrowToolbarPenColor,
            ScreenShotIcon.PEN,
            self.tr("Pen color"),
            parent=arrowToolbarGroup,
            enableAlpha=True,
        )
        arrowToolbarPenStyleCard = ComboBoxSettingCardPlus(
            cfg.arrowToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            None,
            options=[
                (self.tr("Solid line"), Qt.PenStyle.SolidLine),
                (self.tr("Dash line"), Qt.PenStyle.DashLine),
            ],
            parent=arrowToolbarGroup,
        )

        arrowToolbarGroup.addSettingCard(arrowToolbarPenWidthCard)
        arrowToolbarGroup.addSettingCard(arrowToolbarPenColorCard)
        arrowToolbarGroup.addSettingCard(arrowToolbarBrushColorCard)
        arrowToolbarGroup.addSettingCard(arrowToolbarPenStyleCard)
        return arrowToolbarGroup

    def buildEraseToolbar(self):
        eraseToolbarGroup = SettingCardGroupLite(self)
        eraseToolbarWidthCard = RangeSettingCard(
            cfg.eraseToolbarWidth,
            ScreenShotIcon.PEN,
            self.tr("Eraser width"),
            parent=eraseToolbarGroup,
        )
        eraseToolbarGroup.addSettingCard(eraseToolbarWidthCard)
        return eraseToolbarGroup

    def buildTextEditToolbar(self):
        textEditToolbarGroup = SettingCardGroupLite(self)
        textEditToolbarFontCard = PushSettingCard(
            self.tr("Choose font"),
            ScreenShotIcon.TEXT,
            self.tr("Font family"),
            parent=textEditToolbarGroup,
        )
        textEditToolbarFontSizeCard = RangeSettingCard(
            cfg.textEditToolbarFontSize,
            FIF.FONT_SIZE,
            self.tr("Font size"),
            parent=textEditToolbarGroup,
        )
        textEditToolbarTextColorCard = ColorSettingCard(
            cfg.textEditToolbarTextColor,
            ScreenShotIcon.PEN,
            self.tr("Text color"),
            parent=textEditToolbarGroup,
            enableAlpha=True,
        )
        textEditToolbarOutlineColorCard = ColorSettingCard(
            cfg.textEditToolbarOutlineColor,
            ScreenShotIcon.BRUSH,
            self.tr("Outline color"),
            parent=textEditToolbarGroup,
            enableAlpha=True,
        )
        textEditToolbarShadowEffectCard = SwitchSettingCard(
            ScreenShotIcon.SHADOW_EFFECT,
            self.tr("Shadow effect"),
            None,
            configItem=cfg.textEditToolbarUseShadowEffect,
            parent=textEditToolbarGroup,
        )

        textEditToolbarGroup.addSettingCard(textEditToolbarFontCard)
        textEditToolbarGroup.addSettingCard(textEditToolbarFontSizeCard)
        textEditToolbarGroup.addSettingCard(textEditToolbarTextColorCard)
        textEditToolbarGroup.addSettingCard(textEditToolbarOutlineColorCard)
        textEditToolbarGroup.addSettingCard(textEditToolbarShadowEffectCard)
        textEditToolbarFontCard.clicked.connect(self.__onTextEditToolbarFontCardClicked)
        return textEditToolbarGroup

    def buildBubbleTextEditToolbar(self):
        bubbleTextEditToolbarGroup = SettingCardGroupLite(self)
        bubbleTextEditToolbarFontCard = PushSettingCard(
            self.tr("Choose font"),
            ScreenShotIcon.TEXT,
            self.tr("Font family"),
            parent=bubbleTextEditToolbarGroup,
        )
        bubbleTextEditToolbarFontSizeCard = RangeSettingCard(
            cfg.bubbleTextEditToolbarFontSize,
            FIF.FONT_SIZE,
            self.tr("Font size"),
            parent=bubbleTextEditToolbarGroup,
        )
        bubbleTextEditToolbarTextColorCard = ColorSettingCard(
            cfg.bubbleTextEditToolbarTextColor,
            ScreenShotIcon.TEXT,
            self.tr("Text color"),
            parent=bubbleTextEditToolbarGroup,
            enableAlpha=True,
        )
        bubbleTextEditToolbarPenColorCard = ColorSettingCard(
            cfg.bubbleTextEditToolbarPenColor,
            ScreenShotIcon.PEN,
            self.tr("Pen color"),
            parent=bubbleTextEditToolbarGroup,
            enableAlpha=True,
        )
        bubbleTextEditToolbarBrushColorCard = ColorSettingCard(
            cfg.bubbleTextEditToolbarBrushColor,
            ScreenShotIcon.BRUSH,
            self.tr("Brush color"),
            parent=bubbleTextEditToolbarGroup,
            enableAlpha=True,
        )
        bubbleTextEditToolbarShadowEffectCard = SwitchSettingCard(
            ScreenShotIcon.SHADOW_EFFECT,
            self.tr("Shadow effect"),
            None,
            configItem=cfg.bubbleTextEditToolbarUseShadowEffect,
            parent=bubbleTextEditToolbarGroup,
        )

        bubbleTextEditToolbarGroup.addSettingCard(bubbleTextEditToolbarFontCard)
        bubbleTextEditToolbarGroup.addSettingCard(bubbleTextEditToolbarFontSizeCard)
        bubbleTextEditToolbarGroup.addSettingCard(bubbleTextEditToolbarTextColorCard)
        bubbleTextEditToolbarGroup.addSettingCard(bubbleTextEditToolbarPenColorCard)
        bubbleTextEditToolbarGroup.addSettingCard(bubbleTextEditToolbarBrushColorCard)
        bubbleTextEditToolbarGroup.addSettingCard(bubbleTextEditToolbarShadowEffectCard)
        bubbleTextEditToolbarFontCard.clicked.connect(self.__onBubbleTextEditToolbarFontCardClicked)
        return bubbleTextEditToolbarGroup

    def buildShapeToolbar(self):
        # shapeToolbar
        shapeToolbarGroup = SettingCardGroupLite(self)
        shapeToolbarPenWidthCard = RangeSettingCard(
            cfg.shapeToolbarPenWidth,
            ScreenShotIcon.PEN,
            self.tr("Pen width"),
            parent=shapeToolbarGroup,
        )
        shapeToolbarPenColorCard = ColorSettingCard(
            cfg.shapeToolbarPenColor,
            ScreenShotIcon.PEN,
            self.tr("Pen color"),
            parent=shapeToolbarGroup,
            enableAlpha=True,
        )
        shapeToolbarPenStyleCard = ComboBoxSettingCardPlus(
            cfg.shapeToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            None,
            options=[
                (self.tr("Solid line"), Qt.PenStyle.SolidLine),
                (self.tr("Dash line"), Qt.PenStyle.DashLine),
            ],
            parent=shapeToolbarGroup,
        )
        shapeToolbarBrushColorCard = ColorSettingCard(
            cfg.shapeToolbarBrushColor,
            ScreenShotIcon.BRUSH,
            self.tr("Brush color"),
            parent=shapeToolbarGroup,
            enableAlpha=True,
        )
        shapeToolbarShapeCard = ComboBoxSettingCardPlus(
            cfg.shapeToolbarShape,
            ScreenShotIcon.SHAPE,
            self.tr("Shape"),
            None,
            options=[
                (self.tr("Ellipse"), CanvasShapeEnum.Ellipse),
                (self.tr("Triangle"), CanvasShapeEnum.Triangle),
                (self.tr("Rectangle"), CanvasShapeEnum.Rectangle),
                (self.tr("Star"), CanvasShapeEnum.Star),
            ],
            parent=shapeToolbarGroup,
        )

        shapeToolbarGroup.addSettingCard(shapeToolbarPenWidthCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarPenColorCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarPenStyleCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarBrushColorCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarShapeCard)
        return shapeToolbarGroup

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        self.adjustSize()


class ToolbarSettingCard(ScrollArea):
    """Toolbar card with a push button"""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.interface = ToolbarInterface(self)

        self.resize(400, 400)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.interface)


class ToolbarSettingCardGroup(SettingCardGroup):
    """Setting card group"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent)
        self.toolbarCard = ToolbarSettingCard(self)
        self.addSettingCard(self.toolbarCard)
