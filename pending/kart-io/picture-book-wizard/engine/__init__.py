"""
Picture Book Wizard Engine
规则引擎模块
"""

from .config import (
    STYLES,
    SCENES,
    CHARACTERS,
    AGE_SYSTEM,
    WATERMARK_PREVENTION,
    SOUL_ELEMENTS,
    SUPPORTING_CHARACTERS,
    ANIMAL_COMPANIONS,
    STORY_STRUCTURES,
    CCLP_CONFIG,
)

from .rules import (
    # 数据类
    ValidationResult,
    StoryParams,
    CharacterAnchor,
    PageContent,
    PictureBook,
    # 类
    Validator,
    AgeSystem,
    CharacterAnchorGenerator,
    PromptAssembler,
    OutputFormatter,
    PictureBookEngine,
    # 便捷函数
    create_engine,
    quick_validate,
)

__version__ = "1.0.0"
__all__ = [
    # 配置
    "STYLES",
    "SCENES",
    "CHARACTERS",
    "AGE_SYSTEM",
    "WATERMARK_PREVENTION",
    "SOUL_ELEMENTS",
    "SUPPORTING_CHARACTERS",
    "ANIMAL_COMPANIONS",
    "STORY_STRUCTURES",
    "CCLP_CONFIG",
    # 数据类
    "ValidationResult",
    "StoryParams",
    "CharacterAnchor",
    "PageContent",
    "PictureBook",
    # 类
    "Validator",
    "AgeSystem",
    "CharacterAnchorGenerator",
    "PromptAssembler",
    "OutputFormatter",
    "PictureBookEngine",
    # 便捷函数
    "create_engine",
    "quick_validate",
]
