import os, sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from ocr_loader import *
from qt_image_util import qpixmap_to_bgr_ndarray
import numpy as np


def get_ocr_dpi_scale():
    return float(os.environ.get("SCREENPINKIT_OCR_DPI_SCALE", "1"))

try:
    from PaddleOCRModel.PaddleOCRModel import det_rec_functions as OcrDetector

    _importErrorMsg = None
except ImportError as e:
    _importErrorMsg = "\n".join(e.args)


def qpixmapToMatlike(qpixmap: QPixmap):
    if isinstance(qpixmap, np.ndarray):
        return qpixmap

    return qpixmap_to_bgr_ndarray(qpixmap)


class InternalOcrLoader_ReturnTextPlus(OcrLoaderInterface):
    @property
    def name(self):
        return "InternalOcrLoader_ReturnTextPlus"

    @property
    def displayName(self):
        return "Paddle2Onnx-返回TextPlus"

    @property
    def desc(self):
        return "采用PaddleOCR的ONNX模型进行OCR识别，返回版面分析后的Text"

    @property
    def mode(self):
        return EnumOcrMode.UseInside

    @property
    def returnType(self):
        return EnumOcrReturnType.Text

    def ocr(self, pixmap: QPixmap):
        start_time = time.time()
        print("[ocr-loader:text-plus] ocr start", flush=True)
        boxes, texts, scores = self.__ocr(pixmap)
        print(
            f"[ocr-loader:text-plus] raw ocr returned boxes={len(boxes)} texts={len(texts)} elapsed={time.time() - start_time:.3f}s",
            flush=True,
        )
        if isinstance(pixmap, np.ndarray):
            height, width = pixmap.shape[:2]
        else:
            width = pixmap.size().width()
            height = pixmap.size().height()
        boxInfos = []
        for i, box in enumerate(boxes):
            text = texts[i]
            score = scores[i]
            boxInfos.append({"box": box, "text": text, "score": score})
        font_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "PaddleOCRModel/arial.ttf"
        )
        print(
            f"[ocr-loader:text-plus] building html width={width} height={height} boxes={len(boxInfos)}",
            flush=True,
        )
        if len(boxInfos) == 0:
            print("[ocr-loader:text-plus] no boxes, skip gap tree sort", flush=True)
            htmlContent = build_svg_html(
                font_path=font_path,
                width=width,
                height=height,
                box_infos=boxInfos,
                dpi_scale=get_ocr_dpi_scale(),
            )
        else:
            htmlContent = build_svg_html_by_gap_tree_sort(
                font_path=font_path,
                width=width,
                height=height,
                box_infos=boxInfos,
                dpi_scale=get_ocr_dpi_scale(),
            )
        print(
            f"[ocr-loader:text-plus] html built len={len(htmlContent)} elapsed={time.time() - start_time:.3f}s",
            flush=True,
        )
        return htmlContent

    def __ocr(self, pixmap: QPixmap):
        """
        调用ocr模块来进行OCR识别
        @note 由于ocr操作耗时较长，该函数会阻塞当前线程
        @bug 本地经过多番尝试，发现只要调用PaddleOCR.ocr()必定会导致程序崩溃，
            无关乎创建多个PaddleOCR对象还是创建多线程来执行都崩，最终采取命令行方式绕过该崩溃
        @later 后续可能会采取内建ocrweb服务的方式来提供，暂时先搁置它
        """
        if _importErrorMsg != None:
            raise Exception(_importErrorMsg)

        matlike = qpixmapToMatlike(pixmap)
        print(f"[ocr-loader:text-plus] matlike shape={matlike.shape}", flush=True)

        ocr_sys = OcrDetector(matlike, use_dnn=False, version=3)  # 支持v2和v3版本的
        print("[ocr-loader:text-plus] get_boxes start", flush=True)
        dt_boxes = ocr_sys.get_boxes()
        box_count = len(dt_boxes[0]) if len(dt_boxes) > 0 else 0
        print(f"[ocr-loader:text-plus] get_boxes end count={box_count}", flush=True)
        print("[ocr-loader:text-plus] recognition_img start", flush=True)
        results, results_info = ocr_sys.recognition_img(dt_boxes)
        print(f"[ocr-loader:text-plus] recognition_img end results={len(results)}", flush=True)
        print("[ocr-loader:text-plus] get_match_text_boxes start", flush=True)
        match_text_boxes = ocr_sys.get_match_text_boxes(dt_boxes[0], results)
        print(
            f"[ocr-loader:text-plus] get_match_text_boxes end count={len(match_text_boxes)}",
            flush=True,
        )

        boxes = []
        txts = []
        scores = []

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
            boxes.append([left_top, right_top, right_bottom, left_bottom])
            txts.append(text)
            scores.append(0.97)

        return boxes, txts, scores
