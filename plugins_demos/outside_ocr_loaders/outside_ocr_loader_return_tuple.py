import os, sys, codecs, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from ocr_loader import *
from misc import *

class OutsideOcrLoader_ReturnTuple(OcrLoaderInterface):
    @property
    def name(self):
        return "OutsideOcrLoader_ReturnTuple"

    @property
    def desc(self):
        return "采用外部OCR来进行OCR识别，返回Tuple"

    @property
    def mode(self):
        return EnumOcrMode.UseOutside

    @property
    def returnType(self):
        return EnumOcrReturnType.Tuple

    def ocr(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且结果传递回来
        @note 该函数会阻塞当前线程
        '''
        boxes, txts, scores = [], [], []
        workDir = os.path.dirname(__file__)

        hashCode = OsHelper.calculateHashForQPixmap(pixmap, 8)
        fileName = f"ocr_{hashCode}"
        ocrTempDirPath = os.path.join(workDir, "ocr_temp")
        if not os.path.exists(ocrTempDirPath):
            os.mkdir(ocrTempDirPath)

        imagePath = os.path.join(ocrTempDirPath, f"{fileName}.png")
        if not os.path.exists(imagePath):
            pixmap.save(imagePath)

        ocrResultPath = f"{imagePath}.ocr"
        if not os.path.exists(ocrResultPath):
            ocrRunnerBatPath = os.path.join(workDir, "deps/try_paddle_ocr_runner.bat") 
            # ocrRunnerBatPath = os.path.join(workDir, "deps/try_tessact_ocr_runner.bat") 
            fullCmd = f"{ocrRunnerBatPath} {imagePath} {ocrResultPath}"
            print(fullCmd)
            OsHelper.executeSystemCommand(fullCmd)

        # 读取缓存文件夹上的ocr识别结果 
        if os.path.exists(ocrResultPath):
            with codecs.open(ocrResultPath, mode="r", encoding="utf-8", errors='ignore') as f:
                json_str = f.read()
                ocrResult = json.loads(json_str)

                boxes = json.loads(ocrResult["boxes"])
                txts = json.loads(ocrResult["txts"])
                scores = json.loads(ocrResult["scores"])
                f.close()

        # if os.path.exists(imagePath):
        #     os.remove(imagePath)
        # if os.path.exists(ocrResultPath):
        #     os.remove(ocrResultPath)

        return boxes, txts, scores