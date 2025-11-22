from enum import Enum
from typing import Any, Dict

from extend_widgets import *


class EnumItemCardState(Enum):
    NoneState = -1 # 未知
    UninstallState = 0 # 未安装
    ActiveState = 1 # 已安装且已启用
    DeActiveState = 2 # 已安装但未启用

class PluginConfigItem(ConfigItem):
    """ Config item with options """

    @property
    def options(self) -> Any:
        return self.validator.options

    @property
    def isIgnored(self) -> bool:
        return False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[options={self.options}, value={self.value}]'

class PluginConfigItemEx(PluginConfigItem):
    """ Config item with options """
    def __init__(self, group: str, name: str, default: EnumItemCardState) -> None:
        super().__init__(group, name, default, OptionsValidator(EnumItemCardState), EnumSerializer(EnumItemCardState))

    @property
    def isIgnored(self) -> bool:
        if self.value in [EnumItemCardState.NoneState, EnumItemCardState.UninstallState]:
            return True
        return False

class QPluginConfig(QObject):
    """ 
    Config of plugin，支持动态拓展属性
    参考QConfig实现
    """

    def __init__(self) -> None:
        super().__init__()
        self.file = Path("config/config.json")
        self._cfg = self

    def get(self, item: ConfigItem) -> Any:
        """ get the value of config item """
        return item.value

    def set(self, item: ConfigItem, value: Any, save: bool = True, copy: bool = True) -> None:
        """ set the value of config item

        Parameters
        ----------
        item: ConfigItem
            config item

        value:
            the new value of config item

        save: bool
            whether to save the change to config file

        copy: bool
            whether to deep copy the new value
        """
        if item.value == value:
            return

        # deepcopy new value
        try:
            item.value = deepcopy(value) if copy else value
        except:
            item.value = value

        if save:
            self.save()

    def toDict(self, serialize: bool = True) -> Dict[str, Any]:
        """ convert config items to `dict` """
        items: Dict[str, Any] = {}
        for name in dir(self._cfg):
            item = getattr(self._cfg, name)
            if not isinstance(item, ConfigItem):
                continue

            if isinstance(item, PluginConfigItem):
                if item.isIgnored:
                    continue

            value = item.serialize() if serialize else item.value
            if not items.get(item.group):
                if not item.name:
                    items[item.group] = value
                else:
                    items[item.group] = {}

            if item.name:
                items[item.group][item.name] = value

        return items

    def save(self) -> None:
        """ save config """
        self._cfg.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cfg.file, "w", encoding="utf-8") as f:
            json.dump(self._cfg.toDict(), f, ensure_ascii=False, indent=4)

    @exceptionHandler()
    def load(self, file=None, config=None) -> None:
        """ load config

        Parameters
        ----------
        file: str or Path
            the path of json config file

        config: Config
            config object to be initialized
        """
        if isinstance(config, QPluginConfig):
            self._cfg = config

        if isinstance(file, (str, Path)):
            self._cfg.file = Path(file)

        try:
            with open(self._cfg.file, encoding="utf-8") as f:
                cfg = json.load(f)
        except:
            cfg = {}

        # map config items'key to item
        items: Dict[str, ConfigItem] = {}
        for name in dir(self._cfg):
            item = getattr(self._cfg, name)
            if isinstance(item, ConfigItem):
                items[item.key] = item

        # update the value of config item
        for k, v in cfg.items():
            if not isinstance(v, dict) and items.get(k) is not None:
                items[k].deserializeFrom(v)
            elif isinstance(v, dict):
                for key0, value in v.items():
                    key = k + "." + key0

                    if items.get(key) is None:
                        configItem = PluginConfigItemEx(k, key0, EnumItemCardState.UninstallState)
                        setattr(self._cfg, k, configItem)
                        item = getattr(self._cfg, k)
                        item.deserializeFrom(value)
                        items[item.key] = item
                    else:
                        items[key].deserializeFrom(value)

    def isOnByPluginName(self, pluginName):
        # 如果插件目录里已经包含该插件，那么默认该插件已开启
        if not hasattr(self._cfg, pluginName):
            return True

        configItem = getattr(self._cfg, pluginName)
        result = self.get(configItem)
        return result == EnumItemCardState.ActiveState

pluginCfg = QPluginConfig()