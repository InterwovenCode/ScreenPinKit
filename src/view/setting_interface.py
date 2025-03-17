# coding:utf-8
from common import cfg, ScreenShotIcon, StyleSheet
from version import HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    FolderListSettingCard,
    OptionsSettingCard,
    RangeSettingCard,
    PushSettingCard,
    ColorSettingCard,
    HyperlinkCard,
    PrimaryPushSettingCard,
    ScrollArea,
    ComboBoxSettingCard,
    ExpandLayout,
    Theme,
    InfoBar,
    CustomColorSettingCard,
    setTheme,
    setThemeColor,
    isDarkTheme,
)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog
from .hotkey_setting_card_group import HotkeySettingCardGroup
from .toolbar_setting_card_group import ToolbarSettingCardGroup
from .ocr_loader_card_group import OcrLoaderSettingGroup
from .plugin_market_card_group import PluginMarketCardGroup
from .logger_setting_card_group import LoggerSettingCardGroup


class SettingInterface(ScrollArea):
    """Setting interface"""

    checkUpdateSig = pyqtSignal()
    cacheFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # general
        self.generalGroup = SettingCardGroup(self.tr("General"), self.scrollWidget)
        
        self.pluginMarketUrlCard = HyperlinkCard(
            cfg.get(cfg.pluginMarketUrl),
            "Github Url",
            FIF.MARKET,
            self.tr("Plugin Market"),
            cfg.get(cfg.pluginMarketUrl),
            self.generalGroup,
        )
        self.pluginsFolderCard = PushSettingCard(
            self.tr("Choose folder"),
            FIF.DOWNLOAD,
            self.tr("Plugins directory"),
            cfg.get(cfg.pluginsFolder),
            self.generalGroup,
        )
        self.isAutoFindWindowCard = SwitchSettingCard(
            ScreenShotIcon.COPY,
            self.tr("Auto find window"),
            None,
            configItem=cfg.isAutoFindWindow,
            parent=self.generalGroup,
        )

        # pluginMarket
        self.pluginMarketGroup = PluginMarketCardGroup(
            self.tr("Plugin Market"), self.scrollWidget
        )

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr("Personalization"), self.scrollWidget
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr("Application theme"),
            self.tr("Change the appearance of your application"),
            texts=[self.tr("Light"), self.tr("Dark"), self.tr("Use system setting")],
            parent=self.personalGroup,
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%",
                "125%",
                "150%",
                "175%",
                "200%",
                self.tr("Use system setting"),
            ],
            parent=self.personalGroup,
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr("Language"),
            self.tr("Set your preferred language for UI"),
            texts=["简体中文", "English", self.tr("Use system setting")],
            parent=self.personalGroup,
        )

        # toolbar
        self.toolbarGroup = ToolbarSettingCardGroup(
            self.tr("Toolbar"), self.scrollWidget
        )

        # windowShadowStyle
        self.windowShadowStyleGroup = SettingCardGroup(
            self.tr("WindowShadowStyle"), self.scrollWidget
        )
        self.windowShadowStyleFocusColorCard = ColorSettingCard(
            cfg.windowShadowStyleFocusColor,
            ScreenShotIcon.PEN,
            self.tr("Focus color"),
            parent=self.windowShadowStyleGroup,
        )
        self.windowShadowStyleUnfocusColorCard = ColorSettingCard(
            cfg.windowShadowStyleUnFocusColor,
            ScreenShotIcon.PEN,
            self.tr("Unfocus color"),
            parent=self.windowShadowStyleGroup,
        )
        self.windowShadowStyleUseRoundStyleCard = OptionsSettingCard(
            cfg.windowShadowStyleRoundRadius,
            ScreenShotIcon.ROUND_BOX,
            self.tr("Use round style"),
            None,
            texts=["0", "5", "10", "15", "20"],
            parent=self.windowShadowStyleGroup,
        )
        self.windowShadowStyleIsSaveWithShadowCard = SwitchSettingCard(
            ScreenShotIcon.SAVE_AS,
            self.tr("Save screenshot with shadow"),
            None,
            configItem=cfg.windowShadowStyleIsSaveWithShadow,
            parent=self.windowShadowStyleGroup,
        )
        self.windowShadowStyleisCopyWithShadowCard = SwitchSettingCard(
            ScreenShotIcon.COPY,
            self.tr("Copy screenshot with shadow"),
            None,
            configItem=cfg.windowShadowStyleIsCopyWithShadow,
            parent=self.windowShadowStyleGroup,
        )

        # OcrLoaderSetting
        self.ocrLoaderSettingGroup = OcrLoaderSettingGroup(
            self.tr("OcrLoaderSetting"), self.scrollWidget
        )

        # hotkey
        self.hotkeyGroup = HotkeySettingCardGroup(
            self.tr("Global Hotkey"), self.scrollWidget
        )

        # logger
        self.loggerGroup = LoggerSettingCardGroup(
            self.tr("Logger"), 
            self.scrollWidget,
        )

        self.cacheFolderCard = PushSettingCard(
            self.tr("Choose folder"),
            FIF.DOWNLOAD,
            self.tr("Cache directory"),
            cfg.get(cfg.cacheFolder),
            self.generalGroup,
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget
        )
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr("Check for updates when the application starts"),
            self.tr("The new version will be more stable and have more features"),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup,
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr("About"), self.scrollWidget)
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr("Provide feedback"),
            FIF.FEEDBACK,
            self.tr("Provide feedback"),
            self.tr("Help us improve ScreenPinKit by providing feedback"),
            self.aboutGroup,
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr("Check update"),
            FIF.INFO,
            self.tr("About"),
            "© "
            + self.tr("Copyright")
            + f" {YEAR}, {AUTHOR}. "
            + self.tr("Version")
            + f" {VERSION}",
            self.aboutGroup,
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(600, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 30, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        # add cards to group
        self.generalGroup.addSettingCard(self.cacheFolderCard)
        self.generalGroup.addSettingCard(self.pluginMarketUrlCard)
        self.generalGroup.addSettingCard(self.pluginsFolderCard)
        self.generalGroup.addSettingCard(self.isAutoFindWindowCard)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.windowShadowStyleGroup.addSettingCard(self.windowShadowStyleFocusColorCard)
        self.windowShadowStyleGroup.addSettingCard(
            self.windowShadowStyleUnfocusColorCard
        )
        self.windowShadowStyleGroup.addSettingCard(
            self.windowShadowStyleUseRoundStyleCard
        )
        self.windowShadowStyleGroup.addSettingCard(
            self.windowShadowStyleIsSaveWithShadowCard
        )
        self.windowShadowStyleGroup.addSettingCard(
            self.windowShadowStyleisCopyWithShadowCard
        )

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.generalGroup)
        self.expandLayout.addWidget(self.pluginMarketGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.ocrLoaderSettingGroup)
        self.expandLayout.addWidget(self.windowShadowStyleGroup)
        self.expandLayout.addWidget(self.toolbarGroup)
        self.expandLayout.addWidget(self.hotkeyGroup)
        self.expandLayout.addWidget(self.loggerGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """set style sheet"""
        self.scrollWidget.setObjectName("scrollWidget")
        StyleSheet.SETTING_INTERFACE.apply(self)

    def __showRestartTooltip(self):
        """show restart tooltip"""
        InfoBar.warning(
            "",
            self.tr("Configuration takes effect after restart"),
            parent=self.window(),
        )

    def __onCacheFolderCardClicked(self):
        """cache folder card clicked slot"""
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), cfg.get(cfg.cacheFolder))
        if not folder or cfg.get(cfg.cacheFolder) == folder:
            return

        cfg.set(cfg.cacheFolder, folder)
        self.cacheFolderCard.setContent(folder)

    def __onPluginsFolderCardClicked(self):
        """plugins folder card clicked slot"""
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), cfg.get(cfg.pluginsFolder))
        if not folder or cfg.get(cfg.pluginsFolder) == folder:
            return

        cfg.set(cfg.pluginsFolder, folder)
        self.pluginsFolderCard.setContent(folder)

    def __onThemeChanged(self, theme: Theme):
        """theme changed slot"""
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __connectSignalToSlot(self):
        """connect signal to slot"""
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # general
        self.cacheFolderCard.clicked.connect(self.__onCacheFolderCardClicked)

        self.pluginsFolderCard.clicked.connect(self.__onPluginsFolderCardClicked)

        # about
        self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL))
        )
