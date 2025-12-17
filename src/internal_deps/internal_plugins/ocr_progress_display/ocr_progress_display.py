import glob
import os

from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import (
    InfoBar,
    InfoBarIcon,
    InfoBarPosition,
    StateToolTip,
    FluentIcon as FIF,
    TransparentToolButton,
)

from plugin import PluginInterface, GlobalEventEnum

class OCRProgressDisplay(PluginInterface):
    def __init__(self):
        super().__init__()
        self._runtimePath = os.path.dirname(os.path.abspath(__file__))
    
    @property
    def runtimePath(self):
        return self._runtimePath

    @property
    def previewImages(self) -> list:
        folderPath = os.path.join(self.runtimePath, "preview")
        images = glob.glob(f"{folderPath}/*.*", recursive=False)
        return images

    @property
    def name(self):
        return "OCRProgressDisplay"

    @property
    def displayName(self):
        return "OCR进度显示"

    @property
    def desc(self):
        return "将OCR识别进度显示在UI上"

    @property
    def author(self) -> str:
        return "yaoxuanzhi"

    @property
    def icon(self):
        return QIcon(self.runtimePath + "/icons/ocr_process_display.svg")

    @property
    def version(self) -> str:
        return "v1.0.0"

    @property
    def url(self) -> str:
        return "https://github.com/InterwovenCode/ScreenPinKit/blob/main/src/internal_deps/internal_plugins/ocr_progress_display.py"

    @property
    def tags(self) -> list:
        return ["ocr","ui"]

    @property
    def isAllowModify(self) -> bool:
        return False

    def handleEvent(self, eventName, *args, **kwargs):
        if eventName == GlobalEventEnum.OcrStartEvent:
            self.log(f"OCR started {self.name} ===> {self.desc}")
            ocrMode = kwargs["ocr_mode"]
            parentWidget: QWidget = kwargs["parent_widget"]
            if (
                not hasattr(parentWidget, "stateTooltip")
                or parentWidget.stateTooltip == None
            ):
                parentWidget.stateTooltip = StateToolTip(
                    f"正在OCR识别[{ocrMode}]", "客官请耐心等待哦~~", parentWidget
                )
                parentWidget.stateTooltip.setStyleSheet(
                    "background: transparent; border:0px;"
                )
                parentWidget.stateTooltip.move(
                    parentWidget.geometry().topRight()
                    + QPoint(
                        -parentWidget.stateTooltip.frameSize().width() - 20,
                        parentWidget.stateTooltip.frameSize().height() - 20,
                    )
                )
                parentWidget.stateTooltip.show()
        elif eventName == GlobalEventEnum.OcrEndSuccessEvent:
            self.log("OCR ended")
            parentWidget: QWidget = kwargs["parent_widget"]
            if (
                hasattr(parentWidget, "stateTooltip")
                and parentWidget.stateTooltip != None
            ):
                parentWidget.stateTooltip.setContent("OCR识别已结束")
                parentWidget.stateTooltip.setState(True)
                parentWidget.stateTooltip = None
        elif eventName == GlobalEventEnum.OcrEndFailEvent:
            self.log("OCR fail")
            parentWidget: QWidget = kwargs["parent_widget"]
            input: str = kwargs["message"]
            if (
                hasattr(parentWidget, "stateTooltip")
                and parentWidget.stateTooltip != None
            ):
                infoBar = InfoBar(
                    icon=InfoBarIcon.ERROR,
                    title="OCR 失败",
                    content=input,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=-1,  # won't disappear automatically
                    parent=parentWidget,
                )
                copyButton = TransparentToolButton(FIF.COPY, parentWidget)
                copyButton.setFixedSize(36, 36)
                copyButton.setIconSize(QSize(12, 12))
                copyButton.setCursor(Qt.PointingHandCursor)
                copyButton.setVisible(True)
                copyButton.clicked.connect(lambda: self.copyText(infoBar))
                infoBar.addWidget(copyButton)
                infoBar.show()
                parentWidget.stateTooltip.setContent("OCR识别失败")
                parentWidget.stateTooltip.setState(True)
                parentWidget.stateTooltip = None

    def copyText(self, infoBar: InfoBar):
        text = infoBar.contentLabel.text()
        QApplication.clipboard().setText(text)
