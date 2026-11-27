#!/usr/bin/env python3
"""Safety and health screen for liuzi-kitchen meal plans."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


ALLERGEN_KEYWORDS = {
    "milk": ["milk", "cheese", "yogurt", "cream", "butter", "dairy", "牛奶", "奶酪", "酸奶", "黄油"],
    "eggs": ["egg", "eggs", "mayo", "mayonnaise", "鸡蛋", "蛋黄酱"],
    "fish": ["fish", "tuna", "salmon", "anchovy", "鱼", "金枪鱼", "三文鱼"],
    "shellfish": ["shrimp", "crab", "lobster", "oyster", "clam", "虾", "蟹", "龙虾", "牡蛎", "蛤"],
    "tree-nuts": ["almond", "walnut", "cashew", "pistachio", "pecan", "hazelnut", "杏仁", "核桃", "腰果"],
    "peanuts": ["peanut", "花生"],
    "wheat": ["wheat", "noodle", "pasta", "bread", "tortilla", "flour", "小麦", "面条", "意面", "面包", "面粉"],
    "soy": ["soy", "tofu", "miso", "edamame", "tempeh", "soy sauce", "大豆", "豆腐", "味噌", "酱油"],
    "sesame": ["sesame", "tahini", "芝麻", "芝麻油"],
}

SAFETY_TEMP = {
    "chicken": ("165 F / 74 C", "鸡肉/禽类必须到 165 F / 74 C。", "Poultry must reach 165 F / 74 C."),
    "poultry": ("165 F / 74 C", "禽类必须到 165 F / 74 C。", "Poultry must reach 165 F / 74 C."),
    "ground-meat": ("160 F / 71 C", "肉馅通常至少到 160 F / 71 C；禽肉馅到 165 F / 74 C。", "Ground meat usually needs 160 F / 71 C; ground poultry needs 165 F / 74 C."),
    "pork": ("145 F / 63 C", "整块猪肉到 145 F / 63 C 并静置；猪肉馅到 160 F / 71 C。", "Whole pork cuts need 145 F / 63 C with rest; ground pork needs 160 F / 71 C."),
    "beef": ("145 F / 63 C", "整块牛肉到 145 F / 63 C 并静置；牛肉馅到 160 F / 71 C。", "Whole beef cuts need 145 F / 63 C with rest; ground beef needs 160 F / 71 C."),
    "fish": ("145 F / 63 C", "鱼类到 145 F / 63 C。", "Fish needs 145 F / 63 C."),
    "eggs": ("160 F / 71 C", "蛋类菜肴到 160 F / 71 C；高风险人群避免流心蛋。", "Egg dishes need 160 F / 71 C; high-risk users should avoid runny eggs."),
    "leftovers": ("165 F / 74 C", "剩菜复热到 165 F / 74 C。", "Reheat leftovers to 165 F / 74 C."),
    "tofu": ("leftover 165 F / 74 C", "豆腐开封后冷藏；剩菜复热到 165 F / 74 C。", "Refrigerate opened tofu; reheat leftovers to 165 F / 74 C."),
    "beans": ("leftover 165 F / 74 C", "豆类剩菜复热到 165 F / 74 C。", "Reheat bean leftovers to 165 F / 74 C."),
    "none": ("n/a", "没有识别到高风险动物蛋白。", "No high-risk animal protein identified."),
}


@dataclass
class Finding:
    level: str
    zh: str
    en: str


def split_csv(value: str) -> list[str]:
    if not value or value.lower() == "none":
        return []
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def contains_any(text: str, words: list[str]) -> bool:
    lower = text.lower()
    return any(word.lower() in lower for word in words)


def render(finding: Finding, lang: str) -> str:
    if lang == "zh":
        return f"[{finding.level}] {finding.zh}"
    if lang == "en":
        return f"[{finding.level}] {finding.en}"
    return f"[{finding.level}] {finding.zh} / {finding.en}"


def add(findings: list[Finding], level: str, zh: str, en: str) -> None:
    findings.append(Finding(level, zh, en))


def main() -> None:
    parser = argparse.ArgumentParser(description="Check a student meal plan for food safety and health fit.")
    parser.add_argument("--ingredients", default="", help="Comma-separated ingredient list.")
    parser.add_argument("--allergies", default="none", help="Comma-separated allergens to avoid, e.g. milk,eggs,soy.")
    parser.add_argument("--risk", default="none", help="Comma-separated risk flags: pregnant,immunocompromised,older-child,severe-allergy,diabetes,kidney,heart,eating-disorder.")
    parser.add_argument("--goal", default="balanced", help="balanced, high-protein, lower-sodium, lower-sugar, diabetes-friendly, heart-health, training, weight-loss, vegan, vegetarian.")
    parser.add_argument("--protein", default="none", choices=SAFETY_TEMP.keys())
    parser.add_argument("--veg", default="unknown", choices=("yes", "no", "unknown"))
    parser.add_argument("--starch", default="unknown", help="rice,noodles,pasta,potato,whole-grain,none,unknown")
    parser.add_argument("--raw-animal", default="no", choices=("yes", "no", "unknown"))
    parser.add_argument("--leftover-hours", type=float, default=0, help="Hours food may sit at room temperature before chilling.")
    parser.add_argument("--reheat-temp-f", type=float, default=0, help="Known leftover reheat temp in Fahrenheit; 0 if unknown/not leftovers.")
    parser.add_argument("--sodium", default="unknown", choices=("low", "moderate", "high", "unknown"))
    parser.add_argument("--added-sugar", default="unknown", choices=("low", "moderate", "high", "unknown"))
    parser.add_argument("--sat-fat", default="unknown", choices=("low", "moderate", "high", "unknown"))
    parser.add_argument("--fried", default="no", choices=("yes", "no", "unknown"))
    parser.add_argument("--lang", choices=("zh", "en", "zh-en"), default="zh-en")
    args = parser.parse_args()

    findings: list[Finding] = []
    ingredients = args.ingredients
    allergies = split_csv(args.allergies)
    risks = split_csv(args.risk)
    goal = args.goal.lower()

    for allergen in allergies:
        keywords = ALLERGEN_KEYWORDS.get(allergen, [allergen])
        if contains_any(ingredients, keywords):
            add(findings, "FAIL", f"过敏冲突: 食材可能含有 {allergen}。请替换并检查标签/交叉接触。", f"Allergy conflict: ingredients may contain {allergen}. Replace it and check labels/cross-contact.")

    if "severe-allergy" in risks and allergies:
        add(findings, "WARN", "严重过敏: 共用厨房需使用单独器具、清洁台面，并优先买密封标识清楚的食材。", "Severe allergy: in shared kitchens, use separate utensils, clean surfaces, and prefer sealed clearly labeled foods.")

    temp, zh_temp, en_temp = SAFETY_TEMP[args.protein]
    if args.protein != "none":
        add(findings, "PASS", zh_temp, en_temp)

    high_risk = {"pregnant", "immunocompromised", "older-child"} & set(risks)
    if args.raw_animal == "yes":
        level = "FAIL" if high_risk else "WARN"
        add(findings, level, "含生/未熟动物性食材: 建议改为全熟版本，尤其孕期、免疫低下、老人儿童。", "Raw/undercooked animal food: switch to fully cooked, especially for pregnancy, immunocompromise, older adults, or children.")

    if args.leftover_hours > 2:
        add(findings, "FAIL", "剩菜室温超过 2 小时: 不建议食用。高温环境超过 1 小时也应丢弃。", "Leftovers sat over 2 hours at room temperature: do not eat. In hot conditions, discard after 1 hour.")
    elif args.leftover_hours > 0:
        add(findings, "PASS", "剩菜时间在 2 小时内: 尽快浅盒冷藏。", "Leftover time is under 2 hours: chill promptly in shallow containers.")

    if args.reheat_temp_f and args.reheat_temp_f < 165:
        add(findings, "WARN", "剩菜复热温度低于 165 F / 74 C: 继续加热后再吃。", "Leftover reheat temp is below 165 F / 74 C: heat more before eating.")
    elif args.reheat_temp_f >= 165:
        add(findings, "PASS", "剩菜已复热到 165 F / 74 C。", "Leftovers reached 165 F / 74 C.")

    if args.veg == "yes":
        add(findings, "PASS", "有蔬菜/水果组成，利于纤维和微量营养素。", "Includes vegetables/fruit, supporting fiber and micronutrients.")
    elif args.veg == "no":
        add(findings, "WARN", "缺少蔬菜/水果: 加 1-2 把冷冻蔬菜、包菜、胡萝卜、黄瓜或水果。", "Missing vegetables/fruit: add 1-2 handfuls of frozen veg, cabbage, carrots, cucumber, or fruit.")

    if args.protein == "none":
        add(findings, "WARN", "蛋白质不明确: 加鸡蛋、豆腐、豆类、酸奶、鱼、鸡肉或瘦肉。", "Protein is unclear: add eggs, tofu, beans, yogurt, fish, chicken, or lean meat.")

    if args.starch == "none" and goal not in {"lower-carb", "diabetes-friendly"}:
        add(findings, "WARN", "没有主食/能量来源: 若不是刻意低碳，可加米饭、土豆、燕麦、意面或全谷物。", "No starch/energy source: unless intentionally lower-carb, add rice, potatoes, oats, pasta, or whole grains.")
    elif args.starch in {"whole-grain", "potato", "oats", "beans"}:
        add(findings, "PASS", "主食选择有较好的饱腹感或纤维潜力。", "Starch choice has good satiety or fiber potential.")

    if args.sodium == "high":
        add(findings, "WARN", "钠可能偏高: 减少酱油/高汤粉/加工肉，用醋、柠檬、香料、葱姜蒜补味。", "Sodium may be high: reduce soy/bouillon/processed meats and use vinegar, lemon, spices, garlic, ginger, and scallion.")
    if args.added_sugar == "high":
        add(findings, "WARN", "添加糖可能偏高: 减少甜饮和甜酱，用水果或少量糖平衡酸辣即可。", "Added sugar may be high: reduce sweet drinks/sauces; use fruit or small sugar amounts only to balance acidity/heat.")
    if args.sat_fat == "high":
        add(findings, "WARN", "饱和脂肪可能偏高: 少用黄油/奶油/肥肉/大量奶酪，改用植物油、酸奶、豆类或瘦蛋白。", "Saturated fat may be high: reduce butter/cream/fatty meats/large cheese portions; use oils, yogurt, beans, or lean protein.")
    if args.fried == "yes":
        add(findings, "WARN", "油炸频率高: 可改成煎、烤、空气炸，并增加蔬菜和酸味解腻。", "Frequent frying: try pan-searing, baking, or air-frying, and add vegetables plus acidity.")

    if goal in {"diabetes-friendly", "heart-health", "kidney"} or {"diabetes", "heart", "kidney"} & set(risks):
        add(findings, "WARN", "涉及慢性病饮食: 这里只能做一般筛查，个人碳水/钠/钾/蛋白目标请按医生或注册营养师建议。", "Chronic-condition nutrition: this is only a general screen; follow clinician or registered dietitian targets for carbs/sodium/potassium/protein.")
    if "eating-disorder" in risks:
        add(findings, "WARN", "有进食障碍史: 避免严格限制和热量执念，建议与专业人士一起制定饮食计划。", "Eating disorder history: avoid strict restriction/calorie fixation and plan with professional support.")

    if not findings:
        add(findings, "PASS", "没有发现明显安全或健康红旗；仍需按实际标签、温度和个人情况确认。", "No obvious safety or health red flags found; still confirm labels, temperatures, and personal needs.")

    fail_count = sum(1 for item in findings if item.level == "FAIL")
    warn_count = sum(1 for item in findings if item.level == "WARN")
    if args.lang == "en":
        print(f"Meal Check Summary: {fail_count} fail, {warn_count} warn")
    elif args.lang == "zh":
        print(f"餐食检查总结: {fail_count} 个失败, {warn_count} 个提醒")
    else:
        print(f"餐食检查总结: {fail_count} 个失败, {warn_count} 个提醒 / Meal Check Summary: {fail_count} fail, {warn_count} warn")
    print("=" * 64)
    for finding in findings:
        print(render(finding, args.lang))


if __name__ == "__main__":
    main()
