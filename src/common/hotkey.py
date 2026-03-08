# coding:utf-8
"""
提供全局热键的注册功能

"""

import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from system_hotkey import *


class KeyboardListener(QObject):
    _handleSignal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initDatas()

    def __initDatas(self):
        self._pressedRecord = {}
        self.intervalTime = 400
        self._handleSignal.connect(self.handleKeyCallback)
        self._hotkeyBinds = {}

    @property
    def hotkeyBinds(self):
        return self._hotkeyBinds

    def handleKeyCallback(self, hotkeyTuple: tuple):
        if hotkeyTuple in self._hotkeyBinds:
            self._hotkeyBinds[hotkeyTuple]()

    def setHotkeyListener(self, hotkeyStr: str, callback: callable) -> None:
        hotkeyTuple = self.hotkeyToKeyNameTuple(hotkeyStr)
        self._hotkeyBinds[hotkeyTuple] = callback

    def setHotkeyListenerEx(
        self, hotkeyStr: str, times: int, callback: callable
    ) -> None:
        hotkeyTuple = self.hotkeyToKeyNameTuple(hotkeyStr)
        defaultValue = {
            "lastPressTime": 0,
            "triggerTimes": 0,
            "matchTimes": times,
        }
        self._pressedRecord[hotkeyTuple] = defaultValue
        finalTuple = (hotkeyTuple, defaultValue["matchTimes"])
        self._hotkeyBinds[finalTuple] = callback

    def updatePressTime(self, hotkeyStr: str):
        hotkeyTuple = self.hotkeyToKeyNameTuple(hotkeyStr)
        if hotkeyTuple not in self._pressedRecord:
            return
        matchValue = self._pressedRecord[hotkeyTuple]
        currentPressedTime = int(round(time.time() * 1000))
        differentTime = currentPressedTime - matchValue["lastPressTime"]
        matchValue["lastPressTime"] = currentPressedTime
        matchValue["triggerTimes"] = matchValue["triggerTimes"] + 1

        # 超过特定间隔时间重算
        if differentTime > self.intervalTime:
            matchValue["triggerTimes"] = 1

        # 满足检测次数则响应
        if matchValue["triggerTimes"] >= matchValue["matchTimes"]:
            matchValue["triggerTimes"] = 0
            finalTuple = (hotkeyTuple, matchValue["matchTimes"])
            self._handleSignal.emit(finalTuple)

    def __orderHotkeyList(self, keyNames: list) -> list:
        if len(keyNames) > 2:
            new_hotkey = []
            for mod in keyNames[:-1]:
                if "control" == mod:
                    new_hotkey.append(mod)
            for mod in keyNames[:-1]:
                if "shift" == mod:
                    new_hotkey.append(mod)
            for mod in keyNames[:-1]:
                if "alt" == mod:
                    new_hotkey.append(mod)
            for mod in keyNames[:-1]:
                if "super" == mod:
                    new_hotkey.append(mod)
            new_hotkey.append(keyNames[-1])
            keyNames = new_hotkey
        return keyNames

    def hotkeyToKeyNameTuple(self, hotkeyStr: str) -> list:
        hotkeyList = self.hotkeyToKeyNames(hotkeyStr)
        return tuple(hotkeyList)

    def hotkeyToKeyNames(self, hotkeyStr: str) -> list:
        result = []
        for str in hotkeyStr.split("+"):
            temp = str.replace("ctrl", "control")
            temp = temp.lower()
            if len(temp) > 0:
                result.append(temp)
        return self.__orderHotkeyList(result)

    def reset(self):
        self._pressedRecord.clear()
        self._hotkeyBinds.clear()


