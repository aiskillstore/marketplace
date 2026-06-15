#!/usr/bin/env python3
"""Quark OCR - 夸克扫描王 OCR 识别服务"""
from common import run_ocr, save_translated_image_from_result

if __name__ == "__main__":
    # pic-translate 场景需要落盘译图；handler 内部按 scene 守卫，其他 OCR 场景零影响
    run_ocr(result_handler_with_config=save_translated_image_from_result)
