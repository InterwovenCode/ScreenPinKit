# coding=utf-8
import os, random, time
from canvas_item import *
from canvas_item.canvas_util import CanvasUtil


class DrawActionEnum(Enum):
    DrawNone = "无操作"
    EditText = "编辑文字"
    EditBubbleText = "编辑气泡文本"
    UsePen = "使用画笔"
    UseEraser = "使用橡皮擦"
    UseEraserRectItem = "使用橡皮框"
    UseShadowEraserRectItem = "阴影橡皮框"
    UseShadowEraserEllipseItem = "阴影橡皮圈"
    UseMarkerPen = "使用记号笔"
    UseNumberMarker = "使用数字标记"
    PasteSvg = "粘贴图案"

    DrawShape = "绘制形状"
    DrawArrow = "绘制箭头"
    DrawLineStrip = "绘制折线"
    SelectItem = "选择对象"
    UseEffectTool = "特效工具"


class DrawActionInfo(QObject):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)
        self.map = {}
        self.initLocale()

    def initLocale(self):
        self.map[DrawActionEnum.DrawNone] = self.tr("DrawNone")
        self.map[DrawActionEnum.EditText] = self.tr("EditText")
        self.map[DrawActionEnum.EditBubbleText] = self.tr("EditBubbleText")
        self.map[DrawActionEnum.UsePen] = self.tr("UsePencil")
        self.map[DrawActionEnum.UseEraser] = self.tr("UseEraser")
        self.map[DrawActionEnum.UseEraserRectItem] = self.tr("UseEraserRectItem")
        self.map[DrawActionEnum.UseShadowEraserRectItem] = self.tr(
            "UseShadowEraserRectItem"
        )
        self.map[DrawActionEnum.UseShadowEraserEllipseItem] = self.tr(
            "UseShadowEraserEllipseItem"
        )
        self.map[DrawActionEnum.UseMarkerPen] = self.tr("UseMarkerPen")
        self.map[DrawActionEnum.UseNumberMarker] = self.tr("UseNumberMarker")
        self.map[DrawActionEnum.PasteSvg] = self.tr("PasteSvg")
        self.map[DrawActionEnum.DrawShape] = self.tr("DrawShape")
        self.map[DrawActionEnum.DrawArrow] = self.tr("DrawArrow")
        self.map[DrawActionEnum.DrawLineStrip] = self.tr("DrawLineStrip")
        self.map[DrawActionEnum.SelectItem] = self.tr("SelectItem")
        self.map[DrawActionEnum.UseEffectTool] = self.tr("UseEffectTool")

    def getInfo(self, drawActionEnum: DrawActionEnum):
        if drawActionEnum in self.map:
            return self.map[drawActionEnum]
        else:
            return self.tr("UnknownTool")


class SceneUserNotifyEnum(Enum):
    StartDrawedEvent = "已开始绘制"
    EndDrawedEvent = "已结束绘制"
    SelectItemChangedEvent = "选中图元已改变"
    SelectNothing = "啥也没选中"


