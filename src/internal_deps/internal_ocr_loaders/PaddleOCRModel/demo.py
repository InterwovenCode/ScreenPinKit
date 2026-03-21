import os
import sys
import time
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
from qt_image_util import qpixmap_to_bgr_ndarray
from PaddleOCRModel import det_rec_functions as OcrDetector


def qpixmap_to_matlike(qpixmap: QPixmap):
    return qpixmap_to_bgr_ndarray(qpixmap)


class OcrimgThread(QThread):
    """文字识别线程"""

    result_show_signal = pyqtSignal(str)
    statusbar_signal = pyqtSignal(str)
    det_res_img = pyqtSignal(QPixmap)  # 返回文字监测结果
    boxes_info_signal = pyqtSignal(list)  # 返回识别信息结果

    def __init__(self, image):
        super(QThread, self).__init__()
        self.image = image  # img
        self.ocr_result = None
        self.ocr_sys = None

    def get_match_text(self, match_text_boxes):
        if self.ocr_sys is not None:
            return self.ocr_sys.get_format_text(match_text_boxes)

    def run(self):
        self.statusbar_signal.emit("正在识别文字...")
        try:
            self.ocr_sys = OcrDetector(
                self.image, use_dnn=False, version=3
            )  # 支持v2和v3版本的
            stime = time.time()
            # 得到检测框
            dt_boxes = self.ocr_sys.get_boxes()
            image = self.ocr_sys.draw_boxes(dt_boxes[0], self.image)
            # cv2.imwrite("testocr.png",image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # 创建QImage对象
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            qimage = QImage(
                image.data, width, height, bytesPerLine, QImage.Format_RGB888
            )

            # 创建QPixmap对象
            qpixmap = QPixmap.fromImage(qimage)
            self.det_res_img.emit(qpixmap)

            dettime = time.time()
            print(len(dt_boxes[0]))
            if len(dt_boxes[0]) == 0:
                text = "<没有识别到文字>"
            else:
                # 识别 results: 单纯的识别结果，results_info: 识别结果+置信度    原图
                # 识别模型固定尺寸只能100长度，需要处理可以根据自己场景导出模型 1000
                # onnx可以支持动态，不受限
                results, results_info = self.ocr_sys.recognition_img(dt_boxes)
                print("识别时间:", time.time() - dettime, dettime - stime)
                match_text_boxes = self.ocr_sys.get_match_text_boxes(
                    dt_boxes[0], results
                )
                text = self.ocr_sys.get_format_text(match_text_boxes)
                self.boxes_info_signal.emit(match_text_boxes)

        except Exception as e:
            print("Unexpected error:", e, "jampublic l326")
            text = str(sys.exc_info()[0])
            self.statusbar_signal.emit("识别出错！{}".format(text))

        if text == "":
            text = "没有识别到文字"
        self.ocr_result = text
        self.result_show_signal.emit(text)
        self.statusbar_signal.emit("识别完成！")

        print("识别完成")


class OcrService:
    def __init__(self):
        pass

    def ocr(self, image_path):
        with open(image_path, "rb") as f:
            img_bytes = f.read()
            # 从字节数组读取图像
            np_array = np.frombuffer(img_bytes, np.uint8)
            cv_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        self.ocr_status = "ocr"
        self.ocrthread = OcrimgThread(cv_image)
        self.ocrthread.result_show_signal.connect(self.ocr_res_signalhandle)
        self.ocrthread.boxes_info_signal.connect(self.orc_boxes_info_callback)
        self.ocrthread.det_res_img.connect(self.det_res_img_callback)
        self.ocrthread.start()

    def ocr_res_signalhandle(self, text):
        if self.ocr_status == "ocr":
            print(text)
            self.ocr_status = "show"

    def orc_boxes_info_callback(self, text_boxes):
        if self.ocr_status == "ocr":
            for tb in text_boxes:
                tb["select"] = False
            self.ocr_res_info = text_boxes
            print("rec orc_boxes_info_callback")

    def det_res_img_callback(self, piximg):
        if self.ocr_status == "ocr":
            print("rec det_res_img_callback")


def directMain():
    app = QApplication(sys.argv)
    workDir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    image_path = f"{workDir}/11.png"
    print("正在识别图片：\t" + image_path)

    cv_image = qpixmap_to_matlike(QPixmap(image_path))

    ocr_sys = OcrDetector(cv_image, use_dnn=False, version=3)  # 支持v2和v3版本的
    dt_boxes = ocr_sys.get_boxes()
    image = ocr_sys.draw_boxes(dt_boxes[0], cv_image)
    cv2.imwrite(f"{workDir}/testocr.png", image)

    results, results_info = ocr_sys.recognition_img(dt_boxes)
    match_text_boxes = ocr_sys.get_match_text_boxes(dt_boxes[0], results)
    text = ocr_sys.get_format_text(match_text_boxes)
    print(f"results :{str(text)}")


def threadMain():
    app = QApplication(sys.argv)

    workDir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    service = OcrService()
    service.ocr(f"{workDir}/00.png")

    sys.exit(app.exec())


def main():
    directMain()
    # threadMain()


if __name__ == "__main__":
    main()
