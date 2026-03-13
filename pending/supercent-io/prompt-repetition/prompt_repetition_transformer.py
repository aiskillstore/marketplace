#!/usr/bin/env python3
"""
Prompt Repetition Transformer

경량 모델(haiku, flash, mini)에서 자동으로 프롬프트 반복을 적용하여
LLM 정확도를 향상시키는 변환기입니다.

Google Research 2025 연구 기반:
- 70개 벤치마크 중 67%(47/70)에서 유의미한 성능 향상
- 최대 +76%p 개선 (Gemini 2.0 Flash-Lite on NameIndex)
- 지연 시간 증가 +2% (Prefill 병렬화)

Usage:
    from prompt_repetition_transformer import PromptRepetitionTransformer

    transformer = PromptRepetitionTransformer()
    improved_prompt = transformer.transform(prompt, model="claude-haiku")
"""

from dataclasses import dataclass
from typing import Optional, Callable, List, Dict
import re


# 모델별 컨텍스트 윈도우 (토큰 수)
MODEL_CONTEXT_WINDOWS: Dict[str, int] = {
    "claude-3-haiku": 200_000,
    "claude-haiku": 200_000,
    "gemini-flash": 1_000_000,
    "gemini-flash-lite": 1_000_000,
    "gemini-2.0-flash": 1_000_000,
    "gpt-4o-mini": 128_000,
    "gpt-low": 128_000,
}

# 자동 적용 대상 모델
AUTO_APPLY_MODELS: List[str] = list(MODEL_CONTEXT_WINDOWS.keys())

# CoT 패턴 (적용 제외)
COT_PATTERNS: List[str] = [
    r"step by step",
    r"think through",
    r"let's think",
    r"reasoning:",
    r"chain of thought",
    r"단계별로",
    r"차근차근",
]

# Position/Index 패턴 (3회 반복)
POSITION_PATTERNS: List[str] = [
    r"slot \d+",
    r"position \d+",
    r"index \d+",
    r"\d+번째",
    r"item \d+",
    r"row \d+",
    r"column \d+",
    r"슬롯 \d+",
    r"위치 \d+",
]


@dataclass
class PromptRepetitionConfig:
    """프롬프트 반복 설정"""
    default_repetitions: int = 2
    position_repetitions: int = 3
    separator: str = "\n\n"
    max_context_ratio: float = 0.8
    applied_marker: str = "<!-- prompt-repetition-applied -->"


class PromptRepetitionTransformer:
    """경량 모델용 프롬프트 반복 자동 적용 변환기

    Example:
        >>> transformer = PromptRepetitionTransformer()
        >>> prompt = "A. Paris\\nB. London\\n\\nWhat is the capital of France?"
        >>> result = transformer.transform(prompt, "claude-haiku")
        >>> # 프롬프트가 2회 반복됨
    """

    def __init__(self, config: Optional[PromptRepetitionConfig] = None):
        self.config = config or PromptRepetitionConfig()

    def should_apply(self, model: str, prompt: str) -> bool:
        """자동 적용 여부 결정

        Args:
            model: 모델 이름 (예: claude-haiku, gemini-flash)
            prompt: 원본 프롬프트

        Returns:
            적용 여부 (True/False)
        """
        # 이미 적용된 경우 스킵
        if self.config.applied_marker in prompt:
            return False

        # 대상 모델 확인
        model_lower = model.lower()
        if not any(m in model_lower for m in AUTO_APPLY_MODELS):
            return False

        # CoT 패턴 감지 시 스킵
        prompt_lower = prompt.lower()
        for pattern in COT_PATTERNS:
            if re.search(pattern, prompt_lower):
                return False

        return True

    def determine_repetitions(self, prompt: str, model: str) -> int:
        """작업 유형에 따른 반복 횟수 결정

        Args:
            prompt: 프롬프트 내용
            model: 모델 이름

        Returns:
            반복 횟수 (2 또는 3)
        """
        prompt_lower = prompt.lower()

        # Position/Index 패턴 감지 → 3회
        for pattern in POSITION_PATTERNS:
            if re.search(pattern, prompt_lower):
                return self.config.position_repetitions

        return self.config.default_repetitions

    def estimate_tokens(self, text: str) -> int:
        """간단한 토큰 수 추정 (정확도보다 속도 우선)

        Args:
            text: 텍스트

        Returns:
            추정 토큰 수
        """
        # 영어: 평균 4자 = 1토큰
        # 한국어: 평균 2자 = 1토큰 (보수적 추정)
        # 혼합 추정: 3자 = 1토큰
        return len(text) // 3

    def get_max_context(self, model: str) -> int:
        """모델별 최대 컨텍스트 윈도우 반환

        Args:
            model: 모델 이름

        Returns:
            최대 토큰 수
        """
        model_lower = model.lower()
        for m, tokens in MODEL_CONTEXT_WINDOWS.items():
            if m in model_lower:
                return tokens
        return 128_000  # 기본값

    def transform(self, prompt: str, model: str) -> str:
        """프롬프트에 반복 적용

        Args:
            prompt: 원본 프롬프트
            model: 모델 이름

        Returns:
            변환된 프롬프트 (반복 적용됨)
        """
        if not self.should_apply(model, prompt):
            return prompt

        repetitions = self.determine_repetitions(prompt, model)

        # 컨텍스트 제한 체크
        max_tokens = self.get_max_context(model)
        max_allowed = int(max_tokens * self.config.max_context_ratio)
        prompt_tokens = self.estimate_tokens(prompt)

        # 토큰 제한 초과 시 반복 횟수 조정
        while prompt_tokens * repetitions > max_allowed and repetitions > 1:
            repetitions -= 1

        if repetitions <= 1:
            return prompt

        # 반복 적용 + 마커 추가
        repeated = self.config.separator.join([prompt] * repetitions)
        return f"{self.config.applied_marker}\n{repeated}"

    def wrap_llm_call(self, llm_fn: Callable, model: str) -> Callable:
        """LLM 호출 함수 래핑

        Args:
            llm_fn: 원본 LLM 호출 함수
            model: 모델 이름

        Returns:
            래핑된 함수
        """
        def wrapped(prompt: str, **kwargs):
            transformed = self.transform(prompt, model)
            return llm_fn(transformed, **kwargs)
        return wrapped


