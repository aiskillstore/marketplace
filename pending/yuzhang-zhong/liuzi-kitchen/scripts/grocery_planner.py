#!/usr/bin/env python3
"""Bilingual grocery quantity planner for the liuzi-kitchen skill."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    protein_g: int
    starch_dry_g: int
    veg_g: int
    sauce_tbsp: float
    oil_tbsp: float


PROFILES = {
    "balanced": Profile(protein_g=150, starch_dry_g=75, veg_g=250, sauce_tbsp=1.5, oil_tbsp=0.75),
    "high-protein": Profile(protein_g=210, starch_dry_g=55, veg_g=250, sauce_tbsp=1.75, oil_tbsp=0.75),
    "budget": Profile(protein_g=115, starch_dry_g=85, veg_g=275, sauce_tbsp=1.25, oil_tbsp=0.6),
}

PROTEIN_LABELS = {
    "chicken": ("鸡肉", "chicken"),
    "pork": ("猪肉", "pork"),
    "beef": ("牛肉", "beef"),
    "tofu": ("豆腐", "tofu"),
    "eggs": ("鸡蛋", "eggs"),
    "beans": ("豆类/罐头豆", "beans"),
    "shrimp": ("虾", "shrimp"),
    "fish": ("鱼", "fish"),
}

STARCH_LABELS = {
    "rice": ("米", "rice"),
    "noodles": ("面条", "noodles"),
    "pasta": ("意面", "pasta"),
    "potatoes": ("土豆", "potatoes"),
    "tortillas": ("墨西哥饼", "tortillas"),
}

VEG_LABELS = {
    "fresh": ("新鲜蔬菜", "fresh vegetables"),
    "frozen": ("冷冻蔬菜", "frozen vegetables"),
    "mixed": ("新鲜+冷冻蔬菜", "fresh + frozen vegetables"),
}

CUISINE_KITS = {
    "neutral": {
        "name": ("通用", "neutral"),
        "seasoning": ("盐、黑胡椒、蒜、洋葱、醋或柠檬、基础酱油/高汤", "salt, black pepper, garlic, onion, vinegar or lemon, basic soy/broth"),
        "dishes": ("盖饭、炒面、一锅炖、卷饼、清冰箱炒饭", "rice bowls, stir-fried noodles, one-pot stews, wraps, cleanout fried rice"),
    },
    "chinese": {
        "name": ("中式", "Chinese"),
        "seasoning": ("酱油、醋、蚝油或素蚝油、豆瓣酱/辣油、姜蒜葱、淀粉", "soy sauce, vinegar, oyster or mushroom sauce, doubanjiang/chili oil, ginger-garlic-scallion, cornstarch"),
        "dishes": ("番茄炒蛋饭、麻婆豆腐、包菜肉丝面、葱姜鸡饭、炒饭", "tomato egg rice, mapo-ish tofu, cabbage pork noodles, scallion ginger chicken rice, fried rice"),
    },
    "japanese-korean": {
        "name": ("日式韩式", "Japanese-Korean"),
        "seasoning": ("味噌或韩式辣酱、酱油、米醋、芝麻油、泡菜、海苔/芝麻", "miso or gochujang, soy sauce, rice vinegar, sesame oil, kimchi, nori/sesame"),
        "dishes": ("简化拌饭、泡菜豆腐锅、照烧鸡饭、味噌汤面、金枪鱼饭", "bibimbap-ish bowls, kimchi tofu stew, teriyaki chicken rice, miso noodle soup, tuna rice bowls"),
    },
    "southeast-asian": {
        "name": ("东南亚", "Southeast Asian"),
        "seasoning": ("鱼露或酱油、青柠/醋、花生酱、椰奶、咖喱酱/粉、香菜", "fish sauce or soy sauce, lime/vinegar, peanut butter, coconut milk, curry paste/powder, cilantro"),
        "dishes": ("花生拌面、椰奶咖喱、打抛饭、越式饭碗、菠萝蛋炒饭", "peanut noodles, coconut curry, basil protein rice, Vietnamese-ish bowls, pineapple egg fried rice"),
    },
    "south-asian": {
        "name": ("南亚", "South Asian"),
        "seasoning": ("咖喱粉/孜然/姜黄/香菜籽、姜蒜洋葱、番茄、酸奶、柠檬", "curry powder/cumin/turmeric/coriander, ginger-garlic-onion, tomato, yogurt, lemon"),
        "dishes": ("红扁豆咖喱、鹰嘴豆咖喱、鸡肉咖喱、鸡蛋咖喱、香料土豆卷", "red lentil dal, chickpea curry, chicken curry, egg curry, spiced potato wraps"),
    },
    "mediterranean": {
        "name": ("地中海", "Mediterranean"),
        "seasoning": ("橄榄油、柠檬、蒜、牛至/莳萝/欧芹、酸奶或芝麻酱、番茄膏", "olive oil, lemon, garlic, oregano/dill/parsley, yogurt or tahini, tomato paste"),
        "dishes": ("希腊鸡肉饭、鹰嘴豆卷、番茄金枪鱼意面、番茄炖蛋、香草土豆", "Greek-ish chicken bowls, chickpea wraps, tomato tuna pasta, shakshuka-ish eggs, herb potatoes"),
    },
    "middle-eastern": {
        "name": ("中东/北非", "Middle Eastern/North African"),
        "seasoning": ("孜然、香菜籽、红椒粉、哈里萨、柠檬、酸奶、芝麻酱", "cumin, coriander, paprika, harissa, lemon, yogurt, tahini"),
        "dishes": ("扁豆洋葱饭、哈里萨鸡饭、鹰嘴豆番茄炖菜、简化肉丸、鹰嘴豆泥拼盘", "mujadara, harissa chicken bowls, chickpea tomato stew, kofta-ish meatballs, hummus plates"),
    },
    "mexican-latin": {
        "name": ("墨西哥/拉美", "Mexican/Latin American"),
        "seasoning": ("孜然、辣椒粉、牛至、莎莎酱、青柠、香菜、奶酪或酸奶", "cumin, chili powder, oregano, salsa, lime, cilantro, cheese or yogurt"),
        "dishes": ("豆子鸡蛋塔可、鸡肉饭碗、肉馅塔可锅、黑豆芝士饼、土豆肉末", "bean egg tacos, chicken burrito bowls, taco skillet, black bean quesadillas, picadillo-ish potatoes"),
    },
    "american-european": {
        "name": ("美式/欧洲家常", "American/European"),
        "seasoning": ("蒜粉/洋葱粉、芥末、番茄、奶酪、香草、泡菜或醋", "garlic/onion powder, mustard, tomato, cheese, herbs, pickles or vinegar"),
        "dishes": ("辣豆肉酱、一锅芝士豌豆面、蒜香番茄意面、芥末鸡肉土豆、包菜土豆鸡蛋锅", "chili, one-pot mac and peas, garlic tomato pasta, mustard chicken potatoes, cabbage potato egg hash"),
    },
    "african-caribbean": {
        "name": ("非洲/加勒比", "African/Caribbean"),
        "seasoning": ("花生酱、番茄膏、姜蒜洋葱、百里香/多香果/咖喱粉、椰奶、青柠", "peanut butter, tomato paste, ginger-garlic-onion, thyme/allspice/curry powder, coconut milk, lime"),
        "dishes": ("花生炖菜、简化西非番茄饭、香料红扁豆炖菜、加勒比香料鸡饭、椰香豆饭", "peanut stew, jollof-ish rice, spiced red lentil stew, jerk-ish chicken bowls, coconut rice and peas"),
    },
}

SAFETY = {
    "chicken": ("鸡肉中心温度到 165 F / 74 C。", "Cook chicken to 165 F / 74 C."),
    "pork": ("猪肉片到 145 F / 63 C 并静置；肉馅到 160 F / 71 C。", "Cook pork cuts to 145 F / 63 C with rest; ground pork to 160 F / 71 C."),
    "beef": ("牛肉片到 145 F / 63 C 并静置；肉馅到 160 F / 71 C。", "Cook beef cuts to 145 F / 63 C with rest; ground beef to 160 F / 71 C."),
    "tofu": ("豆腐开封后冷藏，剩菜复热到 165 F / 74 C。", "Refrigerate opened tofu; reheat leftovers to 165 F / 74 C."),
    "eggs": ("鸡蛋做熟到蛋黄蛋白凝固；蛋类菜肴到 160 F / 71 C。", "Cook eggs until yolk and white are firm; egg dishes to 160 F / 71 C."),
    "beans": ("罐头豆开封后冷藏；剩菜复热到 165 F / 74 C。", "Refrigerate opened beans; reheat leftovers to 165 F / 74 C."),
    "shrimp": ("虾煮到不透明且紧实，避免过熟。", "Cook shrimp until opaque and firm."),
    "fish": ("鱼中心温度到 145 F / 63 C。", "Cook fish to 145 F / 63 C."),
}


def round_package(amount: float, unit: str) -> str:
    if unit == "g":
        if amount >= 1000:
            return f"{amount / 1000:.1f} kg"
        return f"{math.ceil(amount / 25) * 25:.0f} g"
    if unit == "tbsp":
        return f"{amount:.1f} tbsp"
    return f"{amount:.0f} {unit}"


def line(zh: str, en: str, lang: str) -> str:
    if lang == "zh":
        return zh
    if lang == "en":
        return en
    return f"{zh} / {en}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a bilingual student-kitchen grocery plan.")
    parser.add_argument("--servings", type=int, default=4, help="Servings per meal.")
    parser.add_argument("--meals", type=int, default=3, help="Number of meals to cover.")
    parser.add_argument("--profile", choices=PROFILES.keys(), default="balanced")
    parser.add_argument("--protein", choices=PROTEIN_LABELS.keys(), default="chicken")
    parser.add_argument("--starch", choices=STARCH_LABELS.keys(), default="rice")
    parser.add_argument("--veg", choices=VEG_LABELS.keys(), default="mixed")
    parser.add_argument("--cuisine", choices=CUISINE_KITS.keys(), default="neutral")
    parser.add_argument("--lang", choices=("zh", "en", "zh-en"), default="zh-en")
    args = parser.parse_args()

    total_servings = args.servings * args.meals
    profile = PROFILES[args.profile]
    protein_total = profile.protein_g * total_servings
    starch_total = profile.starch_dry_g * total_servings
    veg_total = profile.veg_g * total_servings
    sauce_total = profile.sauce_tbsp * total_servings
    oil_total = profile.oil_tbsp * total_servings

    protein_zh, protein_en = PROTEIN_LABELS[args.protein]
    starch_zh, starch_en = STARCH_LABELS[args.starch]
    veg_zh, veg_en = VEG_LABELS[args.veg]
    safety_zh, safety_en = SAFETY[args.protein]
    cuisine = CUISINE_KITS[args.cuisine]
    cuisine_zh, cuisine_en = cuisine["name"]
    seasoning_zh, seasoning_en = cuisine["seasoning"]
    dishes_zh, dishes_en = cuisine["dishes"]

    print(line("留子厨房采购量", "Liuzi Kitchen Grocery Quantities", args.lang))
    print("=" * 44)
    print(line(f"覆盖: {args.meals} 餐 x 每餐 {args.servings} 份 = {total_servings} 份", f"Covers: {args.meals} meals x {args.servings} servings = {total_servings} servings", args.lang))
    print(line(f"模式: {args.profile}", f"Profile: {args.profile}", args.lang))
    print(line(f"菜系: {cuisine_zh}", f"Cuisine: {cuisine_en}", args.lang))
    print()
    print(line("购物清单", "Shopping list", args.lang))
    print("- " + line(f"{protein_zh}: {round_package(protein_total, 'g')}", f"{protein_en}: {round_package(protein_total, 'g')}", args.lang))
    print("- " + line(f"{starch_zh}: {round_package(starch_total, 'g')} 干重或等量主食", f"{starch_en}: {round_package(starch_total, 'g')} dry weight or equivalent starch", args.lang))
    print("- " + line(f"{veg_zh}: {round_package(veg_total, 'g')}", f"{veg_en}: {round_package(veg_total, 'g')}", args.lang))
    print("- " + line(f"酱料/调味: 约 {round_package(sauce_total, 'tbsp')}", f"sauce/seasoning: about {round_package(sauce_total, 'tbsp')}", args.lang))
    print("- " + line(f"食用油: 约 {round_package(oil_total, 'tbsp')}", f"cooking oil: about {round_package(oil_total, 'tbsp')}", args.lang))
    print("- " + line(f"菜系调味包: {seasoning_zh}", f"cuisine seasoning kit: {seasoning_en}", args.lang))
    print()
    print(line("菜品方向", "Dish directions", args.lang))
    print("- " + line(dishes_zh, dishes_en, args.lang))
    print()
    print(line("安全提示", "Safety note", args.lang))
    print("- " + line(safety_zh, safety_en, args.lang))
    print("- " + line("生熟分开；剩菜 2 小时内冷藏，复热到 165 F / 74 C。", "Separate raw and ready-to-eat foods; chill leftovers within 2 hours and reheat to 165 F / 74 C.", args.lang))
    print()
    print(line("健康合理性提示", "Health fit notes", args.lang))
    print("- " + line("默认按 蛋白质 + 蔬菜 + 主食 + 适量油脂 搭配；如有过敏、慢性病、孕期或训练目标，需要先按个人情况调整。", "Default balance is protein + vegetables + starch + intentional fat; adjust first for allergies, chronic conditions, pregnancy, or training goals.", args.lang))
    print("- " + line("若酱料较咸，用醋/柠檬/香料/葱姜蒜补味，并减少酱油、高汤粉和加工肉。", "If sauces are salty, use vinegar/lemon/spices/aromatics for flavor and reduce soy sauce, bouillon, and processed meats.", args.lang))
    print()
    print(line("性价比提示", "Value tips", args.lang))
    print("- " + line("按单位价格比较；优先买能跨 2-3 道菜复用的食材。", "Compare unit prices; prioritize ingredients reused across 2-3 dishes.", args.lang))
    print("- " + line("肉类买回后按每餐份量分装冷冻，蔬菜用一半冷冻一半新鲜降低损耗。", "Portion and freeze proteins; mix frozen and fresh vegetables to reduce waste.", args.lang))


if __name__ == "__main__":
    main()
