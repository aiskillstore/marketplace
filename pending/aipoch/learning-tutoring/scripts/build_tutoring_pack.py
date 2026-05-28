#!/usr/bin/env python3
"""Generate study guidance package: study plan + practice questions + answer analysis.

How to use:
1) Fill in the learning requirements in the CONFIG area below
2) Run: python scripts/build_tutoring_pack.py
3) View the results in outputs/tutoring_pack.json"""

from __future__ import annotations

import json
import os
from datetime import datetime

CONFIG = {
    "subject": "Python basics",
    "learner_level": "Zero foundation",
    "duration_weeks": 4,
    "time_per_week_hours": 4,
    "goals": [
        "Master core concepts such as variables, conditions, loops, and functions",
        "Able to use Python to complete simple data processing tasks",
    ],
    "topics": [
        "Variables and data types",
        "Conditional judgment",
        "Loops and iterations",
        "Functions and parameters",
        "Lists and dictionaries",
        "File reading and writing",
    ],
    "practice": {
        "choice": 4,
        "short_answer": 4,
        "application": 2,
    },
    "output_path": os.path.join("outputs", "tutoring_pack.json"),
}


CHOICE_TEMPLATES = [
    "Regarding {topic}, which of the following statements is most accurate?",
    "The main functions of {topic} are:",
    "When learning {topic}, the most critical concepts are:",
]

SHORT_TEMPLATES = [
    "Explain the core concept of {topic} in 1-2 sentences.",
    "Please briefly explain the usage scenarios of {topic}.",
    "Summarize the key points of {topic}.",
]

APPLICATION_TEMPLATES = [
    "Please give a practical application scenario of {topic} and explain the solution.",
    "Design a small task containing {topic}, explain the steps or pseudocode.",
]


def chunk_topics(topics: list[str], weeks: int) -> list[list[str]]:
    if weeks <= 0:
        return []
    size = max(1, len(topics) // weeks)
    chunks = []
    idx = 0
    for week in range(weeks):
        end = idx + size
        if week == weeks - 1:
            end = len(topics)
        chunks.append(topics[idx:end])
        idx = end
    return chunks


def build_plan(config: dict) -> list[dict]:
    weeks = config["duration_weeks"]
    topics = config["topics"]
    chunked = chunk_topics(topics, weeks)
    plan = []
    for i, focus_topics in enumerate(chunked, start=1):
        focus = "、".join(focus_topics) if focus_topics else "Comprehensive review"
        plan.append(
            {
                "week": i,
                "focus": focus,
                "study_tasks": [
                    f"Reading and Comprehension：{focus}",
                    f"Hands-on exercises：Complete with{focus}Related exercises",
                    "Organize notes: record common mistakes and key words",
                ],
                "checkpoint": "Complete this week's exercises and be able to verbally repeat core concepts",
            }
        )
    return plan


def build_choice_question(topic: str, index: int) -> dict:
    prompt = CHOICE_TEMPLATES[index % len(CHOICE_TEMPLATES)].format(topic=topic)
    options = {
        "A": f"emphasize{topic}The core definition and role of",
        "B": f"Description and{topic}irrelevant concept",
        "C": f"right{topic}make absolute misunderstandings",
        "D": f"Confuse{topic}and similar concepts",
    }
    return {
        "type": "choice",
        "question": prompt,
        "options": options,
        "answer": "A",
        "explanation": f"A direct description{topic}core definition of，Other options are off topic or misunderstood。",
        "difficulty": "Base",
        "tags": [topic],
    }


def build_short_question(topic: str, index: int) -> dict:
    prompt = SHORT_TEMPLATES[index % len(SHORT_TEMPLATES)].format(topic=topic)
    return {
        "type": "short_answer",
        "question": prompt,
        "answer": f"{topic}Emphasize its core concepts and usage scenarios，Can be explained with specific examples。",
        "explanation": "Answers should cover definitions, functions and typical usage scenarios, and avoid vague descriptions.",
        "difficulty": "Advanced",
        "tags": [topic],
    }


def build_application_question(topic: str, index: int) -> dict:
    prompt = APPLICATION_TEMPLATES[index % len(APPLICATION_TEMPLATES)].format(topic=topic)
    return {
        "type": "application",
        "question": prompt,
        "answer": f"Give an example{topic}real tasks，and broken down into steps or pseudocode。",
        "explanation": "The analysis should include the problem background, key steps, precautions, and reflect executability.",
        "difficulty": "comprehensive",
        "tags": [topic],
    }


def build_exercises(config: dict) -> list[dict]:
    topics = config["topics"]
    practice = config["practice"]
    exercises = []
    for i in range(practice["choice"]):
        topic = topics[i % len(topics)]
        exercises.append(build_choice_question(topic, i))
    for i in range(practice["short_answer"]):
        topic = topics[i % len(topics)]
        exercises.append(build_short_question(topic, i))
    for i in range(practice["application"]):
        topic = topics[i % len(topics)]
        exercises.append(build_application_question(topic, i))
    return exercises


def main() -> None:
    plan = build_plan(CONFIG)
    exercises = build_exercises(CONFIG)
    payload = {
        "profile": {
            "subject": CONFIG["subject"],
            "learner_level": CONFIG["learner_level"],
            "duration_weeks": CONFIG["duration_weeks"],
            "time_per_week_hours": CONFIG["time_per_week_hours"],
            "goals": CONFIG["goals"],
            "topics": CONFIG["topics"],
        },
        "plan": plan,
        "exercises": exercises,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    output_path = CONFIG["output_path"]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    print(f"Learning guidance package has been generated：{output_path}")


if __name__ == "__main__":
    main()
