import os, sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from ocr_loader import *
from PIL import Image
import numpy as np

try:
    from PaddleOCRModel.PaddleOCRModel import det_rec_functions as OcrDetector

    _currentOcrMode = EnumOcrMode.UseInside
except ImportError:
    _currentOcrMode = EnumOcrMode.UseOutside


def qpixmapToMatlike(qpixmap: QPixmap):
    if isinstance(qpixmap, np.ndarray):
        return qpixmap

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


class InternalOcrLoader_ReturnJson(OcrLoaderInterface):
    @property
    def name(self):
        return "InternalOcrLoader_ReturnJson"

    @property
    def displayName(self):
        return "Paddle2Onnx-返回Json"

    @property
    def desc(self):
        return "采用PaddleOCR的ONNX模型进行OCR识别，返回Json"

    @property
    def mode(self):
        return EnumOcrMode.UseInside

    @property
    def returnType(self):
        return EnumOcrReturnType.Json

    def ocr(self, pixmap: QPixmap):
        """
        调用ocr模块来进行OCR识别
        @note 由于ocr操作耗时较长，该函数会阻塞当前线程
        @bug 本地经过多番尝试，发现只要调用PaddleOCR.ocr()必定会导致程序崩溃，
            无关乎创建多个PaddleOCR对象还是创建多线程来执行都崩，最终采取命令行方式绕过该崩溃
        @later 后续可能会采取内建ocrweb服务的方式来提供，暂时先搁置它
        """
        if _currentOcrMode == EnumOcrMode.NoSupport:
            return [], [], []

        start_time = time.time()
        print("[ocr-loader:json] ocr start", flush=True)
        matlike = qpixmapToMatlike(pixmap)
        print(f"[ocr-loader:json] matlike shape={matlike.shape}", flush=True)

        ocr_sys = OcrDetector(matlike, use_dnn=False, version=3)  # 支持v2和v3版本的
        print("[ocr-loader:json] get_boxes start", flush=True)
        dt_boxes = ocr_sys.get_boxes()
        box_count = len(dt_boxes[0]) if len(dt_boxes) > 0 else 0
        print(f"[ocr-loader:json] get_boxes end count={box_count}", flush=True)
        print("[ocr-loader:json] recognition_img start", flush=True)
        results, results_info = ocr_sys.recognition_img(dt_boxes)
        print(f"[ocr-loader:json] recognition_img end results={len(results)}", flush=True)
        print("[ocr-loader:json] get_match_text_boxes start", flush=True)
        match_text_boxes = ocr_sys.get_match_text_boxes(dt_boxes[0], results)
        print(
            f"[ocr-loader:json] get_match_text_boxes end count={len(match_text_boxes)}",
            flush=True,
        )

        data = []
        for info in match_text_boxes:
            text = info["text"]
            left = float(info["box"][0][0])
            top = float(info["box"][0][1])
            right = float(info["box"][1][0])
            bottom = float(info["box"][2][1])

            left_top = [left, top]
            right_top = [right, top]
            right_bottom = [right, bottom]
            left_bottom = [left, bottom]
            box = [left_top, right_top, right_bottom, left_bottom]
            score = 0.97
            data.append({"text": text, "box": box, "score": score})

        print(
            f"[ocr-loader:json] result built count={len(data)} elapsed={time.time() - start_time:.3f}s",
            flush=True,
        )
        return {"code": 100, "data": data}
