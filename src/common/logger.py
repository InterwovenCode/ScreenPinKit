# coding:utf-8
import os
import sys
import logging
import datetime
from logging.handlers import RotatingFileHandler
from PyQt5.QtCore import QObject

class Logger(QObject):
    """统一的日志系统，支持控制台和文件输出"""

    # 日志级别映射
    LEVEL_MAP = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self.loggers = {}
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # 创建默认日志记录器
        self.setup_logger("app")

    def setup_logger(self, name, level="INFO", max_size=10*1024*1024, backup_count=5):
        """设置一个命名的日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别，默认INFO
            max_size: 单个日志文件最大大小，默认10MB
            backup_count: 保留的日志文件数量，默认5个
        """
        if name in self.loggers:
            return self.loggers[name]
            
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(self.LEVEL_MAP.get(level, logging.INFO))
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
            
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
        
        # 创建文件处理器
        log_file = os.path.join(self.log_dir, f"{name}.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        self.loggers[name] = logger
        return logger
    
    def get_logger(self, name="app"):
        """获取指定名称的日志记录器，如果不存在则创建"""
        if name not in self.loggers:
            return self.setup_logger(name)
        return self.loggers[name]
    
    def debug(self, msg, *args, logger_name="app", **kwargs):
        """记录DEBUG级别日志"""
        logger = self.get_logger(logger_name)
        logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, logger_name="app", **kwargs):
        """记录INFO级别日志"""
        logger = self.get_logger(logger_name)
        logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, logger_name="app", **kwargs):
        """记录WARNING级别日志"""
        logger = self.get_logger(logger_name)
        logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, logger_name="app", **kwargs):
        """记录ERROR级别日志"""
        logger = self.get_logger(logger_name)
        logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, logger_name="app", **kwargs):
        """记录CRITICAL级别日志"""
        logger = self.get_logger(logger_name)
        logger.critical(msg, *args, **kwargs)


# 创建全局日志实例
logger = Logger()