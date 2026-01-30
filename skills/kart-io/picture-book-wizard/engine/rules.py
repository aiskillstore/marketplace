"""
Picture Book Wizard 规则引擎
将声明式规则转换为可执行代码
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

from .config import (
    STYLES, SCENES, CHARACTERS, AGE_SYSTEM,
    WATERMARK_PREVENTION, SOUL_ELEMENTS,
    SUPPORTING_CHARACTERS, ANIMAL_COMPANIONS,
    STORY_STRUCTURES, CCLP_CONFIG
)


# ============================================================
# 数据类定义
# ============================================================

@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StoryParams:
    """故事参数"""
    style: str
    scene: str
    age: int
    pages: Optional[int] = None
    character: Optional[str] = None
    emotion: Optional[str] = None
    theme: Optional[str] = None
    with_characters: List[str] = field(default_factory=list)


@dataclass
class CharacterAnchor:
    """角色锚点"""
    name: str
    name_cn: str
    full_anchor: str
    signature_markers: Dict[str, str]
    build: str
    cclp_version: str = "4.0"


@dataclass
class PageContent:
    """单页内容"""
    page_num: int
    story_cn: str
    story_en: str
    pinyin: str
    learning_char: str
    learning_pinyin: str
    learning_meaning: str
    learning_extra: Optional[str] = None
    prompt: str = ""


@dataclass
class PictureBook:
    """完整绘本"""
    title_cn: str
    title_en: str
    style: str
    scene: str
    age: int
    character: str
    pages: List[PageContent]
    created_at: str = ""


# ============================================================
# 验证器
# ============================================================

class Validator:
    """参数验证器"""

    @staticmethod
    def validate_style(style: str) -> ValidationResult:
        """验证风格"""
        if style in STYLES:
            return ValidationResult(valid=True)

        # 模糊匹配建议
        suggestions = [s for s in STYLES.keys() if style.lower() in s.lower()]
        return ValidationResult(
            valid=False,
            errors=[f"未知风格 '{style}'"],
            warnings=[f"您是否想要: {', '.join(suggestions)}"] if suggestions else []
        )

    @staticmethod
    def validate_scene(scene: str) -> ValidationResult:
        """验证场景"""
        if scene in SCENES:
            return ValidationResult(valid=True)

        suggestions = [s for s in SCENES.keys() if scene.lower() in s.lower()]
        return ValidationResult(
            valid=False,
            errors=[f"未知场景 '{scene}'"],
            warnings=[f"您是否想要: {', '.join(suggestions)}"] if suggestions else []
        )

    @staticmethod
    def validate_age(age: int) -> ValidationResult:
        """验证年龄"""
        if 3 <= age <= 12:
            return ValidationResult(valid=True)
        return ValidationResult(
            valid=False,
            errors=[f"年龄 {age} 超出范围 (3-12岁)"]
        )

    @staticmethod
    def validate_character(character: str) -> ValidationResult:
        """验证角色"""
        if character in CHARACTERS:
            return ValidationResult(valid=True)
        return ValidationResult(
            valid=False,
            errors=[f"未知角色 '{character}'"],
            warnings=[f"可用角色: {', '.join(CHARACTERS.keys())}"]
        )

    @staticmethod
    def validate_content_safety(params: StoryParams) -> ValidationResult:
        """内容安全验证"""
        errors = []

        # 禁止内容关键词
        forbidden = ["暴力", "恐怖", "成人", "政治", "violence", "horror", "adult"]

        theme = params.theme or ""
        if any(word in theme.lower() for word in forbidden):
            errors.append(f"主题包含禁止内容: {params.theme}")

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    @classmethod
    def validate_all(cls, params: StoryParams) -> ValidationResult:
        """完整验证"""
        all_errors = []
        all_warnings = []

        checks = [
            cls.validate_style(params.style),
            cls.validate_scene(params.scene),
            cls.validate_age(params.age),
            cls.validate_content_safety(params),
        ]

        if params.character:
            checks.append(cls.validate_character(params.character))

        for result in checks:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)

        return ValidationResult(
            valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )


# ============================================================
# 年龄系统
# ============================================================

class AgeSystem:
    """年龄驱动系统"""

    @staticmethod
    def get_age_config(age: int) -> Dict:
        """获取年龄配置"""
        for (min_age, max_age), config in AGE_SYSTEM.items():
            if min_age <= age <= max_age:
                return config
        # 默认返回最高年龄段
        return AGE_SYSTEM[(9, 10)]

    @classmethod
    def calculate_pages(cls, age: int, override: Optional[int] = None) -> int:
        """计算页数"""
        if override:
            return override
        config = cls.get_age_config(age)
        return config["default_pages"]

    @classmethod
    def get_default_character(cls, age: int) -> str:
        """获取默认角色"""
        config = cls.get_age_config(age)
        return config["default_character"]

    @classmethod
    def get_sentence_limits(cls, age: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """获取句子长度限制 (中文, 英文)"""
        config = cls.get_age_config(age)
        return config["sentence_cn"], config["sentence_en"]

    @classmethod
    def get_learning_domains(cls, age: int) -> List[str]:
        """获取学习领域"""
        config = cls.get_age_config(age)
        return config["learning"]


# ============================================================
# 角色锚点生成器
# ============================================================

class CharacterAnchorGenerator:
    """CCLP 4.0 角色锚点生成器"""

    @staticmethod
    def generate(character_id: str, is_first_page: bool = False) -> CharacterAnchor:
        """生成完整角色锚点"""
        char = CHARACTERS.get(character_id)
        if not char:
            raise ValueError(f"未知角色: {character_id}")

        sig = char["signature"]

        # 构建完整锚点
        parts = [
            char["anchor"],
            f"**MANDATORY SIGNATURE: {sig['hair']}**",
            f"**MANDATORY SIGNATURE: {sig['top']}**",
        ]

        if sig.get("bottom"):
            parts.append(f"**MANDATORY SIGNATURE: {sig['bottom']}**")

        parts.append(f"**MANDATORY SIGNATURE: {sig['shoes']}**")
        parts.append(char["build"])

        full_anchor = ", ".join(parts)

        # 添加 CCLP 标记
        if is_first_page:
            full_anchor += "\n[LOCK ESTABLISHED - Page 1]\n[CCLP 4.0 STRICT MODE ACTIVE]"
        else:
            full_anchor += "\n[CONSISTENCY REFERENCE - Matches Page 1 Lock]\n[CCLP 4.0 STRICT MODE]"

        return CharacterAnchor(
            name=character_id,
            name_cn=char["name_cn"],
            full_anchor=full_anchor,
            signature_markers=sig,
            build=char["build"]
        )


# ============================================================
# 提示词组装器
# ============================================================

class PromptAssembler:
    """提示词组装器"""

    @staticmethod
    def assemble(
        style: str,
        scene: str,
        character_anchor: CharacterAnchor,
        action: str,
        expression: str,
        is_first_page: bool = False
    ) -> str:
        """组装完整提示词"""

        style_config = STYLES.get(style, {})
        scene_config = SCENES.get(scene, {})

        parts = [
            # 风格
            style_config.get("keywords", "children's book illustration"),
            # 角色锚点
            character_anchor.full_anchor.split("\n")[0],  # 不含 CCLP 标记
            # 表情和动作
            f"{expression}, {action}",
            # 场景元素
            scene_config.get("elements", ""),
            # 水印防护
            WATERMARK_PREVENTION["level2"],
        ]

        prompt = ", ".join(filter(None, parts))

        # 添加 CCLP 标记
        if is_first_page:
            prompt += "\n\n[LOCK ESTABLISHED - Page 1]\n[CCLP 4.0 STRICT MODE ACTIVE]"
        else:
            prompt += "\n\n[CONSISTENCY REFERENCE - Matches Page 1 Lock]\n[CCLP 4.0 STRICT MODE]"

        return prompt

    @staticmethod
    def get_word_count(prompt: str) -> int:
        """计算提示词词数"""
        # 移除 CCLP 标记后计算
        clean = re.sub(r'\[.*?\]', '', prompt)
        return len(clean.split())


# ============================================================
# 输出格式化器
# ============================================================

class OutputFormatter:
    """输出格式化器"""

    @staticmethod
    def format_page(page: PageContent) -> str:
        """格式化单页输出"""
        output = f"""## 第{page.page_num}页 / Page {page.page_num}

