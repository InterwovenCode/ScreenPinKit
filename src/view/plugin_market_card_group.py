# coding=utf-8
import time
from sortedcontainers import SortedDict
from extend_widgets import *
from plugin import *
from .plugin_card_view import PluginCardView, PluginCardViewWithScrollArea

class LineEdit(SearchLineEdit):
    """ Search line edit """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(self.tr('Search plugins'))
        self.setFixedWidth(304)
        self.textChanged.connect(self.search)

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

class ItemCard(ElevatedCardWidget):
    """ App information card """

    def __init__(self, plugin: PluginInterface, parent=None):
        super().__init__(parent)
        self.setFixedSize(304, 160)
        self.attachWidget:ItemCardView = parent
        self.plugin = plugin
        self.itemState = EnumItemCardState.NoneState
        self.iconWidget = TransparentToolButton(plugin.icon, self)
        self.iconWidget.setIconSize(QSize(64, 64))
        self.iconWidget.clicked.connect(self.onIconClicked)

        self.nameLabel = TitleLabel(plugin.displayName, self)
        setFont(self.nameLabel, 14, QFont.Bold)
        self.tagGroupWidget = TagGroupWidget(plugin.tags, self)
        self.companyLabel = HyperlinkLabel(
            QUrl(plugin.url), plugin.author, self)

        self.descriptionLabel = BodyLabel(
            plugin.desc, self)
        setFont(self.descriptionLabel, 12)
        self.descriptionLabel.setWordWrap(True)

        self.versionButton = PillPushButton(plugin.version, self)
        self.versionButton.setCheckable(False)
        setFont(self.versionButton, 12)
        self.versionButton.setFixedSize(80, 32)

        self.contentLayout = QVBoxLayout(self)
        self.leftLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.optionSliderLayout = QHBoxLayout()

        self.initLayout()

    def initLayout(self):
        self.contentLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)

        iconLayout = QVBoxLayout()
        self.topLayout.addLayout(iconLayout)
        iconLayout.addWidget(self.iconWidget)
        iconLayout.addWidget(self.versionButton)

        pluginBaseLayout = QVBoxLayout()
        self.topLayout.addLayout(pluginBaseLayout)
        pluginBaseLayout.addWidget(self.nameLabel)
        pluginBaseLayout.addWidget(self.tagGroupWidget)
        pluginBaseLayout.addWidget(self.companyLabel)

        pluginBaseLayout.addLayout(self.optionSliderLayout)
        self.contentLayout.addWidget(self.descriptionLabel)

    def setInstalledUI(self, defaultChecked):
        if hasattr(self, 'downloadButton'):
            self.downloadButton.deleteLater()

        self.switchButton = SwitchButton(self.tr('关闭'))
        self.switchButton.setChecked(defaultChecked)
        self.deleteButton = TransparentToolButton(FluentIcon.DELETE)

        self.optionSliderLayout.addWidget(self.switchButton)
        self.optionSliderLayout.addWidget(self.deleteButton, 0, Qt.AlignRight)

        self.deleteButton.clicked.connect(self.onDeleteButtonClicked)

        self.deleteButton.setEnabled(self.plugin.isAllowModify)
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)

    def setUnInstalledUI(self):
        if hasattr(self, 'deleteButton'):
            self.deleteButton.deleteLater()
        if hasattr(self,'switchButton'):
            self.switchButton.deleteLater()

        isSupport = False
        for system in self.plugin.supportSystems:
            if sys.platform.startswith(system):
                isSupport = True

        self.downloadButton = TransparentToolButton(FluentIcon.DOWNLOAD)
        self.downloadButton.setEnabled(isSupport)
        self.downloadButton.clicked.connect(self.onDownloadButtonClicked)
        self.optionSliderLayout.addWidget(self.downloadButton, 0, Qt.AlignRight)

    def bindConfigItem(self, configItem: PluginConfigItemEx):
        self.configItem = configItem

        lastItemState:EnumItemCardState = pluginCfg.get(self.configItem)
        if lastItemState == EnumItemCardState.UninstallState:
            self.setUnInstalledUI()
        elif lastItemState == EnumItemCardState.ActiveState:
            self.setInstalledUI(True)
        elif lastItemState == EnumItemCardState.DeActiveState:
            self.setInstalledUI(False)

    def onIconClicked(self):
        parent = self.parentWidget()
        while parent.parentWidget():
            parent = parent.parentWidget()

        pluginView = PluginCardView(self.plugin, parent)
        # pluginView = PluginCardViewWithScrollArea(self.plugin, parent)
        pluginView.exec()

    def onDeleteButtonClicked(self):
        parent = self.parentWidget()
        while parent.parentWidget():
            parent = parent.parentWidget()

        isOk = pluginMgr.unInstallNetworkPlugin(parent, self.plugin.name)
        if not isOk:
            return

        # 更新当前卡片为“未安装”状态
        self.setUnInstalledUI()
        self.setItemState(EnumItemCardState.UninstallState)

        # 增量同步插件列表并刷新启用状态，避免整页 UI 重建
        pluginMgr.syncPluginsIncremental()
        pluginMgr.refreshPluginsEnableState()

    def onDownloadButtonClicked(self):
        parent = self.parentWidget()
        while parent.parentWidget():
            parent = parent.parentWidget()

        isOk = pluginMgr.installNetworkPlugin(parent, self.plugin.name, self.plugin.url)
        if not isOk:
            return

        # 立即把当前卡片切换为“已安装并启用”状态
        self.setInstalledUI(True)
        self.setItemState(EnumItemCardState.ActiveState)

        # 增量同步插件列表并刷新启用状态，加载新安装的插件实例
        pluginMgr.syncPluginsIncremental()
        pluginMgr.refreshPluginsEnableState()

    def setItemState(self, newState: EnumItemCardState):
        if self.itemState == newState:
            return

        self.itemState = newState
        pluginCfg.set(self.configItem, newState)

    @property
    def tags(self) -> str:
        return self.tagGroupWidget.text()

    @tags.setter
    def tags(self, value:str):
        self.tagGroupWidget.setText(value)

    @property
    def url(self) -> str:
        return self.companyLabel.url.toString()

    @url.setter
    def url(self, value:str):
        self.companyLabel.setUrl(value)

    @property
    def title(self) -> str:
        return self.nameLabel.text()

    @title.setter
    def title(self, value:str):
        self.nameLabel.setText(value)

    @property
    def version(self) -> str:
        return self.versionButton.text()

    @version.setter
    def version(self, value:str):
        self.versionButton.setText(value)

    @property
    def description(self) -> str:
        return self.descriptionLabel.text()

    @description.setter
    def description(self, value:str):
        self.descriptionLabel.setText(value)

    @property
    def author(self) -> str:
        return self.companyLabel.text()

    @author.setter
    def author(self, value:str):
        self.companyLabel.setText(value)

    @property
    def icon(self) -> QIcon:
        return self.iconWidget.icon

    @icon.setter
    def icon(self, icon:QIcon):
        self.iconWidget.setIcon(icon)

    def onSwitchCheckedChanged(self, isChecked):
        if isChecked:
            self.switchButton.setText(self.tr('开启'))
        else:
            self.switchButton.setText(self.tr('关闭'))

        if isChecked:
            self.setItemState(EnumItemCardState.ActiveState)
        else:
            self.setItemState(EnumItemCardState.DeActiveState)

        # 增量更新：只根据配置刷新已加载插件的启用状态，避免全量 reload
        pluginMgr.refreshPluginsEnableState()

