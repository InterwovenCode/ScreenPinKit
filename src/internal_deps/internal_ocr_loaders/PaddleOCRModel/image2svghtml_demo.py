import os, sys, argparse, html
from PaddleOCRModel import det_rec_functions as OcrDetector
import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from html_builder import build_svg_html as build_svg_html


def image2svghtml(input, output, dpi_scale=1):
    """将图片进行OCR识别后，将结果转换成html"""
    matlike = cv2.imread(input, cv2.IMREAD_COLOR)
    if matlike is None:
        raise ValueError(f"Unable to read image: {input}")
    height, width = matlike.shape[:2]

    # 使用 PaddleOCR 进行 OCR 识别
    # result = ocr.ocr(input, cls=True)
    with open(input, "rb") as f:
        img_bytes = f.read()
        # 从字节数组读取图像
        np_array = np.frombuffer(img_bytes, np.uint8)
        matlike = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    ocr_sys = OcrDetector(matlike, use_dnn=False, version=3)  # 支持v2和v3版本的
    dt_boxes = ocr_sys.get_boxes()
    results, results_info = ocr_sys.recognition_img(dt_boxes)
    match_text_boxes = ocr_sys.get_match_text_boxes(dt_boxes[0], results)

    temp_image = ocr_sys.draw_boxes(dt_boxes[0], matlike)
    cv2.imwrite("testocr.png", temp_image)

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

    html_content = build_svg_html(
        width=width, height=height, boxes=boxes, txts=txts, dpi_scale=dpi_scale
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)


def main(args):
    input_path = args.input_path
    output_path = args.output_path
    dpi_scale = args.dpi_scale
    image2svghtml(input_path, output_path, dpi_scale)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str)
    parser.add_argument("--output_path", type=str)
    parser.add_argument("--dpi_scale", type=float)

    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
