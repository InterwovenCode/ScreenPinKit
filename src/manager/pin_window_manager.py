import os, glob, re
from base import *
from view import *
from misc import *


class PinWindowManager:
    def __init__(self):
        super().__init__()
        self.screenDevicePixelRatio = CanvasUtil.getDevicePixelRatio()
        self._windowsDict = {}
        self.lastCropRect = None

        startupImagePath, screenX, screenY = self.findScreenImagePath()
        if startupImagePath != None and os.path.exists(startupImagePath):
            imgpix = QPixmap(startupImagePath)
            realSize = self.autoFitScreenPixelRatioForPixmap(imgpix)
            self.addPinWindow(QPoint(screenX, screenY), realSize, imgpix)

    def addPinWindow(self, screenPoint: QPoint, realSize: QSize, pixmap: QPixmap):
        hashCode = OsHelper.calculateHashForQPixmap(pixmap, 8)
        if not hashCode in self._windowsDict:
            self._windowsDict[hashCode] = PinEditorWindow(
                None,
                screenPoint,
                realSize,
                pixmap,
                lambda: self.handleWindowClose(hashCode),
            )

    def showClipboard(self):
        """将剪贴板上的图像数据作为冻结窗口"""
        clipboard = QApplication.clipboard()
        mimeData = clipboard.mimeData()

        def isImagePath(mimeData: QMimeData):
            if mimeData.hasUrls():
                imgPath = clipboard.text().replace("file:///", "")
                if not os.path.exists(imgPath):
                    return False
                extension = Path(imgPath).suffix
                supportImgs = [".png", ".jpg", ".jpeg", ".svg", ".webp", ".jfif"]
                return extension in supportImgs
            return False

        pixmap = None
        if mimeData.hasImage():
            image = clipboard.image()
            pixmap = QPixmap.fromImage(image)
        elif isImagePath(mimeData):
            imgPath = clipboard.text().replace("file:///", "")
            pixmap = QPixmap(imgPath)
        elif mimeData.hasText():
            text = clipboard.text()
            fontPath = ":/fonts/cangerjinxie01-9128-W03.otf"

            maybeColor = OsHelper.tryTextToQColor(text)
            if maybeColor != None:
                # 颜色文本
                pixmap = OsHelper.colorToImageEx(
                    targetColor=maybeColor, fontPath=fontPath, fontSize=18
                )
            else:
                # 普通文本
                pixmap = OsHelper.textToImage(text=text, fontPath=fontPath, fontSize=14)

        if pixmap != None:
            realSize = self.autoFitScreenPixelRatioForPixmap(pixmap)
            screenPoint = QCursor().pos() - QPoint(
                realSize.width() / 2, realSize.height() / 2
            )
            self.addPinWindow(screenPoint, realSize, pixmap)

    def autoFitScreenPixelRatioForPixmap(self, pixmap: QPixmap) -> QSize:
        """自动适配屏幕缩放比例"""
        screenDevicePixelRatio = CanvasUtil.getDevicePixelRatio()
        pixmap.setDevicePixelRatio(screenDevicePixelRatio)
        realSize = pixmap.size() / screenDevicePixelRatio
        return realSize

    def handleWindowClose(self, hashCode: str):
        widget: QWidget = self._windowsDict.pop(hashCode)
        widget.deleteLater()

    def switchMouseThroughState(self):
        """鼠标穿透策略：优先判断获取焦点窗口的"""
        pinWnd: PinWindow = None
        screenPos = QCursor.pos()
        for wnd0 in self._windowsDict.values():
            wnd: PinWindow = wnd0
            if wnd != None and wnd.geometry().contains(screenPos):
                pinWnd = wnd
                break
        if pinWnd != None:
            pinWnd.switchMouseThroughState()
        else:
            for wnd0 in self._windowsDict.values():
                wnd: PinWindow = wnd0
                if wnd != None:
                    wnd.setMouseThroughState(False)

    def recordCropRect(self, cropRect: QRectF):
        self.lastCropRect = cropRect

    def repeatSnip(self):
        if self.lastCropRect == None:
            return

        cropRect = self.lastCropRect
        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        pixelRatio = finalPixmap.devicePixelRatio()
        realCropRect = QRectF(
            cropRect.x() * pixelRatio,
            cropRect.y() * pixelRatio,
            cropRect.width() * pixelRatio,
            cropRect.height() * pixelRatio,
        ).toRect()
        if realCropRect.size() != QSize(0, 0):
            cropPixmap = finalPixmap.copy(realCropRect)
            cropImage = cropPixmap.toImage().convertToFormat(
                QImage.Format.Format_RGB888
            )
            cropPixmap = QPixmap.fromImage(cropImage)
            self.snip(cropRect, cropPixmap)

    def copyToClipboard(self, cropRect: QRectF):
        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        pixelRatio = finalPixmap.devicePixelRatio()
        realCropRect = QRectF(
            cropRect.x() * pixelRatio,
            cropRect.y() * pixelRatio,
            cropRect.width() * pixelRatio,
            cropRect.height() * pixelRatio,
        ).toRect()
        cropPixmap = finalPixmap.copy(realCropRect)
        kv = {"pixmap": cropPixmap}
        pluginMgr.handleEvent(GlobalEventEnum.ImageCopyingEvent, kv=kv, parent=self)
        finalPixmap = kv["pixmap"]
        QApplication.clipboard().setPixmap(finalPixmap)

    def snip(self, cropRect:QRectF, pixmap: QPixmap):
        if QPixmap.isNull(pixmap):
            self.copyToClipboard(cropRect)
        else:
            screenPoint = cropRect.topLeft().toPoint()
            realSize = cropRect.size().toSize()
            self.clearScreenImages()
            saveFolder = cfg.get(cfg.cacheFolder)
            savePath = os.path.join(saveFolder, self.getScreenImageName(screenPoint))
            pixmap.save(savePath, "png")
            self.addPinWindow(screenPoint, realSize, pixmap)
        self.recordCropRect(cropRect)

    def clearScreenImages(self):
        searchFolder = cfg.get(cfg.cacheFolder)
        searchPattern = "*.png"
        finalSearch = os.path.join(searchFolder, searchPattern)
        filePaths = glob.glob(finalSearch)
        for filePath in filePaths:
            matchResult = re.match(self.getImageNamePattern(), filePath)
            if matchResult != None and len(matchResult.groups()) > 0:
                os.remove(filePath)

    def getScreenImageName(self, screenPoint: QPoint):
        return f"screen {screenPoint.x()}-{screenPoint.y()}.png"

    def getImageNamePattern(self):
        return r".*screen ([-]*\d+)-([-]*\d+).png"

    def findScreenImagePath(self):
        searchFolder = cfg.get(cfg.cacheFolder)
        searchPattern = "*.png"
        finalSearch = os.path.join(searchFolder, searchPattern)
        filePaths = glob.glob(finalSearch)
        if len(filePaths) > 0:
            # 遍历filePaths中的文件路径
            for filePath in filePaths:
                matchResult = re.match(self.getImageNamePattern(), filePath)

                if matchResult != None:
                    x = int(matchResult.group(1))
                    y = int(matchResult.group(2))
                    return filePath, x, y
        return None, 0, 0
