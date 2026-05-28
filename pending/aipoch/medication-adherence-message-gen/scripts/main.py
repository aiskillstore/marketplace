#!/usr/bin/env python3
"""Medication Adherence Message Generator
Medication reminder copywriting generator based on behavioral psychology principles

ID: 136
Author:OpenClaw"""

import argparse
import json
import random
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from enum import Enum


class Principle(str, Enum):
    """principles of behavioral psychology"""
    SOCIAL_NORMS = "social_norms"          # social norms
    LOSS_AVERSION = "loss_aversion"        # loss aversion
    IMPLEMENTATION = "implementation"      # execution intention
    REWARD = "reward"                      # Instant rewards
    COMMITMENT = "commitment"              # Commitment to consistency
    SELF_EFFICACY = "self_efficacy"        # self-efficacy
    ANCHORING = "anchoring"                # anchoring effect
    SCARCITY = "scarcity"                  # scarcity
    RANDOM = "random"                      # randomly selected


class Tone(str, Enum):
    """tone style"""
    GENTLE = "gentle"                      # mild
    FIRM = "firm"                          # firm
    ENCOURAGING = "encouraging"            # encourage
    URGENT = "urgent"                      # urgent


class Language(str, Enum):
    """language"""
    ZH = "zh"                              # Chinese
    EN = "en"                              # English


@dataclass
class MessageResult:
    """Message generation results"""
    medication: str
    patient_name: Optional[str]
    dosage: Optional[str]
    time: Optional[str]
    principle: str
    tone: str
    message: str
    psychology_insight: str
    alternative_messages: List[str]


# ============ Chinese copywriting template ============

