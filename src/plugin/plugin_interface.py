import os, inspect
from PyQt5.QtWidgets import QApplication, QStyle
from PyQt5.QtGui import QIcon
from abc import ABC, abstractmethod
from enum import Enum
from common import *

class GlobalEventEnum(Enum):
    OcrStartEvent = 1
    """OCR开始事件"""
    OcrEndSuccessEvent = 2
    """OCR结束事件"""
    OcrEndFailEvent = 3
    """OCR失败事件"""

    ImageCopyingEvent = 4
    """图片复制中事件"""
    ImageSavingEvent = 5
    """图片保存中事件"""

    RegisterContextMenuEvent = 6
    """注册右键弹出菜单事件"""

    RegisterToolbarMenuEvent = 7
    """注册工具栏菜单事件"""

    GlobalHotKeyRegisterStart = 13
    """全局热键开始注册"""
    GlobalHotKeyRegisterEnd = 14
    """全局热键结束注册"""


class PluginInterface(ABC):
    def __init__(self):
        self._enable = False

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def displayName(self):
        return "Unknown"

    @property
    @abstractmethod
    def desc(self) -> str:
        pass

    @property
    def author(self) -> str:
        return "Unknown"

    @property
    def version(self) -> str:
        return "v0.0.1"

    @property
    def url(self) -> str:
        return "http://interwovencode.xyz/"

    @property
    def tags(self) -> list:
        return []

    @property
    def previewImages(self) -> list:
        return []

    @property
    def supportSystems(self) -> list:
        return ["win32", "darwin", "linux"]

    @property
    def icon(self) -> any:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton)

    @property
    def enable(self) -> bool:
        return self._enable

    @property
    def isAllowModify(self) -> bool:
        return True

    @enable.setter
    def enable(self, value: bool):
        if self._enable == value:
            return
        self._enable = value
        self.onChangeEnabled()

    def onLoaded(self):
        pass

    def onChangeEnabled(self):
        # self.log(f"onChangeEnabled ===> {self.name} ===> {self.enable}")
        pass

    def handleEvent(self, eventName: GlobalEventEnum, *args, **kwargs):
        # self.log(f"[{self.name}]：{eventName} ==> {args} {kwargs}")
        pass

    def log(self, message):
        frame = inspect.currentframe().f_back
        evalFilename = frame.f_code.co_filename
        evalLineNumber = frame.f_lineno
        final = f"{self.name}|{evalFilename}:{evalLineNumber} ==> {message}"
        logger.info(final, logger_name=f"plugin")