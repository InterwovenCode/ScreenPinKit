# coding:utf-8
# @note 基于teaching_tip.py改造而来
from enum import Enum

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *

class BubbleTipTailPosition(Enum):
    """Bubble tip tail position"""

    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3
    TOP_LEFT = 4
    TOP_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_RIGHT = 7
    LEFT_TOP = 8
    LEFT_BOTTOM = 9
    RIGHT_TOP = 10
    RIGHT_BOTTOM = 11
    NONE = 12
    AUTO = 13
    TOP_LEFT_AUTO = 14
    BOTTOM_LEFT_AUTO = 15


class BubbleTipContent(QWidget):
    """Bubble tip content"""

    PopupStyle = 1 << 0  # 弹出样式
    ShowOrientStyle = 1 << 1  # 显示方向标记样式

    def __init__(
        self,
        view: FlyoutViewBase,
        tailPosition=BubbleTipTailPosition.BOTTOM,
        showStyle: int = 0,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.manager: BubbleTipManager = BubbleTipManager.make(tailPosition)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = view
        self.showStyle = showStyle
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

    def setView(self, view: QWidget):
        self.hBoxLayout.removeWidget(self.view)
        self.view.deleteLater()
        self.view = view
        self.hBoxLayout.addWidget(view)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        painter.setBrush(QColor(40, 40, 40) if isDarkTheme() else QColor(248, 248, 248))
        painter.setPen(QColor(23, 23, 23) if isDarkTheme() else QColor(195, 195, 195))

        if self.isShowOrientStyle():
            self.manager.draw(self, painter)

    def isPopupStyle(self) -> bool:
        return self.showStyle | BubbleTipContent.PopupStyle == self.showStyle

    def isShowOrientStyle(self) -> bool:
        return self.showStyle | BubbleTipContent.ShowOrientStyle == self.showStyle


class BubbleTip(QWidget):
    """Bubble tip"""

    def __init__(
        self,
        view: FlyoutViewBase,
        target: QWidget,
        duration=1000,
        tailPosition=BubbleTipTailPosition.BOTTOM,
        showStyle: int = 0,
        parent=None,
    ):
        """
        Parameters
        ----------
        target: QWidget
            the target widget to show tip

        view: FlyoutViewBase
            teaching tip view

        duration: int
            the time for teaching tip to display in milliseconds. If duration is less than zero,
            teaching tip will never disappear.

        tailPosition: BubbleTipTailPosition
            the position of bubble tail

        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.target = target
        self.duration = duration
        self.manager: BubbleTipManager = BubbleTipManager.make(tailPosition)

        self.hBoxLayout = QHBoxLayout(self)
        self.opacityAni = QPropertyAnimation(self, b"windowOpacity", self)
        self.bubble = BubbleTipContent(
            view, tailPosition, showStyle, self
        )

        self.hBoxLayout.setContentsMargins(15, 4, 15, 0)
        self.hBoxLayout.addWidget(self.bubble)
        self.setShadowEffect()

        # set style
        self.setAttribute(Qt.WA_TranslucentBackground)

        if self.bubble.isPopupStyle():
            self.setWindowFlags(
                Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
            )
        else:
            self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)

        if parent and parent.window():
            parent.window().installEventFilter(self)

    def setShadowEffect(self, blurRadius=35, offset=(0, 8)):
        """add shadow to dialog"""
        color = QColor(0, 0, 0, 80 if isDarkTheme() else 30)
        self.shadowEffect = QGraphicsDropShadowEffect(self.bubble)
        self.shadowEffect.setBlurRadius(blurRadius)
        self.shadowEffect.setOffset(*offset)
        self.shadowEffect.setColor(color)
        self.bubble.setGraphicsEffect(None)
        self.bubble.setGraphicsEffect(self.shadowEffect)

    def _fadeOut(self):
        """fade out"""
        self.opacityAni.setDuration(167)
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.finished.connect(self.close)
        self.opacityAni.start()

    def showEvent(self, e):
        if self.duration >= 0:
            QTimer.singleShot(self.duration, self._fadeOut)

        self.move(self.manager.position(self))
        self.opacityAni.setDuration(167)
        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.start()
        super().showEvent(e)

    def eventFilter(self, obj, e: QEvent):
        if self.parent() and obj is self.parent().window():
            if e.type() in [QEvent.Resize, QEvent.WindowStateChange, QEvent.Move]:
                self.move(self.manager.position(self))

        return super().eventFilter(obj, e)

    def addWidget(self, widget: QWidget, stretch=0, align=Qt.AlignLeft):
        """add widget to teaching tip"""
        self.view.addSpacing(8)
        self.view.addWidget(widget, stretch, align)

    @property
    def view(self):
        return self.bubble.view

    def setView(self, view):
        self.bubble.setView(view)

    @classmethod
    def make(
        cls,
        view: FlyoutViewBase,
        target: QWidget,
        duration=1000,
        tailPosition=BubbleTipTailPosition.BOTTOM,
        showStyle: int = 0,
        parent=None,
    ):
        """
        Parameters
        ----------
        view: FlyoutViewBase
            teaching tip view

        target: QWidget
            the target widget to show tip

        duration: int
            the time for teaching tip to display in milliseconds. If duration is less than zero,
            teaching tip will never disappear.

        tailPosition: BubbleTipTailPosition
            the position of bubble tail

        parent: QWidget
            parent widget
        """
        w = cls(view, target, duration, tailPosition, showStyle, parent)
        w.show()
        return w


class BubbleTipManager(QObject):
    """Bubble tip manager"""

    def __init__(self):
        super().__init__()

    def position(self, tip: BubbleTip) -> QPoint:
        pos = self._pos(tip)
        x, y = pos.x(), pos.y()

        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        x = min(
            max(-2, x) if QCursor().pos().x() >= 0 else x,
            rect.width() - tip.width() - 4,
        )
        y = min(max(-2, y), rect.height() - tip.height() - 4)

        return QPoint(x, y)

    def draw(self, tip: BubbleTipContent, painter: QPainter):
        """draw the shape of bubble"""
        rect = tip.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 8, 8)

    def _pos(self, tip: BubbleTip):
        """return the poisition of tip"""
        return tip.pos()

    def isCorrectedBound(self):
        return False

    @staticmethod
    def make(position: BubbleTipTailPosition):
        """mask teaching tip manager according to the display position"""
        managers = {
            BubbleTipTailPosition.AUTO: AutoTailBubbleTipManager,
            BubbleTipTailPosition.TOP_LEFT_AUTO: TopLeftAutoTailBubbleTipManager,
            BubbleTipTailPosition.BOTTOM_LEFT_AUTO: BottomLeftAutoTailBubbleTipManager,
            BubbleTipTailPosition.BOTTOM: BottomTailBubbleTipManager,
        }

        if position not in managers:
            raise ValueError(f"`{position}` is an invalid teaching tip position.")

        return managers[position]()


class TopTailBubbleTipManager(BubbleTipManager):
    """Top tail teaching tip manager"""

    def __init__(self):
        super().__init__()
        self._isCorrectedBound = False

    def draw(self, tip: BubbleTipContent, painter):
        w, h = tip.width(), tip.height()
        pt = tip.hBoxLayout.contentsMargins().top()

        path = QPainterPath()
        path.addRoundedRect(1, pt, w - 2, h - pt - 1, 8, 8)
        path.addPolygon(
            QPolygonF(
                [QPointF(w / 2 - 7, pt), QPointF(w / 2, 1), QPointF(w / 2 + 7, pt)]
            )
        )

        painter.drawPath(path.simplified())

    def _pos(self, tip: BubbleTip):
        target = tip.target
        pos = target.mapToGlobal(QPoint(0, target.height()))
        x = pos.x() + target.width() // 2 - tip.sizeHint().width() // 2
        y = pos.y() - tip.layout().contentsMargins().top()
        return QPoint(x, y)

    def tryCorrectBound(self, tip: BubbleTip):
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        maxPosY = rect.height() - tip.height() - 4

        target = tip.target

        pos = target.mapToGlobal(QPoint(0, target.height()))
        y = pos.y()

        self._isCorrectedBound = y > maxPosY
        if self._isCorrectedBound:
            pos = target.mapToGlobal(QPoint())
            y = (
                pos.y()
                - tip.sizeHint().height()
                + tip.layout().contentsMargins().bottom()
                - tip.layout().contentsMargins().top()
            )

        return y

    def isCorrectedBound(self):
        return self._isCorrectedBound


class BottomTailBubbleTipManager(BubbleTipManager):
    """Bottom tail teaching tip manager"""

    def __init__(self):
        super().__init__()
        self._isCorrectedBound = False

    def draw(self, tip: BubbleTipContent, painter):
        w, h = tip.width(), tip.height()
        pb = tip.hBoxLayout.contentsMargins().bottom()

        path = QPainterPath()
        path.addRoundedRect(1, 1, w - 2, h - pb - 1, 8, 8)
        path.addPolygon(
            QPolygonF(
                [
                    QPointF(w / 2 - 7, h - pb),
                    QPointF(w / 2, h - 1),
                    QPointF(w / 2 + 7, h - pb),
                ]
            )
        )

        painter.drawPath(path.simplified())

    def _pos(self, tip: BubbleTip):
        target = tip.target
        pos = target.mapToGlobal(QPoint())
        x = pos.x() + target.width() // 2 - tip.sizeHint().width() // 2
        y = pos.y() - tip.sizeHint().height() + tip.layout().contentsMargins().bottom()
        return QPoint(x, y)

    def tryCorrectBound(self, tip: BubbleTip):
        minPosY = 0

        target = tip.target

        pos = target.mapToGlobal(QPoint())
        y = (
            pos.y()
            - tip.sizeHint().height()
            + tip.layout().contentsMargins().bottom()
            - tip.layout().contentsMargins().top()
        )

        self._isCorrectedBound = y < minPosY
        if self._isCorrectedBound:
            pos = target.mapToGlobal(QPoint(0, target.height()))
            y = pos.y()
        return y

    def isCorrectedBound(self):
        return self._isCorrectedBound

class TopLeftAutoTailBubbleTipManager(TopTailBubbleTipManager):
    """Top left tail teaching tip manager"""

    def draw(self, tip: BubbleTipContent, painter: QPainter):
        w, h = tip.width(), tip.height()
        pt = tip.hBoxLayout.contentsMargins().top()

        path = QPainterPath()
        path.addRoundedRect(1, pt, w - 2, h - pt - 1, 8, 8)
        path.addPolygon(QPolygonF([QPointF(20, pt), QPointF(27, 1), QPointF(34, pt)]))

        painter.drawPath(path.simplified())

    def _pos(self, tip: BubbleTip):
        target = tip.target
        pos = target.mapToGlobal(QPoint(0, target.height()))
        x = pos.x() - tip.layout().contentsMargins().left()
        y = self.tryCorrectBound(tip)
        return QPoint(x, y)

class AutoTailBubbleTipManager(TopTailBubbleTipManager):
    """Auto tail teaching tip manager"""

    def draw(self, tip: BubbleTipContent, painter: QPainter):
        w, h = tip.width(), tip.height()
        pt = tip.hBoxLayout.contentsMargins().top()

        path = QPainterPath()
        path.addRoundedRect(1, pt, w - 2, h - pt - 1, 8, 8)
        path.addPolygon(
            QPolygonF([QPointF(w - 20, pt), QPointF(w - 27, 1), QPointF(w - 34, pt)])
        )

        painter.drawPath(path.simplified())

    def _pos(self, tip: BubbleTip):
        # 优先放在下方，如果底端空间不足再纠正到上方
        point = super()._pos(tip)
        x = point.x()
        y = self.tryCorrectBound(tip)

        return QPoint(x, y)


class BottomLeftAutoTailBubbleTipManager(BottomTailBubbleTipManager):
    """Bottom left tail teaching tip manager"""

    def draw(self, tip: BubbleTipContent, painter: QPainter):
        w, h = tip.width(), tip.height()
        pb = tip.hBoxLayout.contentsMargins().bottom()

        path = QPainterPath()
        path.addRoundedRect(1, 1, w - 2, h - pb - 1, 8, 8)
        path.addPolygon(
            QPolygonF([QPointF(20, h - pb), QPointF(27, h - 1), QPointF(34, h - pb)])
        )

        painter.drawPath(path.simplified())

    def _pos(self, tip: BubbleTip):
        target = tip.target
        pos = target.mapToGlobal(QPoint())
        x = pos.x() - tip.layout().contentsMargins().left()
        y = self.tryCorrectBound(tip)
        return QPoint(x, y)