TEMPLATES_ZH = {
    Principle.SOCIAL_NORMS: {
        Tone.GENTLE: [
            "【{medication} Reminder】{greeting}{time_prompt}Most patients like you can insist on taking their medicines on time, and you are among them. Please {action}.",
            "[Health Reminder] {greeting} research shows that 95% of patients taking {medication} can maintain good medication habits. I believe you can too! {time_prompt} please {action}.",
            "[Medication Time] {greeting}{time_prompt} Among patients with similar conditions to yours, more than 90% insist on taking medication every day. You are also a member of this outstanding group, please {action}."
        ],
        Tone.FIRM: [
            "[Important reminder] {greeting} Taking {medication} on time is the key to recovery. More than 90% of patients can do it, and you are no exception. {time_prompt} immediately {action}!",
            "【Dose Notice】{greeting}{time_prompt} Please take {medication}. The vast majority of patients can persist. This is the basic attitude of being responsible for themselves.",
        ],
        Tone.ENCOURAGING: [
            "[Come on] {greeting} You are joining thousands of patients who insist on taking {medication}. {time_prompt} please {action}, we are all supporting you!",
            "【Health Partner】{greeting} You are not fighting alone! Millions of people take medicine on time every day. {time_prompt} please {action}, keep it up!",
        ],
        Tone.URGENT: [
            "【Emergency Reminder】{greeting}{time_prompt} Please be sure to take {medication}. Interrupting your medication will take you off track with your recovery, and 95% of patients will not do this!",
        ]
    },
    Principle.LOSS_AVERSION: {
        Tone.GENTLE: [
            "[{medication} reminder] {greeting}{time_prompt} please {action}. Missing this dose may affect the treatment effect.",
            "【Health Protection】{greeting} is protecting your health every time you take medicine on time. {time_prompt} please {action}, don’t let your previous efforts go in vain.",
            "[Medication Tips] Missing the dose of {greeting} and {medication} may cause fluctuations in the condition. {time_prompt} please {action} to protect your health."
        ],
        Tone.FIRM: [
            "【Important Warning】{greeting}{time_prompt} please {action} immediately. Missing a dose of {medication} will greatly reduce the therapeutic effect and all previous efforts will be wasted!",
            "【Don't ignore it】Every time you miss a dose of {greeting}, it is an overdraft of your health. {time_prompt} please {action}, don’t let the disease have a chance to counterattack.",
        ],
        Tone.ENCOURAGING: [
            "【Wise Choice】{greeting}{time_prompt} please {action}. A small step today is a giant step towards avoiding future health risks!",
            "【Investment in Health】{greeting} Taking your medicine on time now is saving money and worry for the future. {time_prompt} please {action}, this is the most worthwhile investment!",
        ],
        Tone.URGENT: [
            "[Act now] {greeting}{time_prompt} must take {medication}! Every delay increases health risks, don’t let small oversights turn into big problems!",
        ]
    },
    Principle.IMPLEMENTATION: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting} If {time} arrives, then {action}. Develop this habit and your health will be under control.",
            "[Execution Plan] {greeting}{time_prompt} Execute your medication plan: if it is {time} now, then take {medication}.",
            "[Habit formation] Rules set by {greeting}: {time} = take {medication}. {time_prompt}Please implement this plan."
        ],
        Tone.FIRM: [
            "[Strict implementation] {greeting}{time_prompt} executes the scheduled plan: if {time}, it must be {action}. No excuses!",
            "[Rules to follow] {greeting} The rules you set for yourself: {time} take {medication}. {time_prompt} Please keep your promise.",
        ],
        Tone.ENCOURAGING: [
            '[Plan accomplished] {greeting}{time_prompt} It’s time to implement the "If {time}, take medicine" plan again! Please {action}, you are developing good habits!',
            "[Power of Habit] {greeting} When {time} comes, taking medicine is natural. {time_prompt} please {action}, let good habits become instinct!",
        ],
        Tone.URGENT: [
            "[Execute immediately] {greeting}{time_prompt} Immediately execute your medication plan! If {time}, then {action} must be performed immediately!",
        ]
    },
    Principle.REWARD: {
        Tone.GENTLE: [
            "[{medication} reminder] {greeting}{time_prompt} please {action}. After taking the medicine, you can drink a cup of tea of ​​your choice. This is a reward for being responsible for yourself.",
            "[Health Reward] {greeting} Complete today's medication, and you will be one step closer to recovery! {time_prompt} Please {action} to give yourself a affirmation.",
            "[Small luck] {greeting}{time_prompt} please {action}. Give yourself a small reward when you're done, you deserve it!"
        ],
        Tone.FIRM: [
            "【Instant Feedback】{greeting}{time_prompt} please {action}. Every pill is the fuel for your body’s recovery, so you can realize this health immediately!",
            "[The results are visible] {greeting} takes medicine on time and his body is getting better - this is a real reward. {time_prompt} please {action}!",
        ],
        Tone.ENCOURAGING: [
            "[Celebration Moment] {greeting}{time_prompt} please {action}, and then applaud yourself! Every persistence is worth celebrating!",
            "[Reward yourself] {greeting} Congratulations! It’s another day to take your medicine on time! {time_prompt} please {action}, and then do something that makes you happy!",
        ],
        Tone.URGENT: [
            "【Don’t miss it】{greeting}{time_prompt}{action} now! Don’t let today’s health rewards slip away!",
        ]
    },
    Principle.COMMITMENT: {
        Tone.GENTLE: [
            "【{medication} Reminder】{greeting} Do you remember your commitment to health? {time_prompt} please {action}, this is a promise to yourself.",
            "【Promise Fulfilled】{greeting} You promised to take good care of yourself. {time_prompt} please {action}, to fulfill this important commitment.",
            "[Appointment Reminder] {greeting} You have an agreement with your doctor, family and yourself: take your medicine on time. {time_prompt} please {action}."
        ],
        Tone.FIRM: [
            "【Keep your promise】{greeting}{time_prompt} please {action}. Promise is not empty words, it is determination proven by actions!",
            "[Responsibility] {greeting} Your promise to yourself needs to be fulfilled now. {time_prompt} please {action} and be a trustworthy person.",
        ],
        Tone.ENCOURAGING: [
            "【Commitment Star】{greeting} you are the one who keeps your word! {time_prompt} please {action} and continue to fulfill your commitment to health!",
            "[Proud Moment] {greeting} insists on his promise to make you shine! {time_prompt} please {action} and prove your determination again!",
        ],
        Tone.URGENT: [
            "【Cash now】{greeting}{time_prompt}{action} now! Fulfill your commitment to health now, don’t delay!",
        ]
    },
    Principle.SELF_EFFICACY: {
        Tone.GENTLE: [
            "【{medication} Reminder】{greeting} You have the ability to manage your health. {time_prompt} please {action}, believe in yourself.",
            "[Confidence Reminder] {greeting} You did well in the past, and you can do the same today. {time_prompt} please {action}, you can do it.",
            "【Ability Affirmation】{greeting} Controlling your health is in your hands. {time_prompt} please {action}, you have the ability to do it."
        ],
        Tone.FIRM: [
            "[Believe in yourself] {greeting} You have the ability and determination. {time_prompt} please {action}, prove it to yourself!",
            "[Showing strength] {greeting} is in full control of your medication management. {time_prompt} please {action}, show your action!",
        ],
        Tone.ENCOURAGING: [
            "[You are awesome] {greeting} Every time you take your medicine on time, it proves that you are awesome! {time_prompt} please {action} and defeat yourself again!",
            "[Championship Mentality] {greeting} you are a master of health management! {time_prompt} please {action} and make success a habit!",
        ],
        Tone.URGENT: [
            "[Act now] {greeting} You have the ability to do better! {time_prompt} Now {action}, prove your self-control with actions!",
        ]
    },
    Principle.ANCHORING: {
        Tone.GENTLE: [
            "[{medication} reminder] {greeting}{time_prompt} please {action}. The goal is to take medicine on time for 30 consecutive days, and today is the {day} day!",
            "[Quantitative goal] {greeting} daily {dosage}, this is your standard dose. {time_prompt} please {action}, keep it accurate.",
            "[Specific Action] {greeting} is accurate to {time}, take {dosage}. {time_prompt}Please implement this specific plan."
        ],
        Tone.FIRM: [
            "[Strict implementation] {greeting} standard dose: {dosage}, standard time: {time}. {time_prompt} please be precise {action}!",
            "[Target Locking] The {greeting} 30-day plan is in progress, today is the {day} day. {time_prompt} please {action}, don’t deviate from the goal!",
        ],
        Tone.ENCOURAGING: [
            "[Progress Update] {greeting} has completed {progress}% of the monthly goal! {time_prompt} please {action}, one step closer to 30 days of perfect attendance!",
            "[Specific achievements] {greeting} Today is the {day} day to take medicine on time! {time_prompt} please {action}, specific goals, specific completion!",
        ],
        Tone.URGENT: [
            "[Complete immediately] {greeting} 30-day goal, can’t stop on day {day}! {time_prompt} immediately {action}, complete today’s specific target!",
        ]
    },
    Principle.SCARCITY: {
        Tone.GENTLE: [
            "[{medication} reminder] {greeting}{time_prompt} is the best time window to take medicine, please {action}.",
            "[Timing is important] The optimal concentration of {greeting} drugs in the body needs to be maintained on time. {time_prompt} please {action}, don’t miss this opportunity.",
            "[Window period] {greeting} Now is the period when {medication} works best. {time_prompt} please {action}."
        ],
        Tone.FIRM: [
            "[Time is limited] The best window for taking {greeting} is closing! {time_prompt} please {action} immediately, the time waits for no one!",
            "[Don’t miss the opportunity] If {greeting} misses the critical time point of {time}, the effect will be compromised. {time_prompt} please {action}!",
        ],
        Tone.ENCOURAGING: [
            "【Seize the moment】{greeting}{time_prompt} is the golden time to take {medication}! Please {action}, seize this opportunity!",
            "[Precious Moments] {greeting} Every time you take medicine is a precious opportunity for recovery! {time_prompt} please {action}, cherish the moment!",
        ],
        Tone.URGENT: [
            "[Without delay] The best time to take {greeting} is passing! {time_prompt} is about to {action}, there is no chance of missing it!",
        ]
    }
}


