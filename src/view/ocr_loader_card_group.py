# coding:utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from common import cfg, ScreenShotIcon
from extend_widgets import *
from ocr_loader import *
from qfluentwidgets import FluentIcon as FIF


class OcrLoaderTypeSettingCard(OptionsSettingCard):
    """Toolbar card with a push button"""

    def __init__(self, parent: QWidget = None) -> None:
        configItem = cfg.useOcrLoaderType
        icon = ScreenShotIcon.OCR_LOADER
        title = parent.tr("Use ocrloader type")
        content = None
        texts = OcrLoaderTypeSettingCard.getLoaderDisplayNames()
        texts2 = OcrLoaderTypeSettingCard.getLoaderNames()
        if len(texts2) == 0:
            texts = ["Nothing"]
            texts2 = [""]
        cfg.useOcrLoaderType.defaultValue = texts2[0]
        cfg.useOcrLoaderType.validator = OptionsValidator(texts2)
        super().__init__(
            configItem, icon, title, content=content, texts=texts, parent=parent
        )

    @staticmethod
    def getLoaderDisplayNames():
        texts = []
        for val0 in ocrLoaderMgr.loaderDict.values():
            loader: OcrLoaderInterface = val0
            texts.append(loader.displayName)
        return texts

    @staticmethod
    def getLoaderNames():
        texts = []
        for val0 in ocrLoaderMgr.loaderDict.values():
            loader: OcrLoaderInterface = val0
            texts.append(loader.name)
        return texts


class OcrLoaderSettingGroup(SettingCardGroup):
    """Setting card group"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent)
        self.ocrLoaderTypeCard = OcrLoaderTypeSettingCard(self)
        self.ocrLoaderFolderCard = PushSettingCard(
            self.tr("Choose folder"),
            FIF.DOWNLOAD,
            self.tr("OcrLoader directory"),
            cfg.get(cfg.ocrLoaderFolder),
            self,
        )
        self.addSettingCard(self.ocrLoaderFolderCard)
        self.addSettingCard(self.ocrLoaderTypeCard)

        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        self.ocrLoaderFolderCard.clicked.connect(self.__onOcrLoaderFolderCardClicked)

    def __onOcrLoaderFolderCardClicked(self):
        """ocrloader folder card clicked slot"""
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), cfg.get(cfg.ocrLoaderFolder))
        if not folder or cfg.get(cfg.ocrLoaderFolder) == folder:
            return

        cfg.set(cfg.ocrLoaderFolder, folder)
        self.ocrLoaderFolderCard.setContent(folder)