📖 **故事 / Story:**
{page.story_cn}
{page.story_en}

---

🔤 **拼音 / Pinyin:**
{page.pinyin}

---

✨ **学习要点 / Learning Point:**
{page.learning_char} ({page.learning_pinyin}) - {page.learning_meaning}"""

        if page.learning_extra:
            output += f"\n{page.learning_extra}"

        output += f"""

---

🎨 **Banana Nano Prompt:**
```
{page.prompt}
```

---
"""
        return output

    @staticmethod
    def format_book(book: PictureBook) -> str:
        """格式化完整绘本"""
        char = CHARACTERS.get(book.character, {})

        output = f"""# 🌸 {book.title_cn} / {book.title_en}

**Pages**: {len(book.pages)} | **Age**: {book.age} | **Style**: {book.style.title()} | **Character**: {char.get('name_cn', book.character)}

---

"""
        for page in book.pages:
            output += OutputFormatter.format_page(page)

        output += f"""
## 📚 故事总结 / Story Summary

**Created**: {book.created_at}
**Style**: {STYLES.get(book.style, {}).get('name_cn', book.style)}
**Scene**: {SCENES.get(book.scene, {}).get('name_cn', book.scene)}
"""
        return output

    @staticmethod
    def get_output_path(book: PictureBook) -> str:
        """生成输出文件路径"""
        now = datetime.now()
        filename = f"{book.style}-{book.scene}-{book.character}-{len(book.pages)}pages-{now.strftime('%Y%m%d')}.md"
        return f"./output/picture-books/{now.strftime('%Y-%m')}/{filename}"


# ============================================================
# 主引擎
# ============================================================

class PictureBookEngine:
    """绘本生成引擎"""

    def __init__(self):
        self.validator = Validator()
        self.age_system = AgeSystem()
        self.anchor_gen = CharacterAnchorGenerator()
        self.prompt_asm = PromptAssembler()
        self.formatter = OutputFormatter()

    def parse_args(self, args: str) -> StoryParams:
        """解析参数"""
        parts = args.split()

        params = StoryParams(
            style=parts[0] if len(parts) > 0 else "storybook",
            scene=parts[1] if len(parts) > 1 else "meadow",
            age=int(parts[2]) if len(parts) > 2 else 5,
        )

        # 解析可选参数
        for i, part in enumerate(parts[3:], start=3):
            if part.isdigit():
                params.pages = int(part)
            elif part.startswith("with:"):
                params.with_characters = part[5:].split(",")
            elif part.startswith("emotion:"):
                params.emotion = part[8:]
            elif part.startswith("theme:"):
                params.theme = part[6:]
            elif part in CHARACTERS:
                params.character = part

        # 自动填充
        if not params.pages:
            params.pages = self.age_system.calculate_pages(params.age)
        if not params.character:
            params.character = self.age_system.get_default_character(params.age)

        return params

    def validate(self, params: StoryParams) -> ValidationResult:
        """验证参数"""
        return self.validator.validate_all(params)

    def generate_anchor(self, character: str, page: int) -> CharacterAnchor:
        """生成角色锚点"""
        return self.anchor_gen.generate(character, is_first_page=(page == 1))

    def assemble_prompt(
        self,
        params: StoryParams,
        action: str,
        expression: str,
        page: int
    ) -> str:
        """组装提示词"""
        anchor = self.generate_anchor(params.character, page)
        return self.prompt_asm.assemble(
            style=params.style,
            scene=params.scene,
            character_anchor=anchor,
            action=action,
            expression=expression,
            is_first_page=(page == 1)
        )

    def get_scene_characters(self, scene: str) -> List[str]:
        """获取场景推荐汉字"""
        return SCENES.get(scene, {}).get("characters_cn", [])

    def get_style_keywords(self, style: str) -> str:
        """获取风格关键词"""
        return STYLES.get(style, {}).get("keywords", "")

    def format_output(self, book: PictureBook) -> str:
        """格式化输出"""
        return self.formatter.format_book(book)


# ============================================================
# 便捷函数
# ============================================================

def create_engine() -> PictureBookEngine:
    """创建引擎实例"""
    return PictureBookEngine()


def quick_validate(style: str, scene: str, age: int) -> bool:
    """快速验证"""
    params = StoryParams(style=style, scene=scene, age=age)
    result = Validator.validate_all(params)
    return result.valid
