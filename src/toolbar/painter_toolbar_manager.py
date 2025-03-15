# coding=utf-8
from common import cfg
from .line_strip_toolbar import *
from .shape_toolbar import *
from .text_edit_toolbar import *
from .bubble_text_edit_toolbar import *
from .erase_toolbar import *
from .pen_toolbar import *
from .common_path_toolbar import *
from .arrow_toolbar import *
from .number_marker_item_toolbar import *
from .marker_pen_toolbar import *
from .canvas_item_toolbar import *
from .effect_toolbar import *


class PainterToolBarManager(QObject):
    providerChangeDrawActionSignal = pyqtSignal(DrawActionEnum)
    showToolbarSignal = pyqtSignal(QWidget)

    def __init__(self, targetWidget: QWidget, parent: QObject = None) -> None:
        super().__init__(parent)
        self.currentDrawActionEnum = DrawActionEnum.DrawNone
        self.targetWidget = targetWidget
        self.canvasItemBar: CommandBarView = None
        self.optionBar: QWidget = None
        self.zoomComponent = ZoomComponent()
        self.zoomComponent.zoomClamp = False
        self.zoomComponent.signal.connect(self.wheelZoom)

    def close(self):
        if self.optionBar == None:
            return

        if self.canvasItemBar != None:
            self.canvasItemBar.close()
            self.canvasItemBar.destroy()
            self.canvasItemBar = None

        if self.optionBar != None:
            self.optionBar.close()
            self.optionBar.destroy()
            self.optionBar = None

    def getActiveState(self) -> bool:
        if self.canvasItemBar != None and self.canvasItemBar.isActiveWindow():
            return True
        return False

    def switchSelectItemToolBar(
        self, canvasItem: QGraphicsItem, sceneUserNotifyEnum: SceneUserNotifyEnum
    ):
        """
        切换选中的图元

        1. 如果类型相同，则直接进行重新绑定
        2. 如果类型不同，则更换工具栏
        """
        if sceneUserNotifyEnum == SceneUserNotifyEnum.SelectNothing:
            self.currentDrawActionEnum = DrawActionEnum.DrawNone
            self.close()
            return

        if canvasItem == None:
            return

        drawActionEnum = DrawActionEnum.DrawNone
        if isinstance(self.canvasItemBar, BubbleTextEditToolbar):
            drawActionEnum = DrawActionEnum.EditBubbleText
        elif isinstance(self.canvasItemBar, TextEditToolbar):
            drawActionEnum = DrawActionEnum.EditText
        elif isinstance(self.canvasItemBar, ShapeToolbar):
            drawActionEnum = DrawActionEnum.DrawShape
        elif isinstance(self.canvasItemBar, NumberMarkerItemToolbar):
            drawActionEnum = DrawActionEnum.UseNumberMarker
        elif isinstance(self.canvasItemBar, ArrowToolbar):
            drawActionEnum = DrawActionEnum.DrawArrow
        elif isinstance(self.canvasItemBar, MarkerPenToolbar):
            drawActionEnum = DrawActionEnum.UseMarkerPen
        elif isinstance(self.canvasItemBar, LineStripToolbar):
            drawActionEnum = DrawActionEnum.DrawLineStrip
        elif isinstance(self.canvasItemBar, EffectToolbar):
            drawActionEnum = DrawActionEnum.UseEffectTool

        matchDrawActionEnum = DrawActionEnum.DrawNone
        if isinstance(canvasItem, CanvasBubbleTextItem):
            matchDrawActionEnum = DrawActionEnum.EditBubbleText
        elif isinstance(canvasItem, CanvasTextItem):
            matchDrawActionEnum = DrawActionEnum.EditText
        elif isinstance(canvasItem, CanvasShapeItem):
            matchDrawActionEnum = DrawActionEnum.DrawShape
        elif isinstance(canvasItem, CanvasNumberMarkerItem):
            matchDrawActionEnum = DrawActionEnum.UseNumberMarker
        elif isinstance(canvasItem, CanvasMarkerPen):
            matchDrawActionEnum = DrawActionEnum.UseMarkerPen
        elif isinstance(canvasItem, CanvasLineStripItem):
            matchDrawActionEnum = DrawActionEnum.DrawLineStrip
        elif isinstance(canvasItem, CanvasArrowItem):
            matchDrawActionEnum = DrawActionEnum.DrawArrow
        elif isinstance(canvasItem, CanvasEffectRectItem):
            matchDrawActionEnum = DrawActionEnum.UseEffectTool

        if drawActionEnum != matchDrawActionEnum:
            self.switchDrawTool(matchDrawActionEnum)

        if hasattr(self.canvasItemBar, "bindCanvasItem"):
            self.canvasItemBar.bindCanvasItem(canvasItem, sceneUserNotifyEnum)

    def switchDrawTool(self, drawActionEnum: DrawActionEnum) -> CommandBarView:
        if self.currentDrawActionEnum == drawActionEnum:
            return

        if (
            self.currentDrawActionEnum != DrawActionEnum.DrawNone
            and self.currentDrawActionEnum != drawActionEnum
        ):
            self.close()

        self.currentDrawActionEnum = drawActionEnum
        if drawActionEnum == DrawActionEnum.SelectItem:
            self.close()
            return

        if self.canvasItemBar == None:
            if drawActionEnum == DrawActionEnum.EditText:
                self.canvasItemBar = TextEditToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.EditBubbleText:
                self.canvasItemBar = BubbleTextEditToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.DrawShape:
                self.canvasItemBar = ShapeToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.UseEraser:
                self.canvasItemBar = EraseToolbar(parent=self.targetWidget)
                self.canvasItemBar.eraseTypeChangedSignal = (
                    self.providerChangeDrawActionSignal
                )
            elif drawActionEnum == DrawActionEnum.UseEffectTool:
                self.canvasItemBar = EffectToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.UsePen:
                self.canvasItemBar = PenToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.DrawLineStrip:
                self.canvasItemBar = LineStripToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.DrawArrow:
                self.canvasItemBar = ArrowToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.UseNumberMarker:
                self.canvasItemBar = NumberMarkerItemToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.UseMarkerPen:
                self.canvasItemBar = MarkerPenToolbar(parent=self.targetWidget)

        if self.canvasItemBar == None:
            return

        parent: BubbleTip = self.parent()
        finalTailPosition = BubbleTipTailPosition.TOP_LEFT_AUTO
        if parent.manager.isCorrectedBound():
            finalTailPosition = BubbleTipTailPosition.BOTTOM_LEFT_AUTO

        self.optionBar = BubbleTip.make(
            target=self.targetWidget,
            view=self.canvasItemBar,
            duration=-1,
            tailPosition=finalTailPosition,
            parent=self.targetWidget,
        )
        self.showToolbarSignal.emit(self.optionBar)

    def wheelZoom(self, angleDelta: int, kwargs):
        if self.canvasItemBar == None:
            return

        if cfg.get(cfg.toolbarUseWheelZoom):
            if hasattr(self.canvasItemBar, "wheelZoom"):
                self.canvasItemBar.wheelZoom(angleDelta, kwargs)