class KeyboardEx(KeyboardListener):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hk = SystemHotkey()

    def reset(self):
        super().reset()
        self.hk.unregister()

    def addHotKey(self, hotkeyStr: str, callback: callable, overwrite=False):
        hotkey = self.hotkeyToKeyNames(hotkeyStr)
        if len(hotkey) == 0:
            return
        finalTuple = tuple(hotkey)
        self.hk.register(
            hotkey,
            callback=lambda _: self._handleSignal.emit(finalTuple),
            overwrite=overwrite,
        )
        self.setHotkeyListener(hotkeyStr, callback)

    def addHotKeyEx(self, hotkeyStr: str, times, callback):
        hotkey = self.hotkeyToKeyNames(hotkeyStr)
        if len(hotkey) == 0:
            return
        self.hk.register(hotkey, callback=lambda _: self.updatePressTime(hotkeyStr))
        self.setHotkeyListenerEx(hotkeyStr, times, callback)


class QWidgetHotKey(KeyboardListener):
    """
    针对QWidget的热键监听，基于keyPressEvent实现
    Note:
        想实现一个支持多按的通用热键机制，并且其响应可以被子QWidget打断
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initKeyMap()

    def __initKeyMap(self):
        self.keyMap = {}
        self.keyMap[Qt.Key.Key_Space] = "space"
        self.keyMap[Qt.Key.Key_Control] = "ctrl"
        self.keyMap[Qt.Key.Key_Shift] = "shift"
        self.keyMap[Qt.Key.Key_Alt] = "alt"
        self.keyMap[Qt.Key.Key_W] = "w"
        self.keyMap[Qt.Key.Key_S] = "s"
        self.keyMap[Qt.Key.Key_A] = "a"
        self.keyMap[Qt.Key.Key_D] = "d"
        self.keyMap[Qt.Key.Key_F] = "f"
        self.keyMap[Qt.Key.Key_Q] = "q"
        self.keyMap[Qt.Key.Key_E] = "e"
        self.keyMap[Qt.Key.Key_R] = "r"
        self.keyMap[Qt.Key.Key_T] = "t"
        self.keyMap[Qt.Key.Key_Y] = "y"
        self.keyMap[Qt.Key.Key_U] = "u"
        self.keyMap[Qt.Key.Key_I] = "i"
        self.keyMap[Qt.Key.Key_O] = "o"
        self.keyMap[Qt.Key.Key_P] = "p"
        self.keyMap[Qt.Key.Key_Z] = "z"
        self.keyMap[Qt.Key.Key_X] = "x"
        self.keyMap[Qt.Key.Key_C] = "c"
        self.keyMap[Qt.Key.Key_V] = "v"
        self.keyMap[Qt.Key.Key_B] = "b"
        self.keyMap[Qt.Key.Key_N] = "n"
        self.keyMap[Qt.Key.Key_M] = "m"
        self.keyMap[Qt.Key.Key_0] = "0"
        self.keyMap[Qt.Key.Key_1] = "1"
        self.keyMap[Qt.Key.Key_2] = "2"
        self.keyMap[Qt.Key.Key_3] = "3"
        self.keyMap[Qt.Key.Key_4] = "4"
        self.keyMap[Qt.Key.Key_5] = "5"
        self.keyMap[Qt.Key.Key_6] = "6"
        self.keyMap[Qt.Key.Key_7] = "7"
        self.keyMap[Qt.Key.Key_8] = "8"
        self.keyMap[Qt.Key.Key_9] = "9"

    def keyPressEvent(self, event: QKeyEvent) -> None:
        hotkeyList = []
        if int(event.modifiers()) == Qt.KeyboardModifier.ControlModifier:
            hotkeyList.append("ctrl")
        if int(event.modifiers()) == Qt.KeyboardModifier.ShiftModifier:
            hotkeyList.append("shift")
        if int(event.modifiers()) == Qt.KeyboardModifier.AltModifier:
            hotkeyList.append("alt")
        if int(event.modifiers()) == Qt.KeyboardModifier.MetaModifier:
            hotkeyList.append("super")

        if event.key() in self.keyMap:
            keyName = self.keyMap[event.key()]
            if keyName not in hotkeyList:
                hotkeyList.append(keyName)

        if len(hotkeyList) > 0:
            key = "+".join(hotkeyList)
            self.updatePressTime(key)
