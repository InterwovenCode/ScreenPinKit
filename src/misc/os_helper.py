import os, sys, inspect, subprocess, hashlib
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PIL import Image
import numpy as np


class OsHelper:
    offsetPos = QPoint(20, 20)

    @staticmethod
    def executeSystemCommand(cmd):
        """
        执行系统shell命令的函数
        @note: 该函数会阻塞当前线程
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ,
                encoding="utf-8",
            )
            output = result.stdout
            print("Command Result:\n", output)
        except subprocess.CalledProcessError as e:
            # 如果命令执行出错，打印错误信息
            print("An error occurred while executing the command.", e)
            raise e

    @staticmethod
    def calculateHashForQPixmap(pixmap: QPixmap, cutLength=0, hashAlgorithm="sha256"):
        """计算QPixmap的哈希值，根据需要可以截取对应哈希结果长度"""
        byteArray = Image.fromqpixmap(pixmap).tobytes()

        # 创建哈希对象
        hashObj = hashlib.new(hashAlgorithm)

        # 更新哈希对象
        hashObj.update(byteArray)

        # 获取哈希值的十六进制表示
        if cutLength > 0:
            result = hashObj.hexdigest()[0:cutLength]
        else:
            result = hashObj.hexdigest()

        return result

    @staticmethod
    def qpixmapToMatlike(qpixmap: QPixmap):
        # 将 QPixmap 转换为 QImage
        qimage = qpixmap.toImage()

        # # 获取 QImage 的宽度和高度
        # import cv2
        # width = qimage.width()
        # height = qimage.height()

        # # 将 QImage 转换为 numpy 数组
        # byteArray = qimage.bits().asstring(width * height * 4)  # 4 表示每个像素有 4 个字节（RGBA）
        # imageArray = np.frombuffer(byteArray, dtype=np.uint8).reshape((height, width, 4))
        # imageArray = cv2.cvtColor(imageArray, cv2.IMREAD_COLOR)

        image = Image.fromqimage(qimage)
        imageArray = np.array(image)
        return imageArray

    @staticmethod
    def loadFontFamilyFromQrc(font_path) -> str:
        qfile = QFile(font_path)
        if not qfile.open(QIODevice.ReadOnly):
            raise IOError("Failed to open font file from QRC")

        font_data = qfile.readAll()
        qfile.close()

        font_id = QFontDatabase.addApplicationFontFromData(font_data)
        if font_id == -1:
            raise IOError("Failed to load font from QRC")

        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if not font_families:
            raise IOError("Failed to get font family from QRC")

        return font_families[0]

    @staticmethod
    def textToImage(
        text,
        fontPath,
        fontSize=24,
        textColor=Qt.GlobalColor.black,
        bgColor=Qt.GlobalColor.white,
    ):
        """将文本转换成图像，返回QPixmap"""
        image = QImage(1, 1, QImage.Format_ARGB32)

        painter = QPainter(image)

        fontFamily = OsHelper.loadFontFamilyFromQrc(fontPath)
        font = QFont(fontFamily, fontSize)
        painter.setFont(font)

        # 获取文本的边界矩形
        rect = painter.boundingRect(image.rect(), Qt.AlignLeft, text)

        painter.end()

        # 调整图像大小以适应文本
        image = QImage(
            rect.width() + OsHelper.offsetPos.x() * 2,
            rect.height() + OsHelper.offsetPos.y() * 2,
            QImage.Format_ARGB32,
        )

        image.fill(bgColor)

        painter = QPainter(image)
        painter.setFont(font)

        painter.setPen(QColor(textColor))

        rect.moveTopLeft(OsHelper.offsetPos)
        painter.drawText(rect, Qt.AlignLeft, text)

        painter.end()

        return QPixmap.fromImage(image)

    @staticmethod
    def getColorStrByQColor(color: QColor, showColorMode: int) -> str:
        """将QColor转换成字符串，ShowColorMode: 0:hex, 1:rgb, 2:hsv"""
        if showColorMode == 0:
            return f"hex: {color.name()}"
        elif showColorMode == 1:
            return f"rgb: ({color.red()}, {color.green()}, {color.blue()})"
        elif showColorMode == 2:
            return f"hsv: ({color.hue()}, {color.saturation()}, {color.value()})"

    @staticmethod
    def tryTextToQColor(text: str) -> QColor:
        """将颜色文本转换为QColor并返回"""
        colorPrefixs = ["hex:", "rgb:", "hsv:"]
        result = None
        for prefix in colorPrefixs:
            if text.startswith(prefix):
                content = text.replace(prefix, "")
                content = content.strip(" ()")

                if prefix == "hex:":
                    result = QColor()
                    result.setNamedColor(content)
                elif prefix == "rgb:":
                    r, g, b = map(int, content.split(","))
                    result = QColor.fromRgb(r, g, b)
                elif prefix == "hsv:":
                    h, s, v = map(int, content.split(","))
                    result = QColor.fromHsv(h, s, v)
        return result

    @staticmethod
    def colorToImageEx(
        targetColor: QColor,
        fontPath: str,
        fontSize: int = 24,
        textColor: QColor = Qt.GlobalColor.black,
        bgColor: QColor = Qt.GlobalColor.white,
    ):
        """将颜色数值转换成图像，返回QPixmap"""
        hexStr = OsHelper.getColorStrByQColor(targetColor, 0)
        rgbStr = OsHelper.getColorStrByQColor(targetColor, 1)
        hsvStr = OsHelper.getColorStrByQColor(targetColor, 2)
        text = f"{hexStr}\n\n{rgbStr}\n\n{hsvStr}"
        pixmap = OsHelper.textToImage(text, fontPath, fontSize, textColor, bgColor)

        painter = QPainter(pixmap)
        boundPen = QPen(targetColor)
        boundPen.setStyle(Qt.PenStyle.SolidLine)
        boundPen.setWidthF(5)
        painter.setPen(boundPen)

        colorBound = pixmap.rect() - QMargins(
            OsHelper.offsetPos.x() / 2,
            OsHelper.offsetPos.y() / 2,
            OsHelper.offsetPos.x() / 2,
            OsHelper.offsetPos.y() / 2,
        )
        painter.drawRect(colorBound)

        painter.end()
        return pixmap

    @staticmethod
    def ConvertToRoundedPixmap(pixmap: QPixmap, radius: float):
        """让图像裁剪出圆角边缘"""
        finalPixmap = QPixmap(pixmap.size())

        # 注意，由于dpi缩放的影响，需要将其转换为逻辑坐标才能绘制正确
        finalPixmap.setDevicePixelRatio(pixmap.devicePixelRatioF())
        dpiScale = pixmap.devicePixelRatioF()
        logicRect = QRectF(
            0, 0, pixmap.size().width() / dpiScale, pixmap.size().height() / dpiScale
        )

        # 填充为透明背景
        finalPixmap.fill(Qt.transparent)

        painter = QPainter(finalPixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置裁剪区域
        path = QPainterPath()
        path.addRoundedRect(logicRect, radius, radius)
        painter.setClipPath(path)

        # 复制图像
        painter.drawPixmap(0, 0, pixmap)

        painter.end()

        return finalPixmap

    @staticmethod
    def getWebEngineFontFamily():
        from PyQt5.QtWebEngineWidgets import QWebEngineSettings

        settings = QWebEngineSettings.globalSettings()
        return settings.fontFamily(QWebEngineSettings.FantasyFont)

    @staticmethod
    def getSystemFontFamily():
        font_db = QFontDatabase()
        font_family = font_db.families()[0]
        return font_family

    @staticmethod
    def getCallerFilePath():
        stack = inspect.stack()
        # 获取调用该函数的帧（即调用栈的第三帧）
        callerFrame = stack[2]
        # 获取调用该函数的源文件路径
        callerFilePath = callerFrame.filename
        return callerFilePath

    @staticmethod
    def getInternalPath():
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            result = sys._MEIPASS
        else:
            # 如果是源码运行，目的是定位到src目录
            result = os.path.abspath(os.path.join(os.path.dirname(OsHelper.getCallerFilePath()), ".."))
    
        return result

    @staticmethod
    def explorerFile(path:str):
        if sys.platform.startswith("win32"):
            path = path.replace("/", "\\")
            QProcess.startDetached(f"explorer /select, \"{path}\"")
        elif sys.platform.startswith("linux"):
            path = path.replace("\\", "/")
            QProcess.startDetached(f"nautilus \"{path}\"")
        elif sys.platform.startswith("darwin"):
            pass