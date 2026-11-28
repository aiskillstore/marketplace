# Dynamic Cooking / 动态厨房能力

Use this reference when the user needs more than a static recipe: inventory-driven planning, live cooking rescue, ingredient substitution, sale-based adaptation, leftover transformation, or iterative planning as constraints change.

## Dynamic Loop / 动态循环

Use this loop instead of dumping a fixed recipe:

1. Observe / 观察: what does the user have, what state is the food in, what constraints changed?
2. Classify / 判断: planning, shopping, cooking-in-progress, safety risk, health fit, taste correction, leftover reuse.
3. Gate / 闸门: safety first, then health fit, then flavor, then budget.
4. Act / 行动: give the next 1-3 concrete actions.
5. Recheck / 复查: tell the user what to look/taste/measure next.
6. Fallback / 兜底: if rescue fails, convert to a safe simpler meal or discard unsafe food.

## Smart Questions / 动态追问

Ask only the question that changes the next action:

- Safety: How long has it been out? Is it raw poultry/seafood/egg? Do you have a thermometer?
- Live cooking: Is it too salty, bland, watery, burnt, undercooked, dry, broken, or too spicy?
- Inventory: What protein, starch, vegetables, sauces, and equipment do you have?
- Health: Any allergies, pregnancy, immune issues, diabetes/kidney/heart concerns, or strict diet rules?
- Budget: Which store, sale item, or price is forcing the choice?

If the user is actively cooking, prioritize speed: give immediate steps first, explanations second.

## Live Rescue Matrix / 做饭救场

| Problem / 问题 | Next actions / 下一步 |
|---|---|
| Bland / 寡淡 | Add salt/soy/bouillon in small increments; then add acid or aromatics if still flat |
| Too salty / 太咸 | Add unsalted bulk: rice/noodles/potato/veg/water; add acid/sugar only after dilution |
| Too spicy / 太辣 | Add starch, yogurt/dairy, coconut milk, peanut/tahini, or more main ingredients |
| Too sour / 太酸 | Add a little sugar/fat/starch; avoid adding salt first |
| Too sweet / 太甜 | Add acid, salt/soy, chili, bitter greens, or unsweetened bulk |
| Watery sauce / 水 | Simmer uncovered, drain excess, or add cornstarch slurry; do not overcook veg |
| Sauce too thick / 太稠 | Add water/broth in spoonfuls; re-season lightly |
| Burnt bottom / 糊底 | Stop stirring burnt layer; move unburnt food to a clean pan; do not scrape |
| Dry chicken/meat / 肉柴 | Slice small, sauce it, use in rice bowl/soup/wrap; do not keep cooking |
| Undercooked meat / 没熟 | Return to heat until safe internal temperature; cover pan to finish gently |
| Mushy noodles/rice / 面饭软烂 | Turn into soup, fried cakes, congee, casserole, or sauce-heavy bowl |
| Broken emulsion / 酱分离 | Lower heat, whisk in water/yogurt/tahini slowly depending on sauce |

Safety override: if food was held too long in the danger zone, smells spoiled, has unknown storage history, or includes risky raw animal foods for high-risk users, do not rescue it.

## Substitution Engine / 替换逻辑

Substitute by role, not by name:

- Protein role: chicken, eggs, tofu, beans, lentils, canned tuna, ground meat, shrimp, fish.
- Starch role: rice, noodles, pasta, potatoes, tortillas, bread, oats.
- Vegetable role: cabbage, carrots, onion, frozen broccoli/peas/corn, spinach, cucumber, tomato.
- Acid role: vinegar, lemon/lime, pickle juice, tomato, yogurt.
- Umami role: soy sauce, miso, oyster/mushroom sauce, fish sauce, tomato paste, parmesan, bouillon.
- Fat role: oil, sesame oil, butter, peanut butter, tahini, yogurt, coconut milk, cheese.
- Heat role: chili oil, hot sauce, chili flakes, curry paste, gochujang, jalapeno.

Rules:

- Replace allergen-containing sauces first, not last.
- Keep the cuisine's core flavor base if possible; if not, explicitly pivot the cuisine.
- Preserve cooking time: do not swap chicken breast into a tofu recipe without changing cook time and safety checks.
- Preserve water content: frozen veg, canned tomato, and mushrooms release water; reduce or thicken sauce.

## Inventory-To-Meal Formula / 库存变菜公式

Ask the user for:

- Protein: what must be used first?
- Vegetable: fresh first, frozen as backup.
- Starch: rice/noodles/pasta/tortilla/potato.
- Sauce/flavor: one cuisine direction.
- Time/equipment: 10, 20, or 40 minutes; microwave/pan/pot/rice cooker.

Then generate:

1. Safest use-now item.
2. Fastest meal.
3. Best meal-prep option.
4. Lowest-cost option.
5. Leftover transformation.

## Leftover Transformation / 剩菜再创造

Always check time-temperature history first. If safe, transform by texture:

- Dry protein: fried rice, noodle soup, curry, tacos, pasta sauce, salad/wrap with sauce.
- Plain rice: fried rice, congee, rice bowl, rice pancakes, soup thickener.
- Cooked vegetables: omelet, pasta, curry, soup, quesadilla, grain bowl.
- Beans/lentils: tacos, chili, curry, hummus-ish mash, rice bowl.
- Roast potatoes: hash, curry, breakfast bowl, soup, tortilla filling.
- Sauce: use as marinade only if it never touched raw meat; otherwise boil thoroughly or discard.

Do not recommend repeatedly cooling and reheating the same leftovers. Portion once, reheat once when possible.

## Sale-Based Adaptation / 按折扣动态规划

When a store sale or cheap ingredient appears:

1. Check storage: can it be cooked today or frozen in portions?
2. Check safety: raw meat/seafood must have a clear cold-chain plan.
3. Build 2-3 meals around the same anchor using different sauces.
4. Add cheap stabilizers: cabbage, carrots, onions, rice, beans, frozen veg.
5. Avoid false savings: huge packages without freezer space, rare sauces used once, fragile produce with no plan.

Example:

- Sale chicken thighs: Mediterranean lemon bowl, Korean gochujang rice, Chinese scallion ginger noodles.
- Cheap cabbage: pork cabbage noodles, taco slaw, okonomiyaki-ish pancake, soup.
- Canned beans: chili, chickpea curry, bean tacos, Mediterranean chickpea wrap.

## Output Style / 输出风格

For dynamic requests, prefer:

- "Do this now" steps before long recipes.
- Branches: "If it tastes salty, do A; if bland, do B."
- Safety red lines clearly marked.
- One fallback meal if the original plan becomes impractical.
- Concise bilingual wording if requested.