class CanvasScene(QGraphicsScene):
    itemMovedSignal = pyqtSignal(QGraphicsItem, QPointF, QPointF)
    itemDeleteSignal = pyqtSignal(QGraphicsScene, QGraphicsItem)
    itemDeleteAllSignal = pyqtSignal(QGraphicsScene, list)
    itemAddSignal = pyqtSignal(QGraphicsScene, QGraphicsItem)
    itemRotatedSignal = pyqtSignal(QGraphicsItem, float, float)
    itemResizedSignal = pyqtSignal(QGraphicsItem, tuple, tuple)

    def __init__(self, parent=None, backgroundBrush: QBrush = None):
        super().__init__(parent)
        self._currentDrawActionEnum = DrawActionEnum.DrawNone
        self._isLockedTool = True

        self.currentItem = None
        self.lastAddItem = None
        self.bgBrush = backgroundBrush

        self.itemList: list = []
        self._itemNotifyCallBack = None
        self._lastSelectedItem = None

        self.selectionChanged.connect(self.selectionChangedHandle)
        if self.bgBrush != None:
            self.setBackgroundBrush(self.bgBrush)

    def selectionChangedHandle(self):
        selectItem = None
        if len(self.selectedItems()) == 0:
            return

        selectItem = self.selectedItems()[0]
        if CanvasUtil.isRoiItem(selectItem):
            selectItem = selectItem.parentItem()

        if self._itemNotifyCallBack != None:
            if (
                self.currentDrawActionEnum == DrawActionEnum.SelectItem
                and selectItem == None
            ):
                self._itemNotifyCallBack(SceneUserNotifyEnum.SelectNothing, selectItem)
            else:
                self._itemNotifyCallBack(
                    SceneUserNotifyEnum.SelectItemChangedEvent, selectItem
                )
        self._lastSelectedItem = selectItem

    def initNodes(self):
        targetRect = QRectF(QPointF(0, 0), QSizeF(100, 100))
        arrowStyleMap = {
            "arrowLength": 32.0,
            "arrowAngle": 0.5,
            "arrowBodyLength": 18,
            "arrowBodyAngle": 0.2,
            "arrowBrush": QBrush(QColor(255, 0, 0, 100)),
            "arrowPen": QPen(QColor(255, 0, 0), 2, Qt.SolidLine),
        }
        # finalPoints = CanvasUtil.buildArrowPath(QPainterPath(), QPolygonF([targetRect.topLeft(), targetRect.bottomRight()]), arrowStyleMap)
        finalPoints = CanvasUtil.buildStarPath(
            QPainterPath(), QPolygonF([targetRect.topLeft(), targetRect.bottomRight()])
        )
        pathItem1 = CanvasCommonPathItem(None, False)
        pathItem1.polygon = QPolygonF(finalPoints)
        self.__startDraw(pathItem1)
        pathItem1.completeDraw()

        pathItem2 = CanvasCommonPathItem(None, True)
        pathItem2.polygon = QPolygonF(finalPoints)
        self.__startDraw(pathItem2)
        pathItem2.completeDraw()
        pathItem2.moveBy(300, 0)

        pathItem3 = CanvasEditablePath(None, False)
        pathItem3.addPoint(QPointF(-100, -100), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-30, -50), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-200, -280), Qt.SizeAllCursor)
        pathItem3.update()
        self.__startDraw(pathItem3)

    def setNofityEvent(self, callBack: callable = None):
        self._itemNotifyCallBack = callBack

    @property
    def currentDrawActionEnum(self):
        return self._currentDrawActionEnum

    @currentDrawActionEnum.setter
    def currentDrawActionEnum(self, value):
        if self._currentDrawActionEnum == value:
            return
        self._currentDrawActionEnum = value
        self.setEditableState(value == DrawActionEnum.SelectItem)

    @property
    def isLockedTool(self):
        return self._isLockedTool

    @isLockedTool.setter
    def isLockedTool(self, value):
        self._isLockedTool = value

    def __startDraw(self, item: QGraphicsObject):
        self.addItem(item)
        if isinstance(item, CanvasTextItem):
            item.setEditableState(True)
        else:
            item.setEditableState(False)
        if self._itemNotifyCallBack != None:
            self._itemNotifyCallBack(SceneUserNotifyEnum.StartDrawedEvent, item)

    def forceCompleteDraw(self):
        if self.currentItem != None:
            isOk = True
            # 由于折线图元绘制过程中强制退出时，需要回收一个预览操作点，需要额外处理
            if isinstance(self.currentItem, CanvasLineStripItem):
                if self.currentItem.polygon.count() > 2:
                    self.currentItem.polygon.remove(
                        self.currentItem.polygon.count() - 1
                    )
                else:
                    isOk = False
            self.__completeDraw(self.currentItem, isOk)
        self.lastAddItem = None

    def tryCloseColorPicker(self):
        for item0 in self.itemList:
            item:CanvasCommonPathItem = item0
            item.completeDraw()

    def __completeDraw(self, item: CanvasCommonPathItem, isOk: bool = True):
        if isOk:
            item.completeDraw()
            self.itemAddSignal.emit(self, item)
            self.lastAddItem = item

        self.currentItem = None

        if self._itemNotifyCallBack != None:
            if isOk:
                self._itemNotifyCallBack(SceneUserNotifyEnum.EndDrawedEvent, item)
            else:
                self._itemNotifyCallBack(SceneUserNotifyEnum.EndDrawedEvent, None)

        if isOk and hasattr(item, "transformComponent"):
            item.transformComponent.movedSignal.connect(self.itemMovedSignal)
            item.transformComponent.rotatedSignal.connect(self.itemRotatedSignal)
            item.transformComponent.resizedSignal.connect(self.itemResizedSignal)

    def clearDraw(self):
        self.itemDeleteAllSignal.emit(self, self.itemList)

        self.currentItem = None
        self.lastAddItem = None
        self.itemList = []

    def canUndo(self):
        return self.currentItem == None

    def captureCurrentScenePixmap(self) -> QPixmap:
        """捕获当前场景快照"""
        view = self.views()[0]
        shotGrab = view.grab()
        devicePixelRatio = self.bgBrush.texture().devicePixelRatio()
        finalSize = QSizeF(qRound(self.sceneRect().width() * devicePixelRatio), qRound(self.sceneRect().height() * devicePixelRatio))

        shotGrab = shotGrab.scaled(
            finalSize.width(), finalSize.height(), Qt.KeepAspectRatio
        )
        return shotGrab

    def switchLockState(self):
        self.isLockedTool = not self.isLockedTool

    def setEditableState(self, isEditable: bool):
        for item0 in self.itemList:
            item: CanvasCommonPathItem = item0
            item.setEditableState(isEditable)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent):
        selectedItems = self.selectedItems()
        if len(selectedItems) > 0:
            selectItem = selectedItems[0]
            selectItem.wheelEvent(event)
            event.accept()
            return
        if isinstance(self.currentItem, CanvasLineStripItem):
            event.accept()
            return
        return super().wheelEvent(event)

    # 参考https://excalidraw.com/上面的操作方式
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        view: QGraphicsView = self.views()[0]
        targetPos = event.scenePos()
        item = self.itemAt(event.scenePos(), view.transform())

        isSkip = False
        if self.currentDrawActionEnum in [
            DrawActionEnum.DrawNone,
            DrawActionEnum.SelectItem,
        ]:
            isSkip = True
        if item == self.lastAddItem and item != None:
            isSkip = True
        if item != None and CanvasUtil.isRoiItem(item):
            isSkip = True
        if isinstance(item, CanvasTextItem) and item.isSelected():
            return super().mousePressEvent(event)

        if isSkip and not self.isLockedTool:
            return super().mousePressEvent(event)
        else:
            if event.button() == Qt.LeftButton:
                if self.currentItem == None:
                    if self.currentDrawActionEnum == DrawActionEnum.EditText:
                        self.currentItem = CanvasTextItem()
                        self.currentItem.switchEditableBox()
                        self.__startDraw(self.currentItem)
                        targetPos.setX(
                            targetPos.x() - self.currentItem.boundingRect().width() / 2
                        )
                        targetPos.setY(
                            targetPos.y() - self.currentItem.boundingRect().height() / 2
                        )
                        self.currentItem.setPos(targetPos)
                        self.__completeDraw(self.currentItem)
                    if self.currentDrawActionEnum == DrawActionEnum.EditBubbleText:
                        self.currentItem = CanvasBubbleTextItem()
                        self.currentItem.switchEditableBox()
                        self.__startDraw(self.currentItem)
                        targetPos.setX(
                            targetPos.x() - self.currentItem.boundingRect().width() / 2
                        )
                        targetPos.setY(
                            targetPos.y() - self.currentItem.boundingRect().height() / 2
                        )
                        self.currentItem.setPos(targetPos)
                        self.__completeDraw(self.currentItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseNumberMarker:
                        # 如果当前位置下已经存在一个数字标记图元，则不再创建新的
                        for item0 in self.itemList:
                            if isinstance(item0, CanvasNumberMarkerItem):
                                if item0.sceneBoundingRect().contains(event.scenePos()):
                                    return super().mousePressEvent(event)

                        self.currentItem = CanvasNumberMarkerItem(QRectF(0, 0, 20, 20))
                        self.__startDraw(self.currentItem)
                        targetPos.setX(
                            targetPos.x() - self.currentItem.boundingRect().width() / 2
                        )
                        targetPos.setY(
                            targetPos.y() - self.currentItem.boundingRect().height() / 2
                        )
                        self.currentItem.setPos(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.PasteSvg:
                        folderPath = os.path.join(
                            os.getcwd(), "canvas_item/demos/resources"
                        )

                        def getSvgFiles(folderPath):
                            result = []
                            for filePath in os.listdir(folderPath):
                                if filePath.endswith(".svg"):
                                    result.append(os.path.join(folderPath, filePath))
                            return result

                        svgPaths = getSvgFiles(folderPath)
                        index = random.randint(0, len(svgPaths) - 1)
                        svgPath = svgPaths[index]
                        if index % 2 == 0:
                            self.currentItem = CanvasSvgItem(QRectF(), svgPath)
                        else:
                            self.currentItem = CanvasSvgItem(
                                QRectF(0, 0, 100, 100), svgPath
                            )

                        self.__startDraw(self.currentItem)
                        targetPos.setX(
                            targetPos.x() - self.currentItem.boundingRect().width() / 2
                        )
                        targetPos.setY(
                            targetPos.y() - self.currentItem.boundingRect().height() / 2
                        )
                        self.currentItem.setPos(targetPos)
                        self.__completeDraw(self.currentItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.UsePen:
                        self.currentItem = CanvasPenItem()
                        self.__startDraw(self.currentItem)
                        self.currentItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEraser:
                        if self.currentItem == None:
                            if self.bgBrush != None:
                                eraseBrush = self.bgBrush
                                erasePen = QPen(eraseBrush, 10)
                            else:
                                erasePen = QPen(Qt.GlobalColor.blue)
                            self.currentItem = CanvasEraserItem(erasePen)
                            self.__startDraw(self.currentItem)
                            self.currentItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEraserRectItem:
                        if self.currentItem == None:
                            if self.bgBrush != None:
                                self.currentItem = CanvasEraserRectItem(self.bgBrush)
                                self.__startDraw(self.currentItem)
                                self.currentItem.polygon.append(targetPos)
                                self.currentItem.polygon.append(targetPos)
                    elif (
                        self.currentDrawActionEnum
                        == DrawActionEnum.UseShadowEraserEllipseItem
                    ):
                        if self.currentItem == None:
                            if self.bgBrush != None:
                                self.currentItem = CanvasShadowEraserEllipseItem(
                                    self.bgBrush
                                )
                                self.__startDraw(self.currentItem)
                                self.currentItem.polygon.append(targetPos)
                                self.currentItem.polygon.append(targetPos)
                    elif (
                        self.currentDrawActionEnum
                        == DrawActionEnum.UseShadowEraserRectItem
                    ):
                        if self.currentItem == None:
                            if self.bgBrush != None:
                                self.currentItem = CanvasShadowEraserRectItem(
                                    self.bgBrush
                                )
                                self.__startDraw(self.currentItem)
                                self.currentItem.polygon.append(targetPos)
                                self.currentItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEffectTool:
                        if self.currentItem == None:
                            lastPixmap = self.captureCurrentScenePixmap()
                            self.currentItem = CanvasEffectRectItem(lastPixmap)
                            self.__startDraw(self.currentItem)
                            self.currentItem.polygon.append(targetPos)
                            self.currentItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                        if self.currentItem == None:
                            self.currentItem = CanvasArrowItem()
                            self.__startDraw(self.currentItem)
                            self.currentItem.polygon.append(targetPos)
                            self.currentItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:
                        if self.currentItem == None:
                            self.currentItem = CanvasMarkerPen()
                            self.__startDraw(self.currentItem)
                            self.currentItem.polygon.append(targetPos)
                            self.currentItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawShape:
                        if self.currentItem == None:
                            self.currentItem = CanvasShapeItem()
                            self.__startDraw(self.currentItem)
                            self.currentItem.polygon.append(targetPos)
                            self.currentItem.polygon.append(targetPos)

                if self.currentDrawActionEnum == DrawActionEnum.DrawLineStrip:
                    if self.currentItem == None:
                        self.currentItem = CanvasLineStripItem()
                        self.__startDraw(self.currentItem)
                        self.currentItem.polygon.append(targetPos)
                        self.currentItem.polygon.append(targetPos)
                    else:
                        self.currentItem.polygon.append(targetPos)
                        self.currentItem.update()
            if event.button() == Qt.RightButton:
                if (
                    self.currentItem == None
                    and self.currentDrawActionEnum == DrawActionEnum.UseEffectTool
                ):
                    lastPixmap = self.captureCurrentScenePixmap()
                    self.currentItem = CanvasEffectRectItem(lastPixmap)
                    self.__startDraw(self.currentItem)
                    sceneRect = QRect(QPoint(0, 0), lastPixmap.size())
                    self.currentItem.polygon.append(sceneRect.topLeft())
                    self.currentItem.polygon.append(sceneRect.bottomRight())
                    self.__completeDraw(self.currentItem)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            not self.currentDrawActionEnum
            in [DrawActionEnum.DrawNone, DrawActionEnum.SelectItem]
            and self.currentItem != None
        ):
            targetPos = event.scenePos()

            if self.currentDrawActionEnum in [
                    DrawActionEnum.DrawShape, 
                    DrawActionEnum.UseShadowEraserRectItem,
                    DrawActionEnum.UseShadowEraserEllipseItem,
                ]:
                self.currentItem.polygon.replace(
                    self.currentItem.polygon.count() - 1, targetPos
                )
                isForceEqual = (
                    int(event.modifiers()) == Qt.KeyboardModifier.ShiftModifier
                )
                if isForceEqual:
                    self.currentItem.forceSquare()
                self.currentItem.update()
            elif self.currentDrawActionEnum in [
                DrawActionEnum.DrawLineStrip,
                DrawActionEnum.DrawArrow,
                DrawActionEnum.UseMarkerPen,
                DrawActionEnum.UseEraserRectItem,
                DrawActionEnum.UseShadowEraserRectItem,
                DrawActionEnum.UseShadowEraserEllipseItem,
                DrawActionEnum.UseEffectTool,
            ]:
                self.currentItem.polygon.replace(
                    self.currentItem.polygon.count() - 1, targetPos
                )
                self.currentItem.update()
            elif self.currentDrawActionEnum in [
                DrawActionEnum.UsePen,
                DrawActionEnum.UseEraser,
            ]:
                now = time.time()
                # 控制拾取点的间隔
                if not hasattr(self, "pickupLastTime"):
                    self.pickupLastTime = now
                if now - self.pickupLastTime > 0.02:
                    self.pickupLastTime = now
                    self.currentItem.polygon.append(targetPos)
                    self.currentItem.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (
            self.currentDrawActionEnum != DrawActionEnum.DrawNone
            and self.currentItem != None
        ):
            if (
                self.currentDrawActionEnum in [DrawActionEnum.DrawLineStrip]
                and event.button() == Qt.RightButton
            ):
                if event.button() == Qt.RightButton and self.currentItem != None:
                    isOk = False
                    if self.currentItem.polygon.count() > 2:
                        self.currentItem.polygon.remove(
                            self.currentItem.polygon.count() - 1
                        )
                        isOk = True
                    self.__completeDraw(self.currentItem, isOk)
            elif self.currentDrawActionEnum in [
                DrawActionEnum.UsePen,
                DrawActionEnum.UseEraser,
            ]:
                if event.button() == Qt.LeftButton:
                    self.__completeDraw(self.currentItem)
            elif self.currentDrawActionEnum in [DrawActionEnum.UseNumberMarker]:
                if event.button() == Qt.LeftButton:
                    super().mouseReleaseEvent(event)
                    self.currentItem.setSelected(False)
                    self.__completeDraw(self.currentItem)
            elif self.currentDrawActionEnum in [
                DrawActionEnum.DrawArrow,
                DrawActionEnum.UseMarkerPen,
                DrawActionEnum.UseEraserRectItem,
                DrawActionEnum.UseShadowEraserRectItem,
                DrawActionEnum.UseShadowEraserEllipseItem,
                DrawActionEnum.DrawShape,
                DrawActionEnum.UseEffectTool,
            ]:
                if event.button() == Qt.LeftButton:
                    isOk = False
                    if self.currentItem.polygon.at(0) != self.currentItem.polygon.at(1):
                        isOk = True
                    self.__completeDraw(self.currentItem, isOk)

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace]:
            for item in self.selectedItems():
                finalItem = item
                # 需要兼容边缘操作点和ROI操作点
                while (
                    not hasattr(finalItem, "completeDraw")
                    and finalItem.parentItem() != None
                ):
                    finalItem = finalItem.parentItem()

                if hasattr(finalItem, "completeDraw"):
                    if (
                        not isinstance(finalItem, CanvasTextItem)
                        or not finalItem.isCanEditable()
                    ):
                        self.itemDeleteSignal.emit(self, finalItem)

                        if self._itemNotifyCallBack != None:
                            self._itemNotifyCallBack(
                                SceneUserNotifyEnum.SelectNothing, None
                            )

                        break

        elif event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]:
            selectedItems = self.selectedItems()
            if len(selectedItems) > 0:
                selectItem = selectedItems[0]
                if isinstance(selectItem, CanvasTextItem):
                    if selectItem.isCanEditable():
                        return super().keyPressEvent(event)
                if CanvasUtil.isRoiItem(selectItem):
                    selectItem = selectItem.parentItem()
                if event.key() == Qt.Key_Left:
                    offset = QPointF(-1, 0)
                elif event.key() == Qt.Key_Right:
                    offset = QPointF(1, 0)
                elif event.key() == Qt.Key_Up:
                    offset = QPointF(0, -1)
                elif event.key() == Qt.Key_Down:
                    offset = QPointF(0, 1)

                selectItem.setPos(selectItem.pos() + offset)
            return
        return super().keyPressEvent(event)