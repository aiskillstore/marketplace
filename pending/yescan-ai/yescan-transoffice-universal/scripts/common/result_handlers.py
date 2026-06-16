#!/usr/bin/env python3
"""
结果处理器模块 - 处理扫描王服务结果并保存文件
"""
from typing import Any, Dict

from .constants import SUCCESS_CODE
from .ocr_client import OCRResult
from .file_saver import FileSaver


def save_image_from_result(result: OCRResult) -> OCRResult:
    """从扫描王服务结果中提取并保存图片"""
    if result.code != SUCCESS_CODE:
        return result

    image_base64 = None
    if isinstance(result.data, dict) and "ImageInfo" in result.data:
        image_info_list = result.data["ImageInfo"]
        if isinstance(image_info_list, list) and len(image_info_list) > 0:
            image_info = image_info_list[0]
            if isinstance(image_info, dict) and "ImageBase64" in image_info:
                image_base64 = image_info["ImageBase64"]

    if image_base64:
        try:
            saver = FileSaver()
            save_res = saver.save_image_from_base64(image_base64)
            if save_res["code"] == 0:
                result.data = {"path": save_res["data"]["path"]}
            else:
                result = OCRResult(code=save_res["code"], message=save_res["msg"], data=save_res["data"])
        except (IOError, OSError) as e:
            result = OCRResult(code="FILE_SAVE_ERROR", message=f"File save failed: {e}", data={})

    return result


def save_translated_image_from_result(result: OCRResult, config: dict) -> OCRResult:
    """pic-translate 场景：保存译图、注入 translated_image_path、剔除 ImageInfo

    - 仅当 scene == "pic-translate" 触发；其他场景原样返回
    - 字段路径：data.ImageInfo[0].ResImageBase64
    - 落盘成功 → data["translated_image_path"] = <path>
    - 安静降级（B1）：失败/字段缺失仅 pop ImageInfo，不改 code/message
    - 始终保留 data 中除 ImageInfo 外的其他字段（译文文本、坐标等）
    """
    if config.get("scene") != "pic-translate":
        return result
    if result.code != SUCCESS_CODE or not isinstance(result.data, dict):
        return result

    data: Dict[str, Any] = result.data
    image_info = data.get("ImageInfo")

    # 接口返回的 ImageInfo 是 list，取首元素；同时容错接受 dict
    if isinstance(image_info, list) and image_info:
        image_info = image_info[0] if isinstance(image_info[0], dict) else None

    if not isinstance(image_info, dict):
        data.pop("ImageInfo", None)
        return result

    res_image_base64 = image_info.get("ResImageBase64")
    if isinstance(res_image_base64, str) and res_image_base64.strip():
        try:
            save_res = FileSaver().save_image_from_base64(res_image_base64)
            if save_res.get("code") == 0:
                data["translated_image_path"] = save_res.get("data", {}).get("path")
        except (IOError, OSError):
            # B1 安静降级：落盘异常不抛出，仅不注入 path
            pass

    data.pop("ImageInfo", None)
    return result


def save_document_from_result(result: OCRResult, config: dict) -> OCRResult:
    """从扫描王服务结果中提取并保存文档（Word/Excel/PDF）"""
    if result.code != SUCCESS_CODE:
        return result

    # 根据 scene 名称判断保存类型
    scene = config.get("scene", "")
    if scene == "image-to-word":
        doc_type = "word"
    elif scene == "image-to-excel":
        doc_type = "excel"
    elif scene == "image-to-pdf":
        doc_type = "pdf"
    else:
        doc_type = None

    if not doc_type:
        return result

    file_base64 = None
    if isinstance(result.data, dict) and "TypesetInfo" in result.data:
        typeset_info_list = result.data["TypesetInfo"]
        if isinstance(typeset_info_list, list) and len(typeset_info_list) > 0:
            typeset_info = typeset_info_list[0]
            if isinstance(typeset_info, dict) and "FileBase64" in typeset_info:
                file_base64 = typeset_info["FileBase64"]

    if file_base64:
        try:
            saver = FileSaver()
            if doc_type == "word":
                save_res = saver.save_word_from_base64(file_base64)
            elif doc_type == "pdf":
                save_res = saver.save_pdf_from_base64(file_base64)
            else:  # excel
                save_res = saver.save_excel_from_base64(file_base64)

            if save_res["code"] == 0:
                result.data = {"path": save_res["data"]["path"]}
            else:
                result = OCRResult(code=save_res["code"], message=save_res["msg"], data=save_res["data"])
        except (IOError, OSError) as e:
            result = OCRResult(code="FILE_SAVE_ERROR", message=f"File save failed: {e}", data={})

    return result
