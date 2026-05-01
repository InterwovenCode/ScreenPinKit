import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import (
    QCoreApplication,
    QLocale,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTranslator,
)
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QWidget

import common.resource  # noqa: F401  注册 :/i18n
from view.guide_overlay import GuideBubble, GuideShade, place_bubble, pretty_hotkey

TS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "common",
    "resource",
    "i18n",
    "settings.zh_CN.ts",
)


def test_pretty_hotkey():
    assert pretty_hotkey("") == ""
    assert pretty_hotkey("f7") == "F7"
    assert pretty_hotkey("alt+f") == "Alt+F"
    assert pretty_hotkey("shift+f7") == "Shift+F7"
    assert pretty_hotkey("ctrl+shift+s") == "Ctrl+Shift+S"


def test_place_bubble():
    screen = QRect(0, 0, 1920, 1080)
    bubble = QSize(380, 180)

    top = place_bubble(QRect(), bubble, screen)
    assert top.y() == 48
    assert top.x() == screen.center().x() - bubble.width() // 2

    below = place_bubble(QRect(100, 100, 200, 80), bubble, screen)
    assert below == QPoint(100, 194)

    above = place_bubble(QRect(100, 900, 200, 100), bubble, screen)
    assert above.y() == 706
    assert above.x() == 100

    side = place_bubble(QRect(100, 50, 200, 1000), bubble, screen)
    assert side.x() == 314
    assert side.y() == 50


def _guide_messages():
    root = ET.parse(TS_PATH).getroot()
    messages = {}
    for context in root.findall("context"):
        name = context.findtext("name")
        if name not in ("AppGuide", "MainWindow"):
            continue
        for message in context.findall("message"):
            source = message.findtext("source")
            translation = message.findtext("translation")
            if name == "MainWindow" and source != "Usage guide":
                continue
            messages[(name, source)] = translation
    return messages


def test_guide_translations():
    samples = {"shot": "F7", "through": "Alt+F", "paint": "F4", "toggle": "Alt+L"}
    messages = _guide_messages()
    assert ("AppGuide", "Next") in messages
    assert ("MainWindow", "Usage guide") in messages
    for (context, source), translation in messages.items():
        fields = set(re.findall(r"\{(\w+)\}", source))
        assert fields == set(re.findall(r"\{(\w+)\}", translation)), source
        if fields:
            source.format(**samples)
            translation.format(**samples)

    app = QApplication.instance() or QApplication([])
    chinese = QTranslator()
    loaded = chinese.load(
        QLocale(QLocale.Chinese, QLocale.China), "settings", ".", ":/i18n"
    )
    assert loaded
    assert chinese.translate("AppGuide", "Next") == "下一步"
    assert chinese.translate("AppGuide", "Skip") == "跳过"
    assert chinese.translate("MainWindow", "Usage guide") == "使用指引"
    select = chinese.translate(
        "AppGuide",
        "Drag to select a region, or click a window the app highlights. Press {shot} later to open this view again.",
    )
    assert "{shot}" in select
    assert select.format(shot="F7").endswith("F7 可以再次打开截图。")
    assert chinese.translate("MainWindow", "Snap") == "截图"

    english = QTranslator()
    assert not english.load(QLocale(QLocale.English), "settings", ".", ":/i18n")
    app.installTranslator(chinese)
    assert QCoreApplication.translate("AppGuide", "Done") == "完成"


def test_overlay_mask_and_bubble_click():
    app = QApplication.instance() or QApplication([])
    clicked = {"next": 0}
    parent = QWidget()
    bubble = GuideBubble(parent)
    bubble.nextClicked.connect(lambda: clicked.__setitem__("next", clicked["next"] + 1))
    bubble.set_content("1 / 9", "Title", "Body", "Next", "Back", "Skip", False, 0, 9)
    bubble.show()
    app.processEvents()
    assert bubble.isVisible()
    assert bubble.backButton.isEnabled() is False
    QTest.mouseClick(bubble.nextButton, Qt.LeftButton)
    app.processEvents()
    assert clicked["next"] == 1

    shade = GuideShade(parent)
    shade.set_scene(QRect(80, 60, 120, 90), None)
    shade.set_scene(QRect(80, 60, 120, 90), None)
    shade.show()
    app.processEvents()
    assert shade.isVisible()
    assert shade._scene_ready
    mask = shade.mask()
    assert not mask.isEmpty()
    local_hole = shade._local_inner()
    assert not mask.contains(local_hole.center())
    assert mask.contains(shade.rect().topLeft())
    shade.set_scene(QRect(), None)
    assert shade.mask().isEmpty()
    shade.set_scene(QRect(), None)
    assert shade.mask().isEmpty()


if __name__ == "__main__":
    test_pretty_hotkey()
    test_place_bubble()
    test_guide_translations()
    test_overlay_mask_and_bubble_click()
    print("ok")
