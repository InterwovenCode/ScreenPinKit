# coding=utf-8
from PyQt5.QtCore import QEvent, QObject, QPoint, QRect, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

from common import cfg, logger

from .guide_overlay import GuideBubble, GuideShade, place_bubble, pretty_hotkey


class _Step:
    def __init__(self, kind: str, title: str, body: str):
        self.kind = kind
        self.title = title
        self.body = body


class AppGuide(QObject):
    """跟着真实窗口走的使用指引。遮罩只负责说明，挖孔里的操作仍由原窗口处理。"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main = main_window
        self.shade = GuideShade(main_window)
        self.bubble = GuideBubble(main_window)
        self.bubble.nextClicked.connect(self._next)
        self.bubble.prevClicked.connect(self._prev)
        self.bubble.skipClicked.connect(self.finish)
        self._timer = QTimer(self)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._tick)
        self.running = False
        self._steps = []
        self._index = 0
        self._selection_rect = QRect()
        self._opened_shot = False
        self._opened_paint = False
        self._paint_was_visible = False
        self._placed_pos = None
        self._raise_pending = False

    def start(self):
        if self.running:
            self.running = False
            self._timer.stop()
            self.shade.hide()
            self.bubble.hide()
            self._close_owned_shot()
            self._restore_paint()
        self._timer.stop()
        self.shade.hide()
        self.bubble.hide()
        self._selection_rect = QRect()
        self._opened_shot = False
        self._opened_paint = False
        self._placed_pos = None
        self._raise_pending = False
        self._paint_was_visible = self._paint_visible()
        self._steps = self._build_steps()
        self._index = 0
        self.running = True
        self._hook_shot()
        self._timer.start()
        logger.info("开始使用指引")
        self._go(0)

    def finish(self):
        if not self.running and not self.shade.isVisible() and not self.bubble.isVisible():
            return
        self.running = False
        self._timer.stop()
        self.shade.hide()
        self.bubble.hide()
        self._close_owned_shot()
        self._restore_paint()
        cfg.set(cfg.guideCompleted, True)
        logger.info("结束使用指引")

    def _build_steps(self):
        shot = pretty_hotkey(cfg.get(cfg.hotKeyScreenShot)) or "F7"
        paint = pretty_hotkey(cfg.get(cfg.hotKeyScreenPaint)) or "F4"
        through = pretty_hotkey(cfg.get(cfg.hotKeyToggleMouseClickThrough)) or "Alt+F"
        toggle = pretty_hotkey(cfg.get(cfg.hotKeySwitchScreenPaintMode)) or "Alt+L"
        return [
            _Step(
                "welcome",
                self.tr("Welcome to ScreenPinKit"),
                self.tr(
                    "ScreenPinKit stays in the tray for screenshots, pins, and annotation. This guide walks through those windows."
                ),
            ),
            _Step(
                "tray",
                self.tr("The tray icon"),
                self.tr(
                    "Left-click the tray icon to take a screenshot. Right-click it to open Preferences or Exit."
                ),
            ),
            _Step(
                "select",
                self.tr("Take a screenshot"),
                self.tr(
                    "Drag to select a region, or click a window the app highlights. Press {shot} later to open this view again."
                ).format(shot=shot),
            ),
            _Step(
                "pin",
                self.tr("Pin the selection"),
                self.tr(
                    "Press Ctrl+T to pin the selection. Ctrl+C copies it without pinning. C copies the color under the pointer."
                ),
            ),
            _Step(
                "pin_ops",
                self.tr("Work with the pin"),
                self.tr(
                    "Scroll to zoom. Ctrl+scroll changes opacity. Double-click closes the pin. {through} toggles click-through."
                ).format(through=through),
            ),
            _Step(
                "toolbar",
                self.tr("Annotate on the pin"),
                self.tr(
                    "The toolbar is open. Choose a tool and draw. Later, right-click the pin and choose Show toolbar to open it again."
                ),
            ),
            _Step(
                "paint",
                self.tr("Draw on the desktop"),
                self.tr(
                    "Press {paint} to draw on the whole desktop. Ctrl+W finishes and lets clicks pass through. {toggle} hides or shows the drawing."
                ).format(paint=paint, toggle=toggle),
            ),
            _Step(
                "ocr",
                self.tr("Read text with OCR"),
                self.tr(
                    "On a pin, press Ctrl+A to recognize text. Drag across the result, then press Ctrl+C to copy it. This step does not start OCR for you."
                ),
            ),
            _Step(
                "done",
                self.tr("You are ready"),
                self.tr(
                    "Open Usage guide from the tray menu whenever you want this walkthrough again."
                ),
            ),
        ]

    def _kind(self) -> str:
        if not self._steps:
            return ""
        return self._steps[self._index].kind

    def _index_of(self, kind: str) -> int:
        for i, step in enumerate(self._steps):
            if step.kind == kind:
                return i
        return 0

    def _go(self, index: int):
        if not self.running or not self._steps:
            return
        self._index = max(0, min(index, len(self._steps) - 1))
        self._render()
        self._enter()

    def _next(self):
        if not self.running:
            return
        if self._index >= len(self._steps) - 1:
            self.finish()
            return
        self._go(self._index + 1)

    def _prev(self):
        if self.running and self._index > 0:
            self._go(self._index - 1)

    def _render(self):
        step = self._steps[self._index]
        last = self._index == len(self._steps) - 1
        self.bubble.set_content(
            f"{self._index + 1} / {len(self._steps)}",
            step.title,
            step.body,
            self.tr("Done") if last else self.tr("Next"),
            self.tr("Back"),
            self.tr("Skip"),
            self._index > 0,
            self._index,
            len(self._steps),
        )

    def _enter(self):
        kind = self._kind()
        if kind == "paint":
            self._close_owned_shot()
            self._open_paint()
        else:
            self._hide_paint()
            if kind == "select":
                self._open_screenshot()
            elif kind == "pin":
                if self.main.screenShotWindow is None:
                    self._open_screenshot()
            elif kind in ("pin_ops", "toolbar", "ocr", "done"):
                self._close_owned_shot()
            if kind == "toolbar":
                self._show_pin_toolbar()
        self._layout()
        if kind in ("select", "pin"):
            self._activate(self.main.screenShotWindow)
        elif kind in ("pin_ops", "toolbar", "ocr"):
            self._activate(self._latest_pin())
        self._raise_guide()

    def _tick(self):
        if not self.running:
            return
        self._layout()

    def _layout(self):
        if not self.running:
            return
        hole, show_shade, focus = self._visual_for(self._kind())
        self._watch(focus)
        self._watch(self.main.screenShotWindow)
        self._watch(self._latest_pin())
        self._watch(self._toolbar_widget())
        self._watch(self.main.screenPaintWindow)
        if show_shade:
            self.shade.set_scene(hole, lambda widget=focus: self._alive(widget))
            if not self.shade.isVisible():
                self.shade.show()
        elif self.shade.isVisible():
            self.shade.hide()
        anchor = hole if show_shade else QRect()
        self._place_bubble(anchor)
        if not self.bubble.isVisible():
            self.bubble.show()

    def _visual_for(self, kind: str):
        if kind == "select":
            return QRect(), False, self.main.screenShotWindow
        if kind == "tray":
            return self._tray_rect(), True, None
        if kind == "pin":
            focus = self.main.screenShotWindow or self._latest_pin()
            hole = self._selection_rect if self.main.screenShotWindow is not None else self._pin_rect()
            return hole, True, focus
        if kind == "pin_ops":
            pin = self._latest_pin()
            return self._pin_rect(), True, pin
        if kind == "toolbar":
            pin = self._latest_pin()
            hole = self._toolbar_rect()
            if hole.isEmpty():
                hole = self._pin_rect()
            return hole, True, pin
        if kind == "ocr":
            pin = self._latest_pin()
            return self._pin_rect(), True, pin
        return QRect(), True, None

    def _place_bubble(self, anchor: QRect):
        screen = self._screen_geometry(anchor)
        pos = place_bubble(anchor, self.bubble.size(), screen)
        if self._placed_pos == pos:
            return
        self._placed_pos = QPoint(pos)
        self.bubble.move(pos)

    def _screen_geometry(self, anchor: QRect) -> QRect:
        if anchor.isValid() and not anchor.isEmpty():
            point = anchor.center()
        else:
            point = QCursor.pos()
        screen = QApplication.screenAt(point)
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            return QRect(0, 0, 1280, 720)
        return screen.availableGeometry()

    def _raise_guide(self):
        if not self.running:
            return
        if self.shade.isVisible():
            self.shade.raise_()
        if self.bubble.isVisible():
            self.bubble.raise_()

    def _flush_raise(self):
        self._raise_pending = False
        self._raise_guide()

    def _watch(self, widget):
        widget = self._alive(widget)
        if widget is None or widget in (self.shade, self.bubble):
            return
        if getattr(widget, "_guide_watched", False):
            return
        widget.installEventFilter(self)
        widget._guide_watched = True

    def eventFilter(self, obj, event):
        if (
            self.running
            and not self._raise_pending
            and event.type() in (QEvent.WindowActivate, QEvent.Show)
            and obj is not self.shade
            and obj is not self.bubble
        ):
            self._raise_pending = True
            QTimer.singleShot(0, self._flush_raise)
        return False

    def _open_screenshot(self):
        if self.main.screenShotWindow is None:
            # 先拿掉导览层，避免截图把气泡一起截进去。
            self._timer.stop()
            self.shade.hide()
            self.bubble.hide()
            QApplication.processEvents()
            self._opened_shot = True
            self.main.screenShot()
            if self.running:
                self._timer.start()
        self._hook_shot()

    def _hook_shot(self):
        wnd = self.main.screenShotWindow
        if wnd is None or getattr(wnd, "_guide_hooked", False):
            return
        wnd.selectionReady.connect(self._on_selection_ready)
        wnd.snipedSignal.connect(self._on_sniped)
        self._watch(wnd)
        wnd._guide_hooked = True

    def _on_selection_ready(self, rect: QRect):
        if not self.running:
            return
        self._selection_rect = QRect(rect)
        if self._kind() == "select":
            self._go(self._index_of("pin"))
        elif self._kind() == "pin":
            self._layout()

    def _on_sniped(self, cropRect, pixmap):
        if not self.running or pixmap.isNull():
            return
        self._selection_rect = cropRect.toAlignedRect()
        QTimer.singleShot(80, self._after_pin_created)

    def _after_pin_created(self):
        if not self.running:
            return
        if self._kind() in ("select", "pin"):
            self._go(self._index_of("pin_ops"))
        else:
            self._layout()

    def _close_owned_shot(self):
        wnd = self.main.screenShotWindow
        if self._opened_shot and wnd is not None:
            wnd.close()

    def _open_paint(self):
        wnd = self.main.screenPaintWindow
        if wnd is None:
            self._opened_paint = True
            self.main.screenPaint()
            return
        if not self._alive(wnd):
            return
        if not wnd.isVisible():
            wnd.show()
        if wnd.canvasEditor.drawWidget is not None:
            wnd.startDraw()

    def _hide_paint(self):
        wnd = self.main.screenPaintWindow
        if self._alive(wnd) and wnd.isVisible():
            wnd.hide()

    def _restore_paint(self):
        wnd = self.main.screenPaintWindow
        if not self._alive(wnd):
            if self._opened_paint:
                self.main.screenPaintWindow = None
            return
        if self._opened_paint:
            wnd.close()
            self.main.screenPaintWindow = None
            return
        if self._paint_was_visible:
            wnd.show()
        else:
            wnd.hide()

    def _paint_visible(self) -> bool:
        wnd = self.main.screenPaintWindow
        return self._alive(wnd) is not None and wnd.isVisible()

    def _show_pin_toolbar(self):
        pin = self._latest_pin()
        if pin is None or pin.painterWidget.drawWidget is None:
            return
        pin.showCommandBar()
        pin.raise_()

    def _latest_pin(self):
        windows = getattr(self.main.pinWindowMgr, "_windowsDict", None)
        if not windows:
            return None
        pin = self._alive(list(windows.values())[-1])
        if pin is not None and pin.isVisible():
            return pin
        return None

    def _pin_rect(self) -> QRect:
        pin = self._latest_pin()
        if pin is None:
            return QRect()
        return QRect(pin.mapToGlobal(QPoint(0, 0)), pin.size())

    def _toolbar_widget(self):
        pin = self._latest_pin()
        if pin is None:
            return None
        toolbar = getattr(pin.painterWidget, "toolbar", None)
        if toolbar is None:
            return None
        return self._alive(toolbar)

    def _toolbar_rect(self) -> QRect:
        toolbar = self._toolbar_widget()
        if toolbar is None or not toolbar.isVisible():
            return QRect()
        return QRect(toolbar.mapToGlobal(QPoint(0, 0)), toolbar.size())

    def _activate(self, widget):
        alive = self._alive(widget)
        if alive is not None:
            alive.activateWindow()

    def _tray_rect(self) -> QRect:
        tray = getattr(self.main, "systemTrayIcon", None)
        if tray is None:
            return QRect()
        geo = tray.geometry()
        if geo.isValid() and geo.width() > 1 and geo.height() > 1:
            return geo
        return QRect()

    def _alive(self, widget):
        if widget is None:
            return None
        try:
            widget.isVisible()
        except RuntimeError:
            return None
        return widget
