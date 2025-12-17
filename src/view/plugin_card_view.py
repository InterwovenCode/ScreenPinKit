# coding=utf-8
import sys
from typing import List

from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextBrowser, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from qfluentwidgets import (
    IconWidget,
    PushButton,
    BodyLabel,
    HyperlinkLabel,
    TitleLabel,
    SimpleCardWidget,
    HyperlinkButton,
    PillPushButton,
    TransparentToolButton,
    FluentIcon,
    HorizontalFlipView,
    MaskDialogBase,
    HeaderCardWidget,
    VerticalSeparator,
    InfoBarIcon,
    SingleDirectionScrollArea,
    setFont,
)

from plugin import PluginInterface

class TagGroupWidget(QWidget):
    """ Tags widget """

    def __init__(self, tags: list, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(2)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setAlignment(Qt.AlignLeft)

        for tag in tags:
            tagLabel = PushButton(tag, self)
            tagLabel.setEnabled(False)
            setFont(tagLabel, 12, QFont.DemiBold)
            self.hBoxLayout.addWidget(tagLabel, 0, Qt.AlignLeft)

class StatisticsWidget(QWidget):
    """ Statistics widget """

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent=parent)
        # self.versionLabel = CaptionLabel(title, self)
        self.versionLabel = BodyLabel(value, self)
        self.companyLabel = HyperlinkLabel(
            QUrl('http://interwovencode.xyz/'), 'InterwovenCode Inc.', self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.versionLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.companyLabel, 0, Qt.AlignBottom)
        setFont(self.versionLabel, 18, QFont.DemiBold)


class PluginInfoCard(SimpleCardWidget):
    """ App information card """

    def __init__(self, parent=None):
        super().__init__(parent)
        plugin:PluginInterface = self.parent().plugin

        self.iconWidget = TransparentToolButton(plugin.icon, self)
        self.iconWidget.setIconSize(QSize(120, 120))

        self.nameLabel = TitleLabel(plugin.displayName, self)
        self.homePageButton = HyperlinkButton(plugin.url, self.tr('GitHub home page'), self, FluentIcon.LINK)
        self.tagGroupWidget = TagGroupWidget(plugin.tags, self)
        self.descriptionLabel = BodyLabel(plugin.desc, self)
        self.descriptionLabel.setWordWrap(True)

        self.versionButton = PillPushButton(plugin.version, self)
        self.versionButton.setCheckable(False)
        setFont(self.versionButton, 12)
        self.versionButton.setFixedSize(80, 32)

        self.shareButton = HyperlinkLabel(
            QUrl(plugin.url), plugin.author, self)
        # self.shareButton = TransparentToolButton(FluentIcon.SHARE, self)
        # self.shareButton.setFixedSize(32, 32)
        # self.shareButton.setIconSize(QSize(14, 14))

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.initLayout()

    def initLayout(self):
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # name label and install button
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        self.topLayout.addWidget(self.homePageButton, 0, Qt.AlignRight)

        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.versionButton)

        # description label
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.descriptionLabel)

        # button
        self.vBoxLayout.addSpacing(12)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.tagGroupWidget, 0, Qt.AlignLeft)
        self.buttonLayout.addWidget(self.shareButton, 0, Qt.AlignRight)


class GalleryCard(HeaderCardWidget):
    """ Gallery card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('屏幕截图')

        self.flipView = HorizontalFlipView(self)
        self.expandButton = TransparentToolButton(
            FluentIcon.CHEVRON_RIGHT_MED, self)

        self.expandButton.setFixedSize(32, 32)
        self.expandButton.setIconSize(QSize(12, 12))

        plugin:PluginInterface = self.parent().plugin
        self.flipView.addImages(plugin.previewImages)
        self.flipView.setBorderRadius(8)
        self.flipView.setSpacing(10)

        self.headerLayout.addWidget(self.expandButton, 0, Qt.AlignRight)
        self.viewLayout.addWidget(self.flipView)


class InstallDepsCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        # import markdown
        self.setTitle('安装')

        self.webView = QWebEngineView()
        self.webView.settings().setAttribute(
            QWebEngineSettings.WebAttribute.PluginsEnabled, True
        )

        self.markdownWidget = QTextBrowser(self)
        self.markdownWidget.setStyleSheet("QTextEdit {background-color: transparent; border: none;}")
        self.markdownWidget.setReadOnly(True)
        setFont(self.markdownWidget, 12)

        text = """# 标题
