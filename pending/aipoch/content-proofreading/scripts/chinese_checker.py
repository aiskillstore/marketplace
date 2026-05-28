#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chinese check module"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class IssueSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class IssueCategory(Enum):
    TYPO = "typo"
    GRAMMAR = "grammar"
    PUNCTUATION = "punctuation"
    STYLE = "style"
    FORMAT = "format"

@dataclass
class ChineseIssue:
    type: str
    category: IssueCategory
    message: str
    suggestion: Optional[str] = None
    start: int = 0
    end: int = 0
    line: int = 1
    severity: IssueSeverity = IssueSeverity.WARNING

class ChineseChecker:
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.issues = []
        self.common_typos = {
            "Press installation": "Install", "honeydew melon": "cantaloupe", "September": "September",
            "other": "other", "self": "Own", "can't wait": "Can't wait",
            "straightforward": "straightforward", "Pulse": "pulse", "Shocked": "Shocked",
            "It must eventually happen": "after all", "Talent": "Talent", "water faucet": "Faucet",
            "business card": "postcard", "Xu Xu": "Xuxu", "sit in battle": "Take charge",
            "coverage": "cover", "Staple": "Binding", "belittle": "Needless to say",
            "Rate rate": "lead", "Alkali value": "price", "funny": "funny",
            "Vomiting song": "Acura", "Ota": "beat", "Mu Ai": "evening mist",
            "General Collection": "wanted", "compilation": "arrest", "coherent": "coherent",
            "Renshi": "connect", "destroy": "destroy", "rock": "rock",
            "dotted": "dotted", "Ranked first": "among the best",
            "badge": "badge", "Radiation": "radiation", "spasm": "Cramp",
            "twin": "twin", "spasm": "spasm", "Observe": "Observe",
        }

    def check(self, text):
        self.issues = []
        lines = text.split(chr(10))
        for line_num, line in enumerate(lines, 1):
            self._check_typos(line, line_num)
        return self.issues

    def _check_typos(self, line, line_num):
        for wrong, correct in self.common_typos.items():
            if wrong in line:
                pos = line.find(wrong)
                self.issues.append(ChineseIssue(
                    type="typo", category=IssueCategory.TYPO,
                    message=f"English: {wrong}", suggestion=f"should be {correct}",
                    start=pos, end=pos + len(wrong), line=line_num,
                    severity=IssueSeverity.ERROR))
