# coding:utf-8
from common import cfg, ScreenShotIcon
from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    OptionsSettingCard,
    FluentIcon as FIF
)
from PyQt5.QtCore import Qt


class LoggerSettingCardGroup(SettingCardGroup):
    """Logger card group"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        
        self.logLevelCard = OptionsSettingCard(
            cfg.logLevel,
            FIF.TAG,
            self.tr("Log Level"),
            self.tr("Set the minimum level of log messages to record"),
            texts=[
                self.tr("DEBUG"), 
                self.tr("INFO"), 
                self.tr("WARNING"), 
                self.tr("ERROR"), 
                self.tr("CRITICAL")
            ],
            parent=self
        )
        
        self.enableFileLoggingCard = SwitchSettingCard(
            FIF.SAVE,
            self.tr("Enable File Logging"),
            self.tr("Save log messages to files in the logs directory"),
            configItem=cfg.enableFileLogging,
            parent=self
        )
        
        self.addSettingCard(self.logLevelCard)
        self.addSettingCard(self.enableFileLoggingCard)