# ============ English copywriting template ============

TEMPLATES_EN = {
    Principle.SOCIAL_NORMS: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Most patients like you take their medication on time. You're one of them. Please {action}.",
            "[Health Reminder] {greeting}Research shows 95% of patients taking {medication} maintain good adherence. You can too! {time_prompt}Please {action}.",
        ],
        Tone.FIRM: [
            "[Important] {greeting}Taking {medication} on time is key to recovery. 90%+ of patients do it, and so should you. {time_prompt}{action}!",
        ],
        Tone.ENCOURAGING: [
            "[Keep Going] {greeting}You're taking {medication} alongside thousands of others! {time_prompt}Please {action}, we're all supporting you!",
        ],
        Tone.URGENT: [
            "[Urgent] {greeting}{time_prompt}Please take {medication} now. Missing doses puts you off track—95% of patients don't skip!",
        ]
    },
    Principle.LOSS_AVERSION: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Please {action}. Missing this dose might affect your treatment progress.",
            "[Health Guard] {greeting}Every dose on time protects your health gains. {time_prompt}Please {action}, don't let previous efforts go to waste.",
        ],
        Tone.FIRM: [
            "[Warning] {greeting}{time_prompt}Take {medication} now! Missing doses significantly reduces treatment effectiveness.",
        ],
        Tone.ENCOURAGING: [
            "[Smart Choice] {greeting}{time_prompt}Please {action}. Today's small step prevents future health risks!",
        ],
        Tone.URGENT: [
            "[Act Now] {greeting}{time_prompt}Must take {medication}! Every delay increases health risks—don't let small oversights become big problems!",
        ]
    },
    Principle.IMPLEMENTATION: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}If it's {time}, then {action}. Build this habit and health is in your hands.",
            "[Execute Plan] {greeting}{time_prompt}Follow your plan: If it's {time}, then take {medication}.",
        ],
        Tone.FIRM: [
            "[Strict Schedule] {greeting}{time_prompt}Execute your plan: If {time}, then must {action}. No excuses!",
        ],
        Tone.ENCOURAGING: [
            "[Plan Success] {greeting}{time_prompt}Time to execute your 'If {time}, then take medicine' plan! {action}, you're building a great habit!",
        ],
        Tone.URGENT: [
            "[Execute Now] {greeting}{time_prompt}Execute your plan immediately! If {time}, then you must {action} now!",
        ]
    },
    Principle.REWARD: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Please {action}. Afterward, enjoy your favorite tea as a reward for taking care of yourself.",
            "[Health Reward] {greeting}Completing today's dose brings you closer to recovery! {time_prompt}Please {action}, give yourself credit.",
        ],
        Tone.FIRM: [
            "[Instant Feedback] {greeting}{time_prompt}Please {action}. Each pill is fuel for your recovery—cash in on this health now!",
        ],
        Tone.ENCOURAGING: [
            "[Celebrate] {greeting}{time_prompt}Please {action}, then give yourself applause! Every persistence deserves celebration!",
        ],
        Tone.URGENT: [
            "[Don't Miss] {greeting}{time_prompt}{action} immediately! Don't let today's health reward slip away!",
        ]
    },
    Principle.COMMITMENT: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}Remember your commitment to health? {time_prompt}Please {action}, this is a promise to yourself.",
            "[Honor Promise] {greeting}You promised to take good care of yourself. {time_prompt}Please {action}, fulfill this important commitment.",
        ],
        Tone.FIRM: [
            "[Keep Promise] {greeting}{time_prompt}Please {action}. Commitments aren't empty words—they're proven through action!",
        ],
        Tone.ENCOURAGING: [
            "[Promise Star] {greeting}You're someone who keeps their word! {time_prompt}Please {action}, continue honoring your health commitment!",
        ],
        Tone.URGENT: [
            "[Fulfill Now] {greeting}{time_prompt}{action} now! Fulfill your health commitment immediately, no delay!",
        ]
    },
    Principle.SELF_EFFICACY: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}You have the ability to manage your health well. {time_prompt}Please {action}, believe in yourself.",
            "[Confidence] {greeting}You've done well before, and you can today too. {time_prompt}Please {action}, you're completely capable.",
        ],
        Tone.FIRM: [
            "[Believe] {greeting}You have the ability and determination. {time_prompt}Please {action}, prove it to yourself!",
        ],
        Tone.ENCOURAGING: [
            "[You're Great] {greeting}Every dose on time proves how capable you are! {time_prompt}Please {action}, conquer yourself again!",
        ],
        Tone.URGENT: [
            "[Act Now] {greeting}You can do even better! {time_prompt}{action} now, prove your self-control through action!",
        ]
    },
    Principle.ANCHORING: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}Please {action}. Goal: 30 consecutive days, today is day {day}!",
            "[Quantify Goal] {greeting}{dosage} daily is your standard dose. {time_prompt}Please {action}, stay precise.",
        ],
        Tone.FIRM: [
            "[Strict] {greeting}Standard dose: {dosage}, standard time: {time}. {time_prompt}Please {action} precisely!",
        ],
        Tone.ENCOURAGING: [
            "[Progress Update] {greeting}{progress}% of monthly goal completed! {time_prompt}Please {action}, one step closer to 30-day perfect record!",
        ],
        Tone.URGENT: [
            "[Complete Now] {greeting}30-day goal, day {day} can't break! {time_prompt}{action} immediately, complete today's target!",
        ]
    },
    Principle.SCARCITY: {
        Tone.GENTLE: [
            "[{medication} Reminder] {greeting}{time_prompt}is your optimal medication window. Please {action}.",
            "[Timing Matters] {greeting}Medication works best when taken on schedule. {time_prompt}Please {action}, don't miss this window.",
        ],
        Tone.FIRM: [
            "[Limited Time] {greeting}Optimal medication window is closing! {time_prompt}Please {action} now, timing waits for no one!",
        ],
        Tone.ENCOURAGING: [
            "[Seize Moment] {greeting}{time_prompt}is the golden time for {medication}! Please {action}, seize this opportunity!",
        ],
        Tone.URGENT: [
            "[Act Fast] {greeting}Best medication time is passing! {time_prompt}{action} now, this chance won't come again!",
        ]
    }
}


