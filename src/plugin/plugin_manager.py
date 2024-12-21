import importlib.util
import os, sys, glob, re, platform
import importlib
from qfluentwidgets import (
    InfoBar,
    InfoBarIcon,
    InfoBarPosition,
    FluentIcon as FIF,
    TransparentToolButton,
)
from .plugin_interface import PluginInterface, GlobalEventEnum
from .plugin_inst_config import PluginInstConfig
from .plugin_config import *
from common import *
from misc import *

class CustomLoader(importlib.abc.Loader):
    def __init__(self, module_code):
        self.module_code = module_code

    def exec_module(self, module):
        exec(self.module_code, module.__dict__)


class PluginManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pluginDict = {}
        self.pluginGroupDict = {}
        pluginCfg.load("plugin_settings.json")

    def loadPlugins(self):
        self.__loadPluginsInside()
        self.__loadPluginsOutside()
        self.__clearInvalidPluginCfgs()

    def __clearInvalidPluginCfgs(self):
        '''清除无效的插件配置(考虑到存在绕过插件UI而直接本地删除插件目录的情况，得兼容下)'''
        isSave = False
        for attrName in dir(pluginCfg):
            attr = getattr(pluginCfg, attrName)
            if isinstance(attr, PluginConfigItemEx):
                if self.pluginDict.get(attrName) == None:
                    delattr(pluginCfg, attrName)
                    isSave = True
        if isSave:
            pluginCfg.save()

    def __loadPluginsInside(self):
        internalPath = os.path.join(OsHelper.getInternalPath(), "internal_deps/internal_plugins")
        self.__loadPluginsByFolder(internalPath)

    def __loadPluginsOutside(self):
        folderPath = cfg.get(cfg.pluginsFolder)
        self.__loadPluginsByFolder(folderPath)

    def __loadPluginsByText(self, moduleName, text):
        loader = CustomLoader(text)
        spec = importlib.util.spec_from_loader(moduleName, loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.__filterInterface(module)

    def __loadPluginsByFilePath(self, moduleName, filePath):
        file = QFile(filePath)
        # 打开文件，只读模式
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            # 创建 QTextStream 对象
            stream = QTextStream(file)
            stream.setCodec("utf-8")

            # 读取文件内容
            text = stream.readAll()
            self.__loadPluginsByText(moduleName, text)

    # def __loadPluginsByFilePathBak(self, moduleName, filePath):
    #     '''该方法不支持从qt资源文件里读取，因此弃用'''
    #     spec = importlib.util.spec_from_file_location(moduleName, filePath)
    #     module = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(module)
    #     self.__filterInterface(module)

    def __loadPluginsByFolder(self, folderPath):
        '''遍历指定路径下所有包含PluginInterface的py文件，并作为插件导入'''
        for root, dirs, files in os.walk(folderPath):
            isAppendSysPath = False
        
            # 打印当前目录中的文件
            for fileName in files:
                if fileName.endswith(".py"):
                    maybePath = os.path.join(root, fileName)
                    # 检查文件内是否包含PluginInterface的子类
                    with open(maybePath, "r", encoding="utf-8") as f:
                        text = f.read()
                        isMatch = re.search(r"class.*PluginInterface", text)
                        if isMatch:
                            if not isAppendSysPath:
                                # 添加到sys.path中，以便导入模块
                                isAppendSysPath = True
                                sys.path.append(root)

                            moduleName = fileName[:-3]
                            if moduleName in ["plugin_inst_config", "plugin_manager"]:
                                continue
                            try:
                                module = importlib.import_module(moduleName)
                                pluginInst = self.__filterInterface(module)
                                if pluginInst != None:
                                    self.pluginGroupDict[pluginInst.name] = root
                            except Exception as e:
                                errorMessage = "\n".join(e.args)
                                print(f"{moduleName} load fail：{errorMessage}")

    def __loadPluginByModuleName(self, moduleName):
        module = importlib.import_module(moduleName)
        self.__filterInterface(module)

    def __filterInterface(self, module):
        for attrName in dir(module):
            attr = getattr(module, attrName)
            if (
                isinstance(attr, type)
                and issubclass(attr, PluginInterface)
                and attr != PluginInterface
                and attr != PluginInstConfig
            ):
                pluginInst = attr()
                if pluginInst.name in self.pluginDict:
                    continue

                pluginInst.enable = pluginCfg.isOnByPluginName(pluginInst.name)
                self.pluginDict[pluginInst.name] = pluginInst
                if pluginInst.enable:
                    pluginInst.onLoaded()

                return pluginInst

    def handleEvent(self, eventName: GlobalEventEnum, *args, **kwargs):
        for plugin0 in self.pluginDict.values():
            plugin: PluginInterface = plugin0
            if plugin.enable:
                try:
                    plugin.handleEvent(eventName, *args, **kwargs)
                except Exception as e:
                    print("\n".join(e.args))

    def reloadPlugins(self):
        for plugin0 in self.pluginDict.values():
            plugin: PluginInterface = plugin0
            if plugin.enable:                
                plugin.enable = False

        self.pluginDict.clear()
        self.pluginGroupDict.clear()
        self.loadPlugins()

    def installNetworkPlugin(self, parentWidget:QWidget, targetPluginName: str, gitUrl: str) -> bool:
        try:
            self.__installNetworkPlugin(targetPluginName, gitUrl)
            return True
        except Exception as e:
            if hasattr(e, "stderr"):
                _importErrorMsg = e.stderr
            else:
                _importErrorMsg = "\n".join(e.args)
            self.__showErrBar(parentWidget, "插件安装失败", _importErrorMsg)
            return False

    def __installNetworkPlugin(self, targetPluginName: str, gitUrl: str):
        pluginInst = self.pluginDict.get(targetPluginName)
        if not pluginInst == None:
            return

        outsidePluginFolderPath = cfg.get(cfg.pluginsFolder)
        if platform.system() == "Windows":
            fullCmd = f"cd /d {outsidePluginFolderPath} & git clone {gitUrl}"
        else:
            fullCmd = f"cd {outsidePluginFolderPath} ; git clone {gitUrl}"
        OsHelper.executeSystemCommand(fullCmd)

    def unInstallNetworkPlugin(self, parentWidget:QWidget, targetPluginName: str) -> bool:
        try:
            self.__unInstallNetworkPlugin(targetPluginName)
            return True
        except Exception as e:
            if hasattr(e, "stderr"):
                _importErrorMsg = e.stderr
            else:
                _importErrorMsg = "\n".join(e.args)
            self.__showErrBar(parentWidget, "插件卸载失败", _importErrorMsg)
            return False

    def __unInstallNetworkPlugin(self, targetPluginName: str):
        dirPath:str = self.pluginGroupDict[targetPluginName]

        if platform.system() == "Windows":
            dirPath = dirPath.replace("/", "\\")
            fullCmd = f"rd /s /q {dirPath}"
        else:
            dirPath = dirPath.replace("\\", "/")
            fullCmd = f"rm -rf {dirPath}"
        OsHelper.executeSystemCommand(fullCmd)

    def __showErrBar(self, parentWidget:QWidget, title:str, errMsg:str):
        infoBar = InfoBar(
            icon=InfoBarIcon.ERROR,
            title=title,
            content=errMsg,
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

    def copyText(self, infoBar: InfoBar):
        text = infoBar.contentLabel.text()
        QApplication.clipboard().setText(text)

pluginMgr = PluginManager()
