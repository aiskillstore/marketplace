#!/usr/bin/env python3
"""夸克扫描王 - 文档转换服务"""
from common import run_ocr, save_document_from_result

if __name__ == "__main__":
    run_ocr(result_handler_with_config=save_document_from_result)
