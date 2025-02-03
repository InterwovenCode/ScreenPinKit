# coding=utf-8
import typing, os, threading
from datetime import datetime
from qfluentwidgets import RoundMenu, Action, StateToolTip
from base import *
from canvas_item import *
from canvas_item.canvas_util import ZoomComponent
from canvas_editor import DrawActionEnum
from common import cfg, ScreenShotIcon
from plugin import *
from .painter_interface import PainterInterface


class PinEditorWindow(PinWindow):
    def __init__(
        self,
        parent,
        screenPoint: QPoint,
        physicalSize: QSize,
        physicalPixmap: QPixmap,
        closeCallback: typing.Callable,
    ):
        super().__init__(parent, screenPoint, physicalSize, closeCallback)
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.painterWidget = PainterInterface(self, physicalPixmap)
        self.contentLayout.addWidget(self.painterWidget)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

        self.painterWidget.initDrawLayer()
        self.painterWidget.drawWidget.setEditorEnabled(False)
        self.painterWidget.showCommandBarSignal.connect(self.onShowCommandBar)

        self.setShadowColor(
            cfg.get(cfg.windowShadowStyleFocusColor),
            cfg.get(cfg.windowShadowStyleUnFocusColor),
        )

        self.initActions()

    def onShowCommandBar(self, toolbar:QWidget) -> None:
        toolbar.installEventFilter(self.shadowWindow)

    def getActiveState(self) -> bool:
        return self.isActiveWindow() or self.painterWidget.getActiveState()

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.painterWidget.currentDrawActionEnum != DrawActionEnum.DrawNone:
            return
        menu = RoundMenu(parent=self)
        actions = [
            Action(
                ScreenShotIcon.WHITE_BOARD,
                self.tr("Show toolbar"),
                triggered=self.showCommandBar,
            ),
            Action(
                ScreenShotIcon.COPY, self.tr("Copy"), triggered=self.copyToClipboard
            ),
            Action(
                ScreenShotIcon.SAVE_AS, self.tr("Save as"), triggered=self.saveToDisk
            ),
            Action(
                ScreenShotIcon.CLICK_THROUGH,
                self.tr("Mouse through"),
                triggered=self.clickThrough,
            ),
            Action(ScreenShotIcon.OCR, self.tr("OCR"), triggered=self.startOcr),
        ]
        pluginMgr.handleEvent(
            GlobalEventEnum.RegisterContextMenuEvent,
            actions=actions,
            pixmap=self.painterWidget.physicalPixmap,
            parent=self,
        )
        menu.addActions(actions)

        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def defaultFlag(self) -> None:
        super().defaultFlag()
        self.roundRadius = cfg.get(cfg.windowShadowStyleRoundRadius)

    def showCommandBar(self):
        self.painterWidget.showCommandBar()

    def clickThrough(self):
        self.painterWidget.clickThrough()

    def initActions(self):
        actions = [
            QAction(self, triggered=self.saveToDisk, shortcut="ctrl+s"),
            QAction(self, triggered=self.completeDraw, shortcut="ctrl+w"),
        ]
        self.addActions(actions)

        cfg.windowShadowStyleRoundRadius.valueChanged.connect(self.setRoundRadius)
        cfg.windowShadowStyleUnFocusColor.valueChanged.connect(self.refreshShadowColor)
        cfg.windowShadowStyleFocusColor.valueChanged.connect(self.refreshShadowColor)

    def refreshShadowColor(self, _):
        focusColor = cfg.get(cfg.windowShadowStyleFocusColor)
        unFocusColor = cfg.get(cfg.windowShadowStyleUnFocusColor)
        self.setShadowColor(focusColor, unFocusColor)

    def completeDraw(self):
        self.painterWidget.completeDraw()

    def zoomHandle(self, zoomFactor):
        finalValue = self.windowOpacity()
        if zoomFactor > 1:
            finalValue = finalValue + 0.1
        else:
            finalValue = finalValue - 0.1

        finalValue = min(max(0.2, finalValue), 1)

        self.setWindowOpacity(finalValue)

    def startOcr(self):
        self.painterWidget.startOcr()

    def onBlinkStop(self):
        self.activateWindow()

    def copyToClipboard(self):
        # 因为Windows下剪贴板不支持透明度，其会将Image里的alpha值用255直接进行填充，相关讨论可以看下面这两个链接
        # https://stackoverflow.com/questions/44177115/copying-from-and-to-clipboard-loses-image-transparency/46424800#46424800
        # https://stackoverflow.com/questions/44287407/text-erased-from-screenshot-after-using-clipboard-getimage-on-windows-10/46400011#46400011

        if cfg.get(cfg.windowShadowStyleIsCopyWithShadow):
            finalPixmap = self.grabWithShaodw()
        else:
            finalPixmap = self.grab()

        kv = {"pixmap": finalPixmap}
        pluginMgr.handleEvent(GlobalEventEnum.ImageCopyingEvent, kv=kv, parent=self)
        finalPixmap = kv["pixmap"]
        QApplication.clipboard().setPixmap(finalPixmap)

    def saveToDisk(self):
        # 获取当前时间，并格式化
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        fileName = cfg.get(cfg.imageNameFormat) % (now_str)

        tempFolder = cfg.get(cfg.cacheFolder)
        finalFolder = "./"
        if os.path.exists(tempFolder):
            finalFolder = tempFolder
        finalPath = os.path.join(finalFolder, fileName)
        savePath, _ = QFileDialog.getSaveFileName(
            self, "Save File", finalPath, "PNG(*.png)"
        )
        if savePath != None:
            if cfg.get(cfg.windowShadowStyleIsSaveWithShadow):
                finalPixmap = self.grabWithShaodw()
            else:
                finalPixmap = self.grab()

            kv = {"pixmap": finalPixmap}
            pluginMgr.handleEvent(GlobalEventEnum.ImageSavingEvent, kv=kv, parent=self)
            finalPixmap = kv["pixmap"]
            finalPixmap.save(savePath, "png")

            OsHelper.explorerFile(savePath)

    def isAllowDrag(self):
        if self.painterWidget.drawWidget != None:
            return not self.painterWidget.drawWidget.isEditorEnabled()
        return True

    def isAllowModifyOpactity(self):
        return self.isAllowDrag()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isAllowDrag():
                if int(event.modifiers()) == Qt.ControlModifier:
                    if self._lastScaleFactor == 1:
                        self._lastScaleFactor = 0.2
                    else:
                        self._lastScaleFactor = 1
                    self.__setWindowScaleFactor(self._lastScaleFactor)
                else:
                    self.close()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if (
            self.isAllowModifyOpactity()
            and int(event.modifiers()) == Qt.ControlModifier
        ):
            self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        else:
            if not self.isAllowDrag():
                return super().wheelEvent(event)

            # 缩放窗口大小
            if event.angleDelta().y() > 0:
                self._lastScaleFactor = self._lastScaleFactor + 0.1
            else:
                self._lastScaleFactor = self._lastScaleFactor - 0.1
            self._lastScaleFactor = max(0.2, min(2, self._lastScaleFactor))
            self.__setWindowScaleFactor(self._lastScaleFactor)

    def closeEvent(self, event) -> None:
        self.painterWidget.close()
        cfg.windowShadowStyleRoundRadius.valueChanged.disconnect(self.setRoundRadius)
        cfg.windowShadowStyleUnFocusColor.valueChanged.disconnect(
            self.refreshShadowColor
        )
        cfg.windowShadowStyleFocusColor.valueChanged.disconnect(self.refreshShadowColor)
        super().closeEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            if self.painterWidget.tryQuitDraw():
                self.close()
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            self.copyToClipboard()

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
            self.startOcr()

        super().keyPressEvent(event)

    def setMouseThroughState(self, isThrough: bool):
        self.painterWidget.completeDraw()
        self.painterWidget.clearFocus()
        self.focusOutEvent(
            QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.NoFocusReason)
        )
        return super().setMouseThroughState(isThrough)

    def __setWindowScaleFactor(self, newScaleFactor: float):
        """设置窗口的缩放比例"""
        scaledWidth = int(self._originSize.width() * newScaleFactor)
        scaledHeight = int(self._originSize.height() * newScaleFactor)

        self.resize(scaledWidth, scaledHeight)

    def showEvent(self, a0):
        self._originSize = self.size()
        self._lastScaleFactor = 1
        return super().showEvent(a0)