def apply_prompt_repetition(prompt: str, times: int = 2, separator: str = "\n\n") -> str:
    """간단한 프롬프트 반복 함수

    Args:
        prompt: 원본 프롬프트
        times: 반복 횟수 (기본 2회)
        separator: 반복 간 구분자

    Returns:
        반복된 프롬프트
    """
    if times <= 1:
        return prompt
    return separator.join([prompt] * times)


# 편의 함수
def is_lightweight_model(model: str) -> bool:
    """경량 모델 여부 확인"""
    model_lower = model.lower()
    return any(m in model_lower for m in AUTO_APPLY_MODELS)


def has_cot_pattern(prompt: str) -> bool:
    """CoT 패턴 포함 여부 확인"""
    prompt_lower = prompt.lower()
    for pattern in COT_PATTERNS:
        if re.search(pattern, prompt_lower):
            return True
    return False


def has_position_pattern(prompt: str) -> bool:
    """Position/Index 패턴 포함 여부 확인"""
    prompt_lower = prompt.lower()
    for pattern in POSITION_PATTERNS:
        if re.search(pattern, prompt_lower):
            return True
    return False


if __name__ == "__main__":
    # 테스트
    transformer = PromptRepetitionTransformer()

    # 테스트 1: 기본 반복
    test_prompt = "A. Paris\nB. London\n\nWhich city is the capital of France?"
    result = transformer.transform(test_prompt, "claude-haiku")
    print("=== Test 1: Basic Repetition ===")
    print(f"Applied marker present: {transformer.config.applied_marker in result}")
    print(f"Repeated: {test_prompt in result}")
    print()

    # 테스트 2: Position 패턴 (3회)
    test_prompt_pos = "What item is in slot 25?"
    result_pos = transformer.transform(test_prompt_pos, "gemini-flash")
    repetitions = result_pos.count(test_prompt_pos)
    print("=== Test 2: Position Pattern (3x) ===")
    print(f"Repetitions: {repetitions}")
    print()

    # 테스트 3: CoT 스킵
    test_prompt_cot = "Think step by step. What is 2+2?"
    result_cot = transformer.transform(test_prompt_cot, "claude-haiku")
    print("=== Test 3: CoT Skip ===")
    print(f"Skipped (no change): {result_cot == test_prompt_cot}")
    print()

    # 테스트 4: 비대상 모델 스킵
    test_prompt_skip = "What is the capital of France?"
    result_skip = transformer.transform(test_prompt_skip, "claude-opus")
    print("=== Test 4: Non-target Model Skip ===")
    print(f"Skipped (no change): {result_skip == test_prompt_skip}")
