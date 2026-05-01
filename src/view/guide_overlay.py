# coding=utf-8
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QRegion
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def pretty_hotkey(value: str) -> str:
    """把配置里的 f7 / alt+f 显示成 F7 / Alt+F。"""
    if not value:
        return ""
    names = {
        "ctrl": "Ctrl",
        "alt": "Alt",
        "shift": "Shift",
        "meta": "Win",
        "super": "Win",
    }
    parts = []
    for part in value.split("+"):
        key = part.strip()
        if not key:
            continue
        mapped = names.get(key.lower())
        if mapped:
            parts.append(mapped)
        elif len(key) <= 3:
            parts.append(key.upper())
        else:
            parts.append(key.capitalize())
    return "+".join(parts)


def place_bubble(anchor: QRect, bubble: QSize, screen: QRect) -> QPoint:
    """把说明气泡放在目标区域外侧，并限制在同一块屏幕里。"""
    margin = 12
    gap = 14
    width = bubble.width()
    height = bubble.height()
    screen_right = screen.x() + screen.width()
    screen_bottom = screen.y() + screen.height()

    def clamp(x, y):
        x = max(screen.x() + margin, min(int(x), screen_right - width - margin))
        y = max(screen.y() + margin, min(int(y), screen_bottom - height - margin))
        return QPoint(x, y)

    if (
        anchor.isNull()
        or anchor.isEmpty()
        or not anchor.isValid()
        or width <= 0
        or height <= 0
    ):
        return clamp(screen.center().x() - width // 2, screen.y() + 48)

    below = anchor.y() + anchor.height() + gap
    if below + height <= screen_bottom - margin:
        return clamp(anchor.x(), below)

    above = anchor.y() - gap - height
    if above >= screen.y() + margin:
        return clamp(anchor.x(), above)

    side_x = anchor.x() + anchor.width() + gap
    if side_x + width > screen_right - margin:
        side_x = anchor.x() - gap - width
    return clamp(side_x, anchor.y())


class _Dot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._on = False
        self.setFixedSize(8, 8)

    def set_on(self, on: bool):
        self._on = on
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#009faa" if self._on else "#d0d7de"))
        painter.drawEllipse(self.rect().adjusted(0, 0, -1, -1))
        painter.end()


class GuideShade(QWidget):
    """盖住整个桌面的暗层。挖孔区域不在窗口形状里，鼠标会落到下面的真实窗口。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hole = QRect()
        self._focus_target = None
        self._scene_ready = False
        self._masked = False
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAutoFillBackground(False)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setWindowTitle("")

    def set_scene(self, hole: QRect, focus_target):
        self._focus_target = focus_target
        hole = QRect(hole) if hole is not None else QRect()
        if self._scene_ready and hole == self._hole:
            return
        self._hole = hole
        self._fit_screens()
        self._apply_mask()
        self._scene_ready = True
        self.update()

    def _fit_screens(self):
        geo = QRect()
        for screen in QApplication.screens():
            geo = geo.united(screen.geometry())
        if geo.isNull():
            desktop = QApplication.desktop()
            if desktop is not None:
                geo = desktop.geometry()
        if not geo.isNull() and geo != self.geometry():
            self.setGeometry(geo)

    def _local_inner(self) -> QRect:
        if self._hole.isNull() or self._hole.isEmpty() or not self._hole.isValid():
            return QRect()
        local = QRect(self.mapFromGlobal(self._hole.topLeft()), self._hole.size())
        return local.adjusted(-8, -8, 8, 8)

    def _apply_mask(self):
        inner = self._local_inner()
        if inner.width() < 4 or inner.height() < 4:
            if self._masked:
                self.clearMask()
                self._masked = False
            return
        region = QRegion(self.rect()).subtracted(QRegion(inner))
        self.setMask(region)
        self._masked = True

    def mousePressEvent(self, event):
        event.accept()
        target = self._focus_target() if self._focus_target else None
        if target is not None:
            target.activateWindow()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        inner = self._local_inner()
        if inner.width() > 4 and inner.height() > 4:
            pen = QPen(QColor("#009faa"))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(inner.adjusted(1, 1, -2, -2), 8, 8)
        painter.end()


class GuideBubble(QWidget):
    nextClicked = pyqtSignal()
    prevClicked = pyqtSignal()
    skipClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dots = []
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setWindowTitle("")
        self.setFixedWidth(380)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self.card = QFrame(self)
        self.card.setObjectName("guideCard")
        root.addWidget(self.card)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        self.metaLabel = QLabel(self.card)
        self.metaLabel.setObjectName("guideMeta")
        self.titleLabel = QLabel(self.card)
        self.titleLabel.setObjectName("guideTitle")
        self.titleLabel.setWordWrap(True)
        self.bodyLabel = QLabel(self.card)
        self.bodyLabel.setObjectName("guideBody")
        self.bodyLabel.setWordWrap(True)

        self.dotsHost = QWidget(self.card)
        self.dotsLayout = QHBoxLayout(self.dotsHost)
        self.dotsLayout.setContentsMargins(0, 4, 0, 0)
        self.dotsLayout.setSpacing(6)
        self.dotsLayout.addStretch(1)
        self.dotsLayout.addStretch(1)

        buttonRow = QHBoxLayout()
        buttonRow.setContentsMargins(0, 6, 0, 0)
        self.skipButton = QPushButton(self.card)
        self.skipButton.setObjectName("guideGhost")
        self.backButton = QPushButton(self.card)
        self.backButton.setObjectName("guideGhost")
        self.nextButton = QPushButton(self.card)
        self.nextButton.setObjectName("guideNext")
        buttonRow.addWidget(self.skipButton)
        buttonRow.addStretch(1)
        buttonRow.addWidget(self.backButton)
        buttonRow.addWidget(self.nextButton)

        layout.addWidget(self.metaLabel)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.bodyLabel)
        layout.addWidget(self.dotsHost)
        layout.addLayout(buttonRow)

        self.skipButton.clicked.connect(self.skipClicked)
        self.backButton.clicked.connect(self.prevClicked)
        self.nextButton.clicked.connect(self.nextClicked)
        self.setStyleSheet(
            """
            #guideCard {
                background: #ffffff;
                border: 1px solid #d0d7de;
                border-radius: 14px;
            }
            QLabel#guideTitle { color: #1f2328; font-size: 16px; font-weight: 600; }
            QLabel#guideBody { color: #57606a; font-size: 13px; }
            QLabel#guideMeta { color: #8c959f; font-size: 12px; }
            QPushButton#guideNext {
                background: #009faa; color: white; border: none;
                border-radius: 8px; padding: 6px 14px; font-size: 13px;
            }
            QPushButton#guideNext:hover { background: #00b3bf; }
            QPushButton#guideGhost {
                background: transparent; color: #57606a; border: none;
                padding: 6px 10px; font-size: 13px;
            }
            QPushButton#guideGhost:hover { color: #009faa; }
            QPushButton#guideGhost:disabled { color: #b0b8c0; }
            """
        )

    def set_content(
        self,
        meta: str,
        title: str,
        body: str,
        next_text: str,
        back_text: str,
        skip_text: str,
        back_enabled: bool,
        index: int,
        total: int,
    ):
        self.metaLabel.setText(meta)
        self.titleLabel.setText(title)
        self.bodyLabel.setText(body)
        self.nextButton.setText(next_text)
        self.backButton.setText(back_text)
        self.skipButton.setText(skip_text)
        self.backButton.setEnabled(back_enabled)
        self._set_dots(index, total)
        self.layout().activate()
        hint = self.layout().sizeHint()
        self.setFixedHeight(max(hint.height(), 140))

    def _set_dots(self, index: int, total: int):
        if len(self._dots) != total:
            for dot in self._dots:
                self.dotsLayout.removeWidget(dot)
                dot.deleteLater()
            self._dots = []
            for _ in range(total):
                dot = _Dot(self.dotsHost)
                self._dots.append(dot)
                self.dotsLayout.insertWidget(self.dotsLayout.count() - 1, dot)
        for i, dot in enumerate(self._dots):
            dot.set_on(i == index)
