# coding=utf-8
import typing, os, threading
from common import ScreenShotIcon
from canvas_editor import *
from canvas_item import *
from toolbar import *
from pdf_viewer import *
from plugin import pluginMgr, GlobalEventEnum
from plugin import *
from ocr_loader import *


# 绘制动作
class DrawAction:
    def __init__(
        self, actionEnum: DrawActionEnum, painterTool: QWidget, callback=None
    ) -> None:
        self.actionEnum: DrawActionEnum = actionEnum
        self.painterTool = painterTool
        self.callback = callback

    def switchEditState(self, isEdit: bool):
        if self.callback != None:
            self.callback(isEdit)


# 绘图控件
class PainterInterface(QWidget):
    ocrStartSignal = pyqtSignal()
    ocrEndSuccessSignal = pyqtSignal(object)
    ocrEndFailSignal = pyqtSignal(str)
    showCommandBarSignal = pyqtSignal(QWidget)

    def __init__(self, parent=None, physicalPixmap: QPixmap = None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.physicalPixmap = physicalPixmap
        self.toolbar: QWidget = None
        self.actionGroup: QActionGroup = None
        self.drawWidget: CanvasEditor = None
        self.sceneBrush: QBrush = None
        self.painterToolBarMgr: PainterToolBarManager = None
        self.currentDrawActionEnum = DrawActionEnum.DrawNone
        self.hotkey = QWidgetHotKey()
        self.hotkey.setHotkeyListenerEx("space", 3, self.clearDraw)
        self.initLayout()

    def initLayout(self):
        self.contentLayout = QVBoxLayout()
        self.contentLayout.setAlignment(Qt.AlignHCenter)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.contentLayout)

        if self.physicalPixmap != None:
            basePixmap = self.physicalPixmap.copy()
            basePixmap = OsHelper.ConvertToRoundedPixmap(basePixmap, 0)
            self.sceneBrush = QBrush(basePixmap)
            screenDevicePixelRatio = CanvasUtil.getDevicePixelRatio()
            transform = QTransform()
            transform.scale(1 / screenDevicePixelRatio, 1 / screenDevicePixelRatio)
            self.sceneBrush.setTransform(transform)

            self.ocrStartSignal.connect(self.onOcrStart)
            self.ocrEndSuccessSignal.connect(self.onOcrEndSuccess)
            self.ocrEndFailSignal.connect(self.onOcrEndFail)

    def getCommandBarPosition(self) -> BubbleTipTailPosition:
        return BubbleTipTailPosition.AUTO

    def getActiveState(self) -> bool:
        if self.toolbar != None and  self.toolbar.isActiveWindow():
            return True
        
        if self.painterToolBarMgr != None and self.painterToolBarMgr.getActiveState():
            return True

        return False

    def showCommandBar(self):
        if self.toolbar != None:
            self.toolbar.show()
            self.drawWidget.switchDrawTool(DrawActionEnum.DrawNone)
            return

        position = self.getCommandBarPosition()
        view = CommandBarView(self)

        # 锁定机制-绘制工具
        lockState = self.drawWidget.getLockState()
        if lockState:
            switchLockAction = Action(
                ScreenShotIcon.LOCKED, self.tr("Locked"), triggered=self.switchLocked
            )
        else:
            switchLockAction = Action(
                ScreenShotIcon.UNLOCKED,
                self.tr("UnLocked"),
                triggered=self.switchLocked,
            )

        switchLockAction.setCheckable(True)
        self.switchLockButton = view.addAction(switchLockAction)
        switchLockAction.setChecked(lockState)

        view.addSeparator()

        selectItemAction = Action(
            ScreenShotIcon.SELECT_ITEM,
            self.tr("Select item"),
            triggered=lambda: self.switchDrawTool(DrawActionEnum.SelectItem),
        )
        finalDrawActions = [selectItemAction]
        self.selectItemAction = selectItemAction

        # 初始化绘制工具栏
        drawActions = [
            Action(
                ScreenShotIcon.SHAPE,
                self.tr("Shape"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawShape),
            ),
            Action(
                ScreenShotIcon.LINE_STRIP,
                self.tr("Line strip"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawLineStrip),
            ),
            Action(
                ScreenShotIcon.NUMBER_MARKER,
                self.tr("Number marker"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.UseNumberMarker),
            ),
            # Action(ScreenShotIcon.POLYGON, '图案', triggered=lambda: self.switchDrawTool(DrawActionEnum.PasteSvg)),
            Action(
                ScreenShotIcon.ARROW,
                self.tr("Arrow"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawArrow),
            ),
            Action(
                ScreenShotIcon.MARKER_PEN,
                self.tr("Marker pen"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.UseMarkerPen),
            ),
            Action(
                ScreenShotIcon.PEN,
                self.tr("Pen"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.UsePen),
            ),
            Action(
                ScreenShotIcon.TEXT,
                self.tr("TextEdit"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.EditText),
            ),
            Action(
                ScreenShotIcon.IMAGE_BUBBLE_TEXT,
                self.tr("BubbleTextEdit"),
                triggered=lambda: self.switchDrawTool(DrawActionEnum.EditBubbleText),
            ),
        ]

        for action in drawActions:
            finalDrawActions.append(action)

        # 仅当有背景画刷的时候，橡皮擦和模糊工具才可以使用
        if self.drawWidget.sceneBrush != None:
            extendActions = [
                Action(
                    ScreenShotIcon.ERASER,
                    self.tr("Eraser"),
                    triggered=lambda: self.switchDrawTool(DrawActionEnum.UseEraser),
                ),
                Action(
                    ScreenShotIcon.IMAGE_MOSAIC,
                    self.tr("Mosaic/Blur"),
                    triggered=lambda: self.switchDrawTool(DrawActionEnum.UseEffectTool),
                ),
            ]
            for action in extendActions:
                finalDrawActions.append(action)

        self.actionGroup = QActionGroup(self)
        for action in finalDrawActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)

        view.addActions(finalDrawActions)
        view.addSeparator()

        if self.drawWidget.sceneBrush != None:
            extraActions = [
                Action(ScreenShotIcon.OCR, self.tr("OCR"), triggered=self.startOcr)
            ]
            pluginMgr.handleEvent(
                GlobalEventEnum.RegisterToolbarMenuEvent,
                actions=extraActions,
                pixmap=self.physicalPixmap,
                parent=self,
            )
            view.addActions(extraActions)

        view.addActions(
            [
                Action(
                    ScreenShotIcon.DELETE_ALL,
                    self.tr("Clear draw"),
                    triggered=self.clearDraw,
                ),
                Action(ScreenShotIcon.UNDO, self.tr("Undo"), triggered=self.undo),
                Action(ScreenShotIcon.REDO, self.tr("Redo"), triggered=self.redo),
                Action(
                    ScreenShotIcon.FINISHED,
                    self.tr("Finish draw"),
                    triggered=self.completeDraw,
                ),
            ]
        )

        view.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        view.setIconSize(QSize(20, 20))

        view.resizeToSuitableWidth()

        self.toolbar = BubbleTip.make(
            target=self,
            view=view,
            duration=-1,
            tailPosition=position,
            parent=self,
        )
        self.showCommandBarSignal.emit(self.toolbar)

        self.initDrawLayer()
        self.painterToolBarMgr = PainterToolBarManager(view, self.toolbar)
        self.painterToolBarMgr.showToolbarSignal.connect(self.showCommandBarSignal)
        self.painterToolBarMgr.providerChangeDrawActionSignal.connect(
            self.onProviderChangeDrawAction
        )

    def onProviderChangeDrawAction(self, drawActionEnum: DrawActionEnum):
        self.switchDrawTool(drawActionEnum)

    def initDrawLayer(self):
        if self.drawWidget != None:
            return

        self.drawWidget = CanvasEditor(self, self.sceneBrush)
        self.drawWidget.initUI()
        self.drawWidget.setNofityEvent(self.sceneUserNotifyHandler)
        self.contentLayout.addWidget(self.drawWidget)

    def sceneUserNotifyHandler(
        self, sceneUserNotifyEnum: SceneUserNotifyEnum, item: QGraphicsItem
    ):
        if (
            sceneUserNotifyEnum == SceneUserNotifyEnum.EndDrawedEvent
            and not self.drawWidget.getLockState()
        ):
            if item != None:
                item.setEditableState(True)
                if hasattr(item, "forceSelect"):
                    item.forceSelect()
                self.directSwitchDrawTool(DrawActionEnum.SelectItem)
            self.selectItemAction.setChecked(True)

        if sceneUserNotifyEnum in [
            SceneUserNotifyEnum.SelectItemChangedEvent,
            SceneUserNotifyEnum.StartDrawedEvent,
            SceneUserNotifyEnum.SelectNothing,
        ]:
            if self.painterToolBarMgr != None:
                self.painterToolBarMgr.switchSelectItemToolBar(
                    item, sceneUserNotifyEnum
                )

    def completeDraw(self):
        self.switchDrawTool(DrawActionEnum.DrawNone)
        if self.toolbar != None:
            self.clearDrawFlag()
            self.toolbar.close()
            self.toolbar.destroy()
            self.toolbar = None
            self.painterToolBarMgr.close()
            self.painterToolBarMgr = None
            self.drawWidget.quitDraw()

    def switchLocked(self):
        self.drawWidget.switchLockState()
        finalIcon = None
        tip = ""
        if self.drawWidget.getLockState():
            finalIcon = ScreenShotIcon.LOCKED
            tip = self.tr("Locked")
        else:
            finalIcon = ScreenShotIcon.UNLOCKED
            tip = self.tr("UnLocked")
        self.switchLockButton.setIcon(finalIcon)
        self.switchLockButton.setToolTip(tip)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.completeDraw()

    def tryQuitDraw(self):
        # 如果当前绘图工具不在编辑状态，则本次按下Esc键会关掉绘图工具条
        if not self.currentDrawActionEnum in [
            DrawActionEnum.DrawNone,
            DrawActionEnum.SelectItem,
        ]:
            self.selectItemAction.trigger()
            return False
        elif self.toolbar != None and self.toolbar.isVisible():
            self.completeDraw()
            return False
        return True

    def undo(self):
        self.drawWidget.undo()

    def redo(self):
        self.drawWidget.redo()

    def clickThrough(self):
        self.parentWidget().setMouseThroughState(True)

    # 得到最终绘制后的Pixmap
    def getFinalPixmap(self) -> QPixmap:
        # 经测试，这种方式截屏会有概率出现白边，推测是精度问题导致的，遂改成下面的实现
        # return self.grab()

        basePixmap = self.physicalPixmap.copy()
        painter = QPainter()
        painter.begin(basePixmap)
        if self.drawWidget != None:
            painter.drawPixmap(self.drawWidget.geometry(), self.drawWidget.grab())
        painter.end()
        return basePixmap

    def copyToClipboard(self):
        kv = {"pixmap": self.getFinalPixmap()}
        pluginMgr.handleEvent(GlobalEventEnum.ImageCopyingEvent, kv=kv, parent=self)
        finalPixmap = kv["pixmap"]
        QApplication.clipboard().setPixmap(finalPixmap)

    def switchDrawTool(
        self,
        drawActionEnum: DrawActionEnum,
        cursor: QCursor = Qt.CursorShape.ArrowCursor,
    ):
        self.drawWidget.switchDrawTool(drawActionEnum)
        if not hasattr(self, "drawActionInfo"):
            self.drawActionInfo = DrawActionInfo()
        if self.preHandleEraseToole(drawActionEnum):
            return
        if self.currentDrawActionEnum != drawActionEnum:
            self.createCustomInfoBar(
                "%s 【%s】"
                % (self.tr("Switch to"), self.drawActionInfo.getInfo(drawActionEnum))
            )
        self.currentDrawActionEnum = drawActionEnum
        if self.painterToolBarMgr != None:
            self.painterToolBarMgr.switchDrawTool(drawActionEnum)
        self.setCursor(cursor)

        if drawActionEnum == DrawActionEnum.SelectItem:
            if hasattr(self, "webViewerItem"):
                self.webViewerItem.setEnabled(True)
        else:
            if hasattr(self, "webViewerItem"):
                self.webViewerItem.setEnabled(False)
                self.webViewerItem.cancelSelectText()

    def preHandleEraseToole(self, drawActionEnum: DrawActionEnum):
        eraseTools = [
            DrawActionEnum.UseEraser, 
            DrawActionEnum.UseEraserRectItem, 
            DrawActionEnum.UseShadowEraserRectItem,
            DrawActionEnum.UseShadowEraserEllipseItem,
        ]
        if self.currentDrawActionEnum in eraseTools and drawActionEnum in eraseTools:
            self.directSwitchDrawTool(drawActionEnum)
            return True
        return False

    def directSwitchDrawTool(
        self,
        drawActionEnum: DrawActionEnum,
        cursor: QCursor = Qt.CursorShape.ArrowCursor,
    ):
        self.drawWidget.switchDrawTool(drawActionEnum)
        self.currentDrawActionEnum = drawActionEnum
        self.setCursor(cursor)

    def clearDraw(self):
        if hasattr(self, "drawWidget"):
            self.drawWidget.clearDraw()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.hotkey.keyPressEvent(event)
        super().keyPressEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        self.parentWidget().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        # 获取鼠标居于屏幕上的位置点
        pos = QCursor.pos()

        # 计算绘图区和工具区的并集
        painterRect = QRect(
            self.mapToGlobal(self.rect().topLeft()),
            self.mapToGlobal(self.rect().bottomRight()),
        )
        rects = [painterRect]
        if self.toolbar != None:
            toolbarRect = QRect(
                self.toolbar.mapToGlobal(self.toolbar.rect().topLeft()),
                self.toolbar.mapToGlobal(self.toolbar.rect().bottomRight()),
            )
            rects.append(toolbarRect)
        region = QRegion()
        region.setRects(rects)

        # 经测试发现，焦点非常容易变化，但是我们在绘图区和工具区的操作引起的焦点丢失得屏蔽掉
        if not region.contains(pos):
            self.parentWidget().focusOutEvent(event)

    def clearDrawFlag(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawNone
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if self.actionGroup != None:
            for action in self.actionGroup.actions():
                action.setChecked(False)

    def createCustomInfoBar(self, text: str):
        w = InfoBar.new(
            icon=ScreenShotIcon.GUIDE,
            title="",
            content=text,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.BOTTOM,
            duration=1000,
            parent=self,
        )
        # w.iconWidget.setFixedSize(QSize(40, 40))
        w.setCustomBackgroundColor("white", "#202020")

    def wheelEvent(self, event: QWheelEvent):
        if self.painterToolBarMgr != None:
            self.painterToolBarMgr.zoomComponent.TriggerEvent(event.angleDelta().y(), wheelEvent=event)
        return super().wheelEvent(event)

    def startOcr(self):
        """使用独立线程进行OCR识别"""
        if hasattr(self, "ocrState"):
            self.showCommandBar()
            self.selectItemAction.trigger()
            return
        self.ocrState = 0
        self.ocrThread = OcrThread(self.onExecuteOcr, self.physicalPixmap)
        self.ocrThread.start()
        # self.onExecuteOcr(self.physicalPixmap)

    def checkOcrLoaderValid(self):
        """纠正OCR加载器配置失效情况"""
        if len(ocrLoaderMgr.loaderDict) == 0:
            raise Exception("没有可支持的OCR加载器，无法进行OCR识别")
        ocrLoaderName = cfg.get(cfg.useOcrLoaderType)
        if not ocrLoaderName in ocrLoaderMgr.loaderDict:
            keys = list(ocrLoaderMgr.loaderDict.keys())
            cfg.set(cfg.useOcrLoaderType, keys[0])

    def onExecuteOcr(self, pixmap: QPixmap):
        try:
            self.checkOcrLoaderValid()
            self.ocrLoader: OcrLoaderInterface = ocrLoaderMgr.loaderDict[
                cfg.get(cfg.useOcrLoaderType)
            ]
            logger.info(
                f"ocr info [{self.ocrLoader.mode}]: {pixmap.size()} {os.getppid()} {threading.current_thread().ident}", logger_name="ocr"
            )
            self.ocrStartSignal.emit()

            result = self.ocrLoader.ocr(pixmap)
            logger.info(result, logger_name="ocr")
            self.ocrEndSuccessSignal.emit(result)

        except Exception as e:
            message = "\n".join(e.args)
            logger.error(message, logger_name="ocr")
            self.ocrEndFailSignal.emit(message)

        self.ocrState = 1

    def onOcrStart(self):
        # pluginMgr.handleEvent(GlobalEventEnum.OcrStartEvent, parent_widget=self, ocr_mode=self.ocrLoader.mode)
        pluginMgr.handleEvent(
            GlobalEventEnum.OcrStartEvent,
            parent_widget=self,
            ocr_mode=self.ocrLoader.displayName,
        )

    def onEscPressed(self, hasSelectedText):
        if hasSelectedText:
            if hasattr(self, "webViewerItem"):
                self.webViewerItem.cancelSelectText()
        else:
            escapeEvent = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
            QApplication.sendEvent(self, escapeEvent)

    def onHtmlRenderStart(self):
        if hasattr(self, "webViewerItem"):
            self.webViewerItem.setOpacity(0)

    def onHtmlRenderEnd(self, _width, _height):
        self.delayTimer = QTimer(self)
        self.delayTimer.timeout.connect(self.onDelayExecute)
        self.delayTimer.start(300)

    def onDelayExecute(self):
        self.delayTimer.stop()
        if hasattr(self, "webViewerItem"):
            self.webViewerItem.setOpacity(1)

        self.showCommandBar()
        self.selectItemAction.trigger()

    def onOcrEndForReturnStr(self, input: str):
        # 渲染Html
        if input.endswith(".pdf"):
            self.webViewerItem = CanvasOcrViewerItem(PdfWidget())
        elif input.endswith(".html"):
            self.webViewerItem = CanvasOcrViewerItem(WebWidget())
        else:
            # 传了一个网页文本进来
            self.webViewerItem = CanvasOcrViewerItem(WebWidget())

        self.webViewerItem.receiver.htmlRenderStartSlot.connect(self.onHtmlRenderStart)
        self.webViewerItem.receiver.htmlRenderEndSlot.connect(self.onHtmlRenderEnd)
        self.webViewerItem.receiver.escPressedSlot.connect(self.onEscPressed)

        self.drawWidget.scene.addItem(self.webViewerItem)
        # 让OCR文本层位于最底部
        self.webViewerItem.setZValue(-1)

        if input.endswith(".html") or input.endswith(".pdf"):
            self.webViewerItem.openFile(input)
        else:
            self.webViewerItem.setHtml(input)

    def onOcrEndForReturnJson(self, input: dict):
        boxInfos = input["data"]
        # 将ocr识别结果渲染出来
        drop_score = 0.5
        dpiScale = CanvasUtil.getDevicePixelRatio()

        for info in boxInfos:
            text = info["text"]
            box = info["box"]
            score = info["score"]
            if score is not None and score < drop_score:
                continue

            polygon = QPolygonF()
            for position in box:
                achorPos = QPointF(
                    position[0] / dpiScale, position[-1] / dpiScale
                ).toPoint()
                # finalPosition = self.drawWidget.view.mapToScene(achorPos)
                finalPosition = achorPos
                polygon.append(finalPosition)

            textItem = CanvasOcrTextItem(polygon.boundingRect(), text)
            self.drawWidget.scene.addItem(textItem)
            self.drawWidget.scene.addPolygon(
                polygon, QPen(Qt.GlobalColor.yellow), QBrush(Qt.NoBrush)
            )

    def onOcrEndSuccess(self, input):
        pluginMgr.handleEvent(GlobalEventEnum.OcrEndSuccessEvent, parent_widget=self)

        if isinstance(input, dict):
            self.onOcrEndForReturnJson(input)
        else:
            self.onOcrEndForReturnStr(input)

        if hasattr(self, "ocrThread"):
            self.ocrThread.quit()
            self.ocrThread = None

    def onOcrEndFail(self, message):
        pluginMgr.handleEvent(
            GlobalEventEnum.OcrEndFailEvent, parent_widget=self, message=message
        )

        if hasattr(self, "ocrThread"):
            self.ocrThread.quit()
            self.ocrThread = None
