#!/usr/bin/env python3
"""夸克扫描王图片增强服务"""
from common import run_ocr, save_image_from_result

if __name__ == "__main__":
    run_ocr(result_handler=save_image_from_result)