# Psychology Principles Explained
PSYCHOLOGY_INSIGHTS_ZH = {
    Principle.SOCIAL_NORMS: "Use the principle of social norms to enhance patients' behavioral motivation by emphasizing high compliance rates and making patients feel that they are part of a 'normal' group",
    Principle.LOSS_AVERSION: "Using the principle of loss aversion, emphasizing what will be lost if you do not take medicine on time, people are more concerned about avoiding losses than obtaining the same benefits.",
    Principle.IMPLEMENTATION: "Utilize the principle of execution intention to help patients establish automated medication habits and reduce decision-making fatigue through 'if-then' plans",
    Principle.REWARD: "Utilize the principle of immediate reward to associate medication-taking behavior with positive feedback to enhance intrinsic motivation and the possibility of repeated behavior",
    Principle.COMMITMENT: "Use the principle of commitment consistency to strengthen patients' commitment to themselves, doctors and family members, and enhance their sense of responsibility and motivation to fulfill their obligations.",
    Principle.SELF_EFFICACY: "Utilize the principle of self-efficacy to enhance patients' confidence in their self-management abilities and their ability to successfully perform medication-taking behaviors",
    Principle.ANCHORING: "Utilize the anchoring effect to provide specific and quantified goals (such as a 30-day plan) to make abstract health management concrete and trackable.",
    Principle.SCARCITY: "Use the principle of scarcity to emphasize the limited time window for taking medication and create a moderate sense of urgency to promote immediate action"
}

