import sys, os

from PyQt5.QtCore import QCoreApplication, QTranslator, Qt
from PyQt5.QtWidgets import QApplication, QWidget
from qfluentwidgets import Action, FluentTranslator, Icon

from common import cfg, logger, ScreenShotIcon
from common.hotkey import KeyboardEx
from view.system_tray_icon import SystemTrayIcon
from view.screen_shot_window import ScreenShotWindow
from view.screen_paint_window import ScreenPaintWindow
from view.setting_window import SettingWindow
from manager.pin_window_manager import PinWindowManager
from base.app_dpi_helper import AppDpiHelper
from version.version import APP_NAME
from plugin import pluginMgr, GlobalEventEnum
from ocr_loader.ocr_loader_manager import ocrLoaderMgr

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settingWindow = None
        self.keyObj = None
        self.screenShotWindow = None
        self.screenPaintWindow = None
        self.initPluginManager()
        self.initSystemTrayMenu()
        self.initPinWindowManager()
        self.initHotKey()

    def initPluginManager(self):
        logger.info("初始化插件管理器")
        pluginMgr.loadPlugins()
        logger.info("初始化OCR加载器")
        ocrLoaderMgr.initLoaders()

    def initPinWindowManager(self):
        self.pinWindowMgr = PinWindowManager()

    def initSystemTrayMenu(self):
        trayMenuActions = [
            Action(ScreenShotIcon.SNAP, self.tr("Snap"), triggered=self.screenShot),
            Action(
                ScreenShotIcon.SETTING,
                self.tr("Preferences"),
                triggered=self.showSettingWindow,
            ),
            Action(ScreenShotIcon.QUIT, self.tr("Exit"), triggered=self.exit),
        ]
        self.systemTrayIcon = SystemTrayIcon(
            self, APP_NAME, Icon(ScreenShotIcon.LOGO), trayMenuActions, self.screenShot
        )
        self.systemTrayIcon.show()

    def initHotKey(self):
        if self.keyObj == None:
            self.keyObj = KeyboardEx()
        pluginMgr.handleEvent(
            GlobalEventEnum.GlobalHotKeyRegisterStart, keyboard=self.keyObj
        )
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyShowClipboard), self.showClipboard)
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyScreenPaint), self.screenPaint)
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyScreenShot), self.screenShot)
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyRepeatScreenShot), self.repeatScreenShot)
        self.keyObj.addHotKey(
            cfg.get(cfg.hotKeyToggleMouseClickThrough), self.switchMouseThroughState
        )
        self.keyObj.addHotKey(
            cfg.get(cfg.hotKeySwitchScreenPaintMode), self.switchScreenPaintMode
        )
        pluginMgr.handleEvent(
            GlobalEventEnum.GlobalHotKeyRegisterEnd, keyboard=self.keyObj
        )

    def repeatScreenShot(self):
        self.pinWindowMgr.repeatSnip()

    def screenShot(self):
        logger.info("执行屏幕截图操作")
        if self.screenShotWindow == None:
            logger.debug("创建新的截图窗口")
            self.screenShotWindow = ScreenShotWindow()
            self.screenShotWindow.snipedSignal.connect(self.pinWindowMgr.snip)
            self.screenShotWindow.closedSignal.connect(self.onScreenShotWindowClosed)
        self.screenShotWindow.reShow()

    def screenPaint(self):
        if self.screenPaintWindow == None:
            self.screenPaintWindow = ScreenPaintWindow()
            self.screenPaintWindow.show()
        else:
            self.screenPaintWindow.startDraw()

    def showClipboard(self):
        self.pinWindowMgr.showClipboard()

    def showSettingWindow(self):
        if self.settingWindow == None:
            self.settingWindow = SettingWindow()
        self.settingWindow.show()

    def switchScreenPaintMode(self):
        if self.screenPaintWindow == None:
            return

        if self.screenPaintWindow.isVisible():
            self.screenPaintWindow.canvasEditor.completeDraw()
            self.screenPaintWindow.hide()
        else:
            self.screenPaintWindow.show()

    def switchMouseThroughState(self):
        self.pinWindowMgr.switchMouseThroughState()

    def onScreenShotWindowClosed(self):
        self.screenShotWindow.deleteLater()
        self.screenShotWindow = None

    def exit(self):
        QCoreApplication.quit()


def fixWebEngineViewCrash():
    # 修复QWebEngineView偶现卡死的问题，参考：https://bbs.csdn.net/topics/611959180
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)
    os.putenv("QMLSCENE_DEVICE", "softwarecontext")


def main():
    appDpiHelper = AppDpiHelper()
    if not appDpiHelper.tryApplyDpiConfig():
        return
        
    # 初始化日志系统
    logger.info("应用程序启动", logger_name="app")
    logger.info(f"日志级别: {cfg.get(cfg.logLevel)}", logger_name="app")
    logger.info(f"文件日志: {'启用' if cfg.get(cfg.enableFileLogging) else '禁用'}", logger_name="app")

    # create application
    fixWebEngineViewCrash()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", ":/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    MainWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
