# coding:utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *

class LineEditPlus(LineEdit):
    finalTextChanged = pyqtSignal(str)
    def __init__(self, oldText: str, parent=None):
        super().__init__(parent)
        self.oldText = oldText
        self.setText(oldText)
        self.setPlaceholderText(oldText)
        # self.setClearButtonEnabled(True)
        self.setAlignment(Qt.AlignCenter)
        self.setValidator(QIntValidator()) 

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Enter:
            self.finalTextChanged.emit(self.text())
        super().keyPressEvent(a0)

class TextModifyDialog(MaskDialogBase):
    finalTextChanged = pyqtSignal(str)

    def __init__(self, oldText: str, parent=None):
        super().__init__(parent)
        self.lineEdit = LineEditPlus(oldText)
        self.lineEdit.finalTextChanged.connect(self.finalTextChanged)
        self.contentLayout = QVBoxLayout(self.widget)
        self.__initWidget()

    def __initWidget(self):
        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 80))
        # self.setMaskColor(QColor(0, 0, 0, 2)) # 几乎透明
        self.setMaskColor(QColor(0, 0, 0, 30)) # 半透明
        self.__initLayout()

    def __initLayout(self):
        self._hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.addWidget(self.lineEdit, 0, Qt.AlignCenter)

    def showEvent(self, e):
        self.lineEdit.setFocus()
        return super().showEvent(e)
