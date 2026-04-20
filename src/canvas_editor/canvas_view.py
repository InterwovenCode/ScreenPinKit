# coding=utf-8
from canvas_item.canvas_util import *


class CanvasView(QGraphicsView):
    """
    注意，不应该对Scene进行缩放，否则你的橡皮擦实现需要改变思路，
    通过新建一个橡皮层来实现，因为一旦缩放之后，Sene同背景就会不匹配了
    """

    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

    def initUI(self):
        self.setMinimumSize(QSize(1, 1))
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            "background: transparent; border:0px; padding: 0px; margin: 0px;"
        )
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )

    def isCanDrag(self):
        """判断当前是否可以拖曳图元"""
        matchMode = self.dragMode()
        return matchMode | QGraphicsView.RubberBandDrag == matchMode

    def switchCanvas(self):
        if self.isCanDrag():
            self.setDragMode(self.dragMode() & ~QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)

    def wheelEvent(self, event: QWheelEvent):
        pathItem = None
        if hasattr(self.scene(), "pathItem"):
            pathItem = self.scene().pathItem
        # 如果有选中了某个图元，则滚动事件会正常往下分发
        if len(self.scene().selectedItems()) < 1 and pathItem == None:
            return
        return super().wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        if not hasattr(self, "isInit"):
            self.isInit = True
            self.originFrameSize = self.frameSize()
            # 圆角效果可能在布局完成前触发离屏绘制，此时控件仍是临时尺寸。
            # 有背景图时使用画刷变换后的图片尺寸，避免把临时尺寸作为缩放基准。
            backgroundBrush = self.scene().backgroundBrush()
            texture = backgroundBrush.texture()
            if not texture.isNull():
                imageRect = backgroundBrush.transform().mapRect(QRectF(texture.rect()))
                self.originFrameSize = imageRect.size().toSize()
            self.scene().setSceneRect(
                0, 0, self.originFrameSize.width(), self.originFrameSize.height()
            )

        currentFrameSize = self.frameSize()

        # 有个奇怪问题，会多出几个像素的位置，暂时采用修正方式来处理
        val = 4
        val = val * self.originFrameSize.width() / currentFrameSize.width()
        correctOffset = QMarginsF(0, 0, val, val)
        self.fitInView(
            self.sceneRect() - correctOffset, Qt.AspectRatioMode.IgnoreAspectRatio
        )