PSYCHOLOGY_INSIGHTS_EN = {
    Principle.SOCIAL_NORMS: "Uses social norms to enhance motivation by emphasizing high adherence rates, making patients feel part of the 'normal' group",
    Principle.LOSS_AVERSION: "Uses loss aversion to emphasize what patients stand to lose by missing doses—people prefer avoiding losses to acquiring equivalent gains",
    Principle.IMPLEMENTATION: "Uses implementation intentions through 'if-then' plans to help patients build automatic habits and reduce decision fatigue",
    Principle.REWARD: "Uses immediate rewards to associate medication behavior with positive feedback, enhancing intrinsic motivation",
    Principle.COMMITMENT: "Uses commitment and consistency to strengthen patients' promises to themselves, doctors, and family, enhancing responsibility",
    Principle.SELF_EFFICACY: "Uses self-efficacy to boost patients' confidence in their ability to manage medication successfully",
    Principle.ANCHORING: "Uses anchoring by providing specific quantifiable goals (e.g., 30-day plan), making abstract health management concrete",
    Principle.SCARCITY: "Uses scarcity to emphasize the limited medication window, creating urgency to prompt immediate action"
}


def get_greeting(name: Optional[str], language: Language) -> str:
    """Get greeting"""
    if not name:
        return ""
    if language == Language.ZH:
        return f"{name}，"
    else:
        return f"Hi {name}, "