## 子标题
这是一个 **Markdown** 示例。
  - 列表项1
  - 列表项2
  - 列表项3
[链接](https://www.example.com)

### Linux系统
```sh
sudo apt install python3-pip python3-pyqt5
pip3 install PyQt5
```

### Windows系统
```sh
choco install python tessactocr
```
        """

        self.markdownWidget.setMarkdown(text)
        self.viewLayout.addWidget(self.markdownWidget)

        # self.channel = QWebChannel()
        # self.webView.page().setBackgroundColor(Qt.GlobalColor.transparent)
        # self.webView.page().setWebChannel(self.channel)
        # self.viewLayout.addWidget(self.webView)
        # self.webView.setHtml(htmlConent)

class SystemRequirementCard(HeaderCardWidget):
    """ System requirements card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('系统支持')
        self.vBoxLayout = QVBoxLayout()
        self.hBoxLayout = QHBoxLayout()

        self.hBoxLayout.setSpacing(10)
        self.vBoxLayout.setSpacing(16)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        plugin:PluginInterface = self.parent().plugin

        for system in plugin.supportSystems:
            self.hBoxLayout.addWidget(VerticalSeparator(self))
            if sys.platform.startswith(system):
                self.iconWidget = IconWidget(InfoBarIcon.SUCCESS, self)
                self.iconWidget.setFixedSize(16, 16)
                self.hBoxLayout.addWidget(self.iconWidget)
            self.hBoxLayout.addWidget(QLabel(system))

        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.viewLayout.addLayout(self.vBoxLayout)

class PluginCardView(MaskDialogBase):
    def __init__(self, plugin: PluginInterface, parent=None):
        super().__init__(parent)

        self.plugin = plugin
        self.contentLayout = QVBoxLayout(self.widget)
        self.view = QWidget(self.widget)

        self.pluginCard = PluginInfoCard(self)
        self.systemCard = SystemRequirementCard(self)

        self.contentLayout.setContentsMargins(50, 50, 50, 50)
        self.contentLayout.setAlignment(Qt.AlignCenter)

        self.contentLayout.addWidget(self.pluginCard, 0, Qt.AlignTop)
        if len(self.plugin.previewImages) > 0:
            self.galleryCard = GalleryCard(self)
            self.contentLayout.addWidget(self.galleryCard, 0, Qt.AlignTop)

        self.contentLayout.addWidget(self.systemCard, 0, Qt.AlignTop)
        self.setStyleSheet(
            "PluginCardView {border: none; background:transparent}")
        self.__initLayout()

    def __initLayout(self):
        self._hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(1)
        self.contentLayout.addWidget(self.view)

    def showEvent(self, e):
        self.setFocus()
        return super().showEvent(e)

class PluginCardViewWithScrollArea(MaskDialogBase):
    def __init__(self, plugin: PluginInterface, parent=None):
        super().__init__(parent)

        self.plugin = plugin
        self.hBoxLayout = QHBoxLayout(self.widget)
        self.scrollArea = SingleDirectionScrollArea(self)
        self.view = QWidget(self.widget)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.pluginCard = PluginInfoCard(self)
        self.installDepsCard = InstallDepsCard(self)
        self.systemCard = SystemRequirementCard(self)

        self.scrollArea.setWidget(self.view)
        self.scrollArea.setWidgetResizable(True)

        self.hBoxLayout.setContentsMargins(50, 50, 50, 50)
        self.hBoxLayout.addWidget(self.scrollArea)

        self.vBoxLayout.addWidget(self.pluginCard, 0, Qt.AlignTop)
        if len(self.plugin.previewImages) > 0:
            self.galleryCard = GalleryCard(self)
            self.vBoxLayout.addWidget(self.galleryCard, 0, Qt.AlignTop)

        self.vBoxLayout.addWidget(self.installDepsCard, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.systemCard, 0, Qt.AlignTop)

        self.scrollArea.setStyleSheet(
            "QScrollArea {border: none; background:transparent}")

    def showEvent(self, e):
        self.setFocus()
        return super().showEvent(e)