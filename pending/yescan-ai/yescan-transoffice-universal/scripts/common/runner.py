#!/usr/bin/env python3
"""
公共执行器模块 - 封装扫描王脚本的通用执行逻辑
"""
import sys
import argparse
from typing import Callable, Optional

from .ocr_client import OCRResult, CredentialManager, QuarkOCRClient
from .scene_configs import get_scene_config, list_scenes
from .messages import CLI_DESCRIPTION, CLI_EPILOG_AVAILABLE_SCENES, CLI_SCENE_HELP, CLI_URL_HELP, CLI_PATH_HELP, CLI_BASE64_HELP, CLI_EPILOG_EXAMPLES


# 结果处理器类型
ResultHandler = Callable[[OCRResult], OCRResult]
ResultHandlerWithConfig = Callable[[OCRResult, dict], OCRResult]


def run_ocr(result_handler: Optional[ResultHandler] = None,
            result_handler_with_config: Optional[ResultHandlerWithConfig] = None) -> None:
    """
    通用扫描王服务执行器
    
    Args:
        result_handler: 结果处理函数，签名为 (OCRResult) -> OCRResult
        result_handler_with_config: 需要配置的结果处理函数，签名为 (OCRResult, config) -> OCRResult
    
    使用示例:
        # 仅调用（不保存文件）
        run_ocr()
        
        # 图片增强类（保存图片）
        run_ocr(result_handler=save_image_from_result)
        
        # 文档转换类（保存文档，需要config判断word/excel）
        run_ocr(result_handler_with_config=save_document_from_result)
    """
    parser = argparse.ArgumentParser(
        description=CLI_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{CLI_EPILOG_AVAILABLE_SCENES}
  {', '.join(list_scenes())}

{CLI_EPILOG_EXAMPLES}
  python3 scripts/scan.py --scene image-to-excel --url "https://example.com/sales.png"
  python3 scripts/scan.py --scene image-to-word --path "/path/to/notes.jpg"
        """
    )
    
    # 场景参数（必填）
    parser.add_argument("--scene", "-s", required=True, help=CLI_SCENE_HELP)
    
    # 图片输入参数（三选一）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", "-u", help=CLI_URL_HELP)
    group.add_argument("--path", "-p", help=CLI_PATH_HELP)
    group.add_argument("--base64", "-b", help=CLI_BASE64_HELP)

    # 平台标识（可选，Agent 自动填写）
    parser.add_argument("--platform", default=None,
                        help="Agent 平台标识（如 openclaw、wukong、qoderWork 等）")
    
    args = parser.parse_args()
    
    # 获取场景配置
    try:
        config = get_scene_config(args.scene)
        config["scene"] = args.scene  # 添加 scene 名称供 result_handler 使用
    except ValueError as e:
        print(OCRResult(code="INVALID_SCENE", message=str(e), data=None).to_json())
        sys.exit(1)
    
    try:
        api_key = CredentialManager.load()
        with QuarkOCRClient(
            api_key=api_key,
            scene=args.scene,
            data_type=config["data_type"],
            platform=args.platform
        ) as client:
            if args.base64:
                result = client.recognize(base64_data=args.base64)
            elif args.url:
                result = client.recognize(image_url=args.url)
            else:
                result = client.recognize(image_path=args.path)
        
        # 应用结果处理器
        if result_handler_with_config:
            result = result_handler_with_config(result, config)
        elif result_handler:
            result = result_handler(result)
        
        print(result.to_json())
        
    except ValueError as e:
        print(OCRResult(code="A0100", message=str(e), data=None).to_json())
        sys.exit(1)
    except Exception as e:
        print(OCRResult(code="UNKNOWN_ERROR", message=f"Unexpected error: {str(e)}", data=None).to_json())
        sys.exit(1)
