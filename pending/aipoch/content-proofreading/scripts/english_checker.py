#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""English check module
Provides English spelling, grammar, punctuation and style checking functions"""

import re
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set


class IssueSeverity(Enum):
    """problem severity"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(Enum):
    """Question Category"""

    SPELLING = "spelling"
    GRAMMAR = "grammar"
    PUNCTUATION = "punctuation"
    STYLE = "style"
    CAPITALIZATION = "capitalization"


@dataclass
class EnglishIssue:
    """English check problem record"""

    type: str
    category: IssueCategory
    message: str
    suggestion: Optional[str] = None
    start: int = 0
    end: int = 0
    line: int = 1
    severity: IssueSeverity = IssueSeverity.WARNING


class EnglishChecker:
    """English checker"""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.issues: List[EnglishIssue] = []

        self.us_to_uk: Dict[str, str] = {
            "color": "colour",
            "center": "centre",
            "meter": "metre",
            "liter": "litre",
            "program": "programme",
            "analyze": "analyse",
            "catalog": "catalogue",
            "dialog": "dialogue",
            "analog": "analogue",
            "esthetic": "aesthetic",
            "defense": "defence",
            "license": "licence",
            "practise": "practice",
            "realise": "realize",
            "paralyse": "paralyze",
            "catalyse": "catalyze",
            "fertilise": "fertilize",
            "industrialise": "industrialize",
            "socialise": "socialize",
            "standardise": "standardize",
            "characterise": "characterize",
            "emphasise": "emphasize",
            "optimise": "optimize",
            "organisation": "organization",
            "labour": "labor",
            "honour": "honor",
            "favour": "favor",
            "behaviour": "behavior",
            "neighbour": "neighbor",
            "colour": "color",
        }

        self.uk_to_us: {k: v for k, v in self.us_to_uk.items()}

        self.common_misspellings: Dict[str, str] = {
            "accomodate": "accommodate",
            "accomodation": "accommodation",
            "occurence": "occurrence",
            "recieve": "receive",
            "seperate": "separate",
            "definately": "definitely",
            "occassion": "occasion",
            "occassionally": "occasionally",
            "recomend": "recommend",
            "recomendation": "recommendation",
            "untill": "until",
            "writting": "writing",
            "noticable": "noticeable",
            "inteligence": "intelligence",
            "beleive": "believe",
            "enviroment": "environment",
            "existance": "existence",
            "foriegn": "foreign",
            "goverment": "government",
            "happend": "happened",
            "immediatly": "immediately",
            "independant": "independent",
            "knowlege": "knowledge",
            "neccessary": "necessary",
            "occured": "occurred",
            "perscholas": "per se",
            "posession": "possession",
            "privelege": "privilege",
            "publically": "publicly",
            "refered": "referred",
            "relavant": "relevant",
            "succesful": "successful",
            "tommorow": "tomorrow",
            "tounge": "tongue",
            "truely": "truly",
            "unfortunatly": "unfortunately",
        }

        self.passive_voice_patterns: List[re.Pattern] = [
            re.compile(r"\b(was|were|is|are|been|being)\s+\w+ed\b", re.IGNORECASE),
        ]

        self.redundant_expressions: Dict[str, str] = {
            "advance planning": "planning",
            "end result": "result",
            "each and every": "each or every",
            "at this point in time": "now",
            "in the event that": "if",
            "due to the fact that": "because",
            "has the ability to": "can",
            "in order to": "to",
            "a large number of": "many",
            "at all times": "always",
            "in the near future": "soon",
            "refer back": "refer",
            "repeat again": "repeat",
            "return back": "return",
            "still remains": "remains",
            "completely eliminate": "eliminate",
            "exactly identical": "identical",
            "past history": "history",
            "unexpected surprise": "surprise",
            "basic fundamentals": "fundamentals",
            "absolutely essential": "essential",
            "unexpected outcome": "outcome",
        }

        self.article_patterns: List[re.Pattern] = [
            re.compile(r"\ba\s+[aeiou]", re.IGNORECASE),
            re.compile(r"\ban\s+[bcdfgjklmnpqrstvwxyz]", re.IGNORECASE),
        ]

        self.plural_patterns: List[re.Pattern] = [
            re.compile(r"\bdata\s+(is|was)\b", re.IGNORECASE),
            re.compile(r"\bmedia\s+(is|was)\b", re.IGNORECASE),
            re.compile(r"\bphenomena\s+(is|was)\b", re.IGNORECASE),
            re.compile(r"\bcriteria\s+(is|was)\b", re.IGNORECASE),
            re.compile(r"\banalysis\s+(is|was)\b", re.IGNORECASE),
        ]

    def check(self, text: str) -> List[EnglishIssue]:
        """Perform English check"""
        self.issues = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            self._check_spelling(line, line_num, text)
            self._check_grammar(line, line_num, text)
            self._check_punctuation(line, line_num, text)
            self._check_style(line, line_num, text)
            self._check_capitalization(line, line_num, text)

        return self.issues

    def _check_spelling(self, line: str, line_num: int, full_text: str):
        """Check for spelling errors"""
        for misspelled, correct in self.common_misspellings.items():
            pattern = re.compile(r"\b" + re.escape(misspelled) + r"\b", re.IGNORECASE)
            for match in pattern.finditer(line):
                self.issues.append(
                    EnglishIssue(
                        type="spelling",
                        category=IssueCategory.SPELLING,
                        message=f"misspelling: '{match.group()}'",
                        suggestion=f"should be '{correct}'",
                        start=match.start(),
                        end=match.end(),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                    )
                )

        if self.strict:
            for i, word in enumerate(line.split()):
                clean_word = word.lower().strip(".,!?;:")
                if clean_word in self.us_to_uk:
                    self.issues.append(
                        EnglishIssue(
                            type="spelling",
                            category=IssueCategory.SPELLING,
                            message=f"American spelling: '{word}'",
                            suggestion=f"The British spelling would be: '{self.us_to_uk[clean_word]}'",
                            start=self._get_position(line, i),
                            end=self._get_position(line, i) + len(word),
                            line=line_num,
                            severity=IssueSeverity.INFO,
                        )
                    )

    def _check_grammar(self, line: str, line_num: int, full_text: str):
        """Check for syntax errors"""
        for pattern in self.plural_patterns:
            for match in pattern.finditer(line):
                self.issues.append(
                    EnglishIssue(
                        type="grammar",
                        category=IssueCategory.GRAMMAR,
                        message="Inconsistency between subject and verb: plural nouns should use plural verbs",
                        suggestion="Use plural forms (data are, media are, etc.)",
                        start=match.start(),
                        end=match.end(),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                    )
                )

        for pattern in self.article_patterns:
            for match in pattern.finditer(line):
                word_after = match.group().split()[1] if match.group().split() else ""
                if word_after and word_after[0].lower() in "aeiou":
                    expected = "an"
                else:
                    expected = "a"
                self.issues.append(
                    EnglishIssue(
                        type="grammar",
                        category=IssueCategory.GRAMMAR,
                        message=f"Wrong use of articles: '{match.group().split()[0]}'",
                        suggestion=f"should be '{expected}'",
                        start=match.start(),
                        end=match.end(),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                    )
                )

        subject_verb_patterns = [
            (r"\b(one of the)\s+\w+s?\s+(is|are)\b", "one of the + plural noun + are"),
            (
                r"\b(either|neither)\s+\w+s?\s+(is|are|was|were)\b",
                "either/neither + singular noun + is",
            ),
        ]

        for pattern, context in subject_verb_patterns:
            compiled = re.compile(pattern, re.IGNORECASE)
            for match in compiled.finditer(line):
                self.issues.append(
                    EnglishIssue(
                        type="grammar",
                        category=IssueCategory.GRAMMAR,
                        message="Subject-verb agreement error",
                        suggestion=context,
                        start=match.start(),
                        end=match.end(),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                    )
                )

    def _check_punctuation(self, line: str, line_num: int, full_text: str):
        """Check punctuation"""
        double_space = re.compile(r"\.  +[A-Z]")
        for match in double_space.finditer(line):
            self.issues.append(
                EnglishIssue(
                    type="punctuation",
                    category=IssueCategory.PUNCTUATION,
                    message="There are extra spaces after the period",
                    suggestion="Remove extra spaces",
                    start=match.start(),
                    end=match.end(),
                    line=line_num,
                    severity=IssueSeverity.WARNING,
                )
            )

        missing_space = re.compile(r"\.[a-zA-Z]")
        for match in missing_space.finditer(line):
            self.issues.append(
                EnglishIssue(
                    type="punctuation",
                    category=IssueCategory.PUNCTUATION,
                    message="Missing space after period",
                    suggestion="Add space after period",
                    start=match.start(),
                    end=match.end(),
                    line=line_num,
                    severity=IssueSeverity.WARNING,
                )
            )

        comma_splice = re.compile(r"[A-Z][a-z]+,  +[a-z]+,  +and", re.IGNORECASE)
        for match in comma_splice.finditer(line):
            self.issues.append(
                EnglishIssue(
                    type="punctuation",
                    category=IssueCategory.PUNCTUATION,
                    message="comma splice error (comma splice)",
                    suggestion="Use semicolons or connectives",
                    start=match.start(),
                    end=match.end(),
                    line=line_num,
                    severity=IssueSeverity.ERROR,
                )
            )

    def _check_style(self, line: str, line_num: int, full_text: str):
        """Check language style"""
        for pattern in self.passive_voice_patterns:
            for match in pattern.finditer(line):
                if self.strict:
                    self.issues.append(
                        EnglishIssue(
                            type="style",
                            category=IssueCategory.STYLE,
                            message="Use passive voice",
                            suggestion="Consider changing to active voice to enhance readability",
                            start=match.start(),
                            end=match.end(),
                            line=line_num,
                            severity=IssueSeverity.INFO,
                        )
                    )

        for redundant, preferred in self.redundant_expressions.items():
            pattern = re.compile(r"\b" + re.escape(redundant) + r"\b", re.IGNORECASE)
            for match in pattern.finditer(line):
                self.issues.append(
                    EnglishIssue(
                        type="style",
                        category=IssueCategory.STYLE,
                        message=f"redundant expression: '{match.group()}'",
                        suggestion=f"simplified to: '{preferred}'",
                        start=match.start(),
                        end=match.end(),
                        line=line_num,
                        severity=IssueSeverity.WARNING,
                    )
                )

        very_pattern = re.compile(r"\bvery\s+\w+", re.IGNORECASE)
        for match in very_pattern.finditer(line):
            if self.strict:
                word = match.group().split()[1]
                stronger = self._get_stronger_word(word)
                if stronger:
                    self.issues.append(
                        EnglishIssue(
                            type="style",
                            category=IssueCategory.STYLE,
                            message=f"use 'very + {word}'",
                            suggestion=f"Consider using stronger words: '{stronger}'",
                            start=match.start(),
                            end=match.end(),
                            line=line_num,
                            severity=IssueSeverity.INFO,
                        )
                    )

        that_that_pattern = re.compile(r"\bthat\s+that\b", re.IGNORECASE)
        for match in that_that_pattern.finditer(line):
            self.issues.append(
                EnglishIssue(
                    type="style",
                    category=IssueCategory.STYLE,
                    message="Repeated use of 'that'",
                    suggestion="Remove one of 'that'",
                    start=match.start(),
                    end=match.end(),
                    line=line_num,
                    severity=IssueSeverity.WARNING,
                )
            )

    def _check_capitalization(self, line: str, line_num: int, full_text: str):
        """Check case"""
        sentence_start = re.compile(r"^[a-z]")
        for match in sentence_start.finditer(line):
            if line.strip() and not line.strip().startswith("*"):
                self.issues.append(
                    EnglishIssue(
                        type="capitalization",
                        category=IssueCategory.CAPITALIZATION,
                        message="The first letter of a sentence should be capitalized",
                        suggestion=f"Will '{match.group()}' Change to '{match.group().upper()}'",
                        start=match.start(),
                        end=match.end(),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                    )
                )

        title_case_patterns = [
            (r"\b(of|in|on|at|to|for|and|but|or|the|a|an)\b", "Small words should be lowercase in uppercase titles"),
        ]

        for pattern, context in title_case_patterns:
            compiled = re.compile(pattern, re.IGNORECASE)
            if self.strict:
                for match in compiled.finditer(line):
                    if match.group(0).isupper():
                        self.issues.append(
                            EnglishIssue(
                                type="capitalization",
                                category=IssueCategory.CAPITALIZATION,
                                message="Title case wrong",
                                suggestion=context,
                                start=match.start(),
                                end=match.end(),
                                line=line_num,
                                severity=IssueSeverity.INFO,
                            )
                        )

    def _get_position(self, line: str, word_index: int) -> int:
        """Get the position of a word in a line"""
        words = line.split()
        if word_index < len(words):
            return sum(len(w) + 1 for w in words[:word_index])
        return 0

    def _get_stronger_word(self, word: str) -> Optional[str]:
        """Get more powerful synonyms"""
        stronger_words = {
            "big": "large/huge",
            "good": "excellent",
            "bad": "poor/terrible",
            "happy": "delighted",
            "sad": "devastated",
            "angry": "furious",
            "scared": "terrified",
            "tired": "exhausted",
            "hungry": "starving",
            "smart": "intelligent",
            "hard": "difficult",
            "fast": "rapid/quick",
            "slow": "sluggish",
            "rich": "wealthy",
            "poor": "impoverished",
            "beautiful": "gorgeous/stunning",
            "ugly": "hideous",
        }
        return stronger_words.get(word.lower())

    def check_spelling_only(self, text: str) -> List[EnglishIssue]:
        """Check spelling only"""
        issues = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            self._check_spelling(line, line_num, text)

        issues = self.issues.copy()
        self.issues = []
        return issues

    def check_grammar_only(self, text: str) -> List[EnglishIssue]:
        """Check syntax only"""
        issues = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            self._check_grammar(line, line_num, text)

        issues = self.issues.copy()
        self.issues = []
        return issues