class ItemCardView(QWidget):
    """ Item card view """
    searchedSignal = pyqtSignal(list)
    reloadUISignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("background-color: transparent;")
        self.searchLineEdit = LineEdit(self)

        self.view = QFrame(self)
        self.scrollArea = SmoothScrollArea(self.view)
        self.scrollWidget = QWidget(self.scrollArea)

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self.view)
        self.flowLayout = FlowLayout(self.scrollWidget, isTight=True)
        self.fuzzyMatch = FuzzyMatch()
        self.reloadUISignal.connect(self.reloadUI)

        self.sortedDict = SortedDict()
        self.cards = []     # type:List[ItemCard]
        self.icons = []
        self.options = []

        self.__initWidget()

    def __initWidget(self):
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setViewportMargins(0, 0, 0, 0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.searchLineEdit)
        self.vBoxLayout.addWidget(self.view)

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.scrollArea)

        self.flowLayout.setVerticalSpacing(8)
        self.flowLayout.setHorizontalSpacing(8)
        self.flowLayout.setContentsMargins(0, 3, 0, 0)

        self.searchLineEdit.clearSignal.connect(self.showAllPlugins)
        self.searchLineEdit.searchSignal.connect(self.search)

        self.initUI()

    def initUI(self):
        # 添加本地磁盘上的插件到UI上
        for plugin in pluginMgr.pluginDict.values():
            self.insertPluginPrepare(plugin)

        # 先排序再渲染(这里先显示，等到网络插件加载完成后再重刷UI)
        for plugin in self.sortedDict.values():
            self.addPlugin(plugin)

        # 添加网络插件市场的插件到UI上
        self.networkLoaderMgr = NetworkLoaderManager(cfg.get(cfg.pluginMarketUrl))
        self.networkLoaderMgr.loadItemFinishedSignal.connect(self.onLoadNetworkItemFinished)
        self.networkLoaderMgr.loadAllFinishedSignal.connect(self.reloadUI)
        self.networkLoaderMgr.start()

    def onLoadNetworkItemFinished(self, plugin: PluginInterface):
        if not hasattr(self, 'networkPluginCache'):
            self.networkPluginCache = []

        self.networkPluginCache.append(plugin)

    def onLoadAllFinished(self):
        if hasattr(self, 'networkPluginCache'):
            for plugin in self.networkPluginCache:
                self.insertPluginPrepare(plugin)

        # 先排序再渲染
        for plugin in self.sortedDict.values():
            self.addPlugin(plugin)

        self.showAllPlugins()

    def reloadUI(self):
        # 安装/卸载插件后，仅对插件列表做增量同步，避免全量卸载再重载
        pluginMgr.syncPluginsIncremental()
        self.flowLayout.removeAllWidgets()

        for card in self.cards:
            card.setVisible(False)
            card.deleteLater()
            card.close()

        self.cards.clear()
        self.icons.clear()
        self.options.clear()

        self.fuzzyMatch.clear()
        self.resetPluginPrepare()
        for plugin in pluginMgr.pluginDict.values():
            self.insertPluginPrepare(plugin)

        self.onLoadAllFinished()

    def insertPluginPrepare(self, plugin: PluginInterface):
        if plugin.name in self.sortedDict:
            return
        self.sortedDict[plugin.name] = plugin

    def resetPluginPrepare(self):
        self.sortedDict.clear()

    def addPlugin(self, plugin: PluginInterface):
        """ add plugin to view """
        pluginName:str = plugin.name
        if pluginName in self.options:
            return
        if not hasattr(pluginCfg, pluginName):
            configItem = PluginConfigItemEx(
                pluginName, "pluginState", 
                EnumItemCardState.UninstallState, 
            )

            setattr(pluginCfg, pluginName, configItem)
            if not issubclass(type(plugin), PluginInstConfig):
                pluginCfg.set(configItem, EnumItemCardState.ActiveState)
        else:
            configItem = getattr(pluginCfg, pluginName)

        card = ItemCard(plugin, self)
        card.bindConfigItem(configItem)

        self.fuzzyMatch.insertItem(pluginName + plugin.displayName + plugin.desc)

        self.cards.append(card)
        self.icons.append(icon)
        self.options.append(pluginName)
        self.flowLayout.addWidget(card)

    def search(self, keyWord: str):
        """ search icons """
        now = time.time()
        if not hasattr(self, "updateLastTime"):
            self.updateLastTime = 0
        if now - self.updateLastTime > 0.2:
            self.updateLastTime = now

            indexes = self.fuzzyMatch.bestMatch(keyWord)

            self.flowLayout.removeAllWidgets()

            for i, card in enumerate(self.cards):
                isVisible = i in indexes
                card.setVisible(isVisible)
                if isVisible:
                    self.flowLayout.addWidget(card)

            self.flowLayout.update()

    def showAllPlugins(self):
        self.flowLayout.removeAllWidgets()
        for card in self.cards:
            card.setVisible(True)
            self.flowLayout.addWidget(card)

        self.flowLayout.update()

class MarketSettingCard(ScrollArea):
    """Toolbar card with a push button"""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.interface = ItemCardView(self)

        self.resize(400, 400)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.interface)

class PluginMarketCardGroup(SettingCardGroup):
    """Setting card group"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent)
        self.marketCard = MarketSettingCard(self)
        self.addSettingCard(self.marketCard)