def get_time_prompt(time: Optional[str], language: Language) -> str:
    """Get time reminder"""
    if not time:
        return ""
    if language == Language.ZH:
        return f"now is{time}。"
    else:
        return f"It's {time}. "


def get_action_text(medication: str, dosage: Optional[str], language: Language) -> str:
    """Get action text"""
    if language == Language.ZH:
        if dosage:
            return f"take{dosage}of{medication}"
        else:
            return f"take{medication}"
    else:
        if dosage:
            return f"take {dosage} of {medication}"
        else:
            return f"take your {medication}"


def generate_message(
    medication: str,
    patient_name: Optional[str] = None,
    dosage: Optional[str] = None,
    time: Optional[str] = None,
    principle: Principle = Principle.RANDOM,
    tone: Tone = Tone.ENCOURAGING,
    language: Language = Language.ZH,
    day: int = 1,
    progress: int = 50
) -> MessageResult:
    """Generate medication reminder messages
    
    Args:
        medication: drug name
        patient_name: patient name
        dosage: dose
        time: medication time
        principle: psychological principle
        tone: tone style
        language: language
        day: day (for anchoring effect)
        progress: progress percentage (for anchoring effect)
    
    Returns:
        MessageResult: Result object containing the main message and alternative messages"""
    # Select template library
    templates = TEMPLATES_ZH if language == Language.ZH else TEMPLATES_EN
    insights = PSYCHOLOGY_INSIGHTS_ZH if language == Language.ZH else PSYCHOLOGY_INSIGHTS_EN
    
    # random selection principle
    if principle == Principle.RANDOM:
        principle = random.choice([
            Principle.SOCIAL_NORMS, Principle.LOSS_AVERSION,
            Principle.IMPLEMENTATION, Principle.REWARD,
            Principle.COMMITMENT, Principle.SELF_EFFICACY,
            Principle.ANCHORING, Principle.SCARCITY
        ])
    
    # Get a template for this philosophy and tone
    principle_templates = templates.get(principle, templates[Principle.SOCIAL_NORMS])
    tone_templates = principle_templates.get(tone, principle_templates[Tone.ENCOURAGING])
    
    # Prepare variables
    greeting = get_greeting(patient_name, language)
    time_prompt = get_time_prompt(time, language)
    action = get_action_text(medication, dosage, language)
    
    # Generate primary and alternative messages
    messages = []
    for template in tone_templates:
        try:
            msg = template.format(
                medication=medication,
                greeting=greeting,
                time_prompt=time_prompt,
                action=action,
                time=time or ("now" if language == Language.EN else "Now"),
                dosage=dosage or ("your dose" if language == Language.EN else "prescribed dose"),
                day=day,
                progress=progress
            )
            messages.append(msg)
        except KeyError:
            # Some templates may not contain all variables
            continue
    
    if not messages:
        # Guaranteed news
        if language == Language.ZH:
            messages = [f"【Medication reminder】{greeting}Please take it on time{medication}。"]
        else:
            messages = [f"[Medication Reminder] {greeting}Please take your {medication} on time."]
    
    # The main message is the first one, and the rest are alternatives
    main_message = messages[0]
    alternative_messages = messages[1:]
    
    # Add alternative messages in other tones
    all_tones = [Tone.GENTLE, Tone.FIRM, Tone.ENCOURAGING, Tone.URGENT]
    for other_tone in all_tones:
        if other_tone != tone and len(alternative_messages) < 3:
            other_templates = principle_templates.get(other_tone, [])
            if other_templates:
                try:
                    alt_msg = random.choice(other_templates).format(
                        medication=medication,
                        greeting=greeting,
                        time_prompt=time_prompt,
                        action=action,
                        time=time or ("now" if language == Language.EN else "Now"),
                        dosage=dosage or ("your dose" if language == Language.EN else "prescribed dose"),
                        day=day,
                        progress=progress
                    )
                    if alt_msg not in alternative_messages:
                        alternative_messages.append(f"[{other_tone.value}] {alt_msg}")
                except:
                    pass
    
    return MessageResult(
        medication=medication,
        patient_name=patient_name,
        dosage=dosage,
        time=time,
        principle=principle.value,
        tone=tone.value,
        message=main_message,
        psychology_insight=insights.get(principle, ""),
        alternative_messages=alternative_messages[:3]  # Up to 3 options
    )


