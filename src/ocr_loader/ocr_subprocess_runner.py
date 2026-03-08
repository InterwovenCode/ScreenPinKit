# coding=utf-8
import argparse
import os
import pickle
import sys
import time
import traceback

import numpy as np


def log(message: str):
    print(f"[ocr-child] {message}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loader", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dpi-scale", default="1")
    args = parser.parse_args()

    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    start_time = time.time()
    os.environ["SCREENPINKIT_OCR_DPI_SCALE"] = args.dpi_scale
    log(f"start loader={args.loader} input={args.input} dpi_scale={args.dpi_scale}")

    try:
        from ocr_loader.ocr_loader_manager import ocrLoaderMgr

        log("loading image array")
        image = np.load(args.input)
        log(f"image loaded shape={image.shape} dtype={image.dtype}")

        log("initializing OCR loaders")
        ocrLoaderMgr.initLoaders()
        if args.loader not in ocrLoaderMgr.loaderDict:
            names = ", ".join(ocrLoaderMgr.loaderDict.keys())
            raise RuntimeError(f"OCR loader not found: {args.loader}; available: {names}")

        loader = ocrLoaderMgr.loaderDict[args.loader]
        log(f"running OCR loader display={loader.displayName} mode={loader.mode}")
        result = loader.ocr(image)
        result_type = type(result).__name__
        result_len = len(result) if hasattr(result, "__len__") else "unknown"
        log(f"OCR loader returned type={result_type} len={result_len}")

        with open(args.output, "wb") as f:
            pickle.dump(result, f)
        log(f"output written elapsed={time.time() - start_time:.3f}s")
        return 0
    except Exception:
        log("failed with Python exception")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