def main():
    """Command line entry"""
    parser = argparse.ArgumentParser(
        description="Medication Adherence Message Generator - Medication reminder copywriting generator based on behavioral psychology"
    )
    
    parser.add_argument("-n", "--name", type=str, help="Patient name")
    parser.add_argument("-m", "--medication", type=str, required=True, help="Medication name")
    parser.add_argument("-d", "--dosage", type=str, help="Dosage (e.g., '20mg')")
    parser.add_argument("-t", "--time", type=str, help="Time of taking medication (Time, e.g., 'after breakfast')")
    parser.add_argument(
        "-p", "--principle",
        type=str,
        choices=[p.value for p in Principle],
        default="random",
        help="Psychological principle"
    )
    parser.add_argument(
        "--tone",
        type=str,
        choices=[t.value for t in Tone],
        default="encouraging",
        help="Tone style"
    )
    parser.add_argument("-l", "--language", type=str, choices=["zh", "en"], default="zh", help="Language")
    parser.add_argument("-o", "--output", type=str, choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--day", type=int, default=1, help="Day number for anchoring")
    parser.add_argument("--progress", type=int, default=50, help="Progress percentage")
    
    args = parser.parse_args()
    
    # Generate message
    result = generate_message(
        medication=args.medication,
        patient_name=args.name,
        dosage=args.dosage,
        time=args.time,
        principle=Principle(args.principle),
        tone=Tone(args.tone),
        language=Language(args.language),
        day=args.day,
        progress=args.progress
    )
    
    # Output results
    if args.output == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print("=" * 50)
        print("📋 Medication reminder copywriting")
        print("=" * 50)
        print(f"\n📝 main message:\n{result.message}\n")
        
        print(f"🧠 Principles of psychology: {result.principle}")
        print(f"💡 Principle description: {result.psychology_insight}\n")
        
        if result.alternative_messages:
            print("📎 Alternative copy:")
            for i, alt in enumerate(result.alternative_messages, 1):
                print(f"  {i}. {alt}")
            print()
        
        print("=" * 50)
        print(f"drug: {result.medication}")
        if result.patient_name:
            print(f"patient: {result.patient_name}")
        if result.dosage:
            print(f"dose: {result.dosage}")
        if result.time:
            print(f"time: {result.time}")
        print(f"Tone: {result.tone}")
        print("=" * 50)


if __name__ == "__main__":
    main()
