---
name: Recipe Manager
description: Helps add, edit, validate, and manage recipe data in recipes.js. Use this when the user wants to create new recipes, modify existing ones, fix recipe formatting, or validate recipe structure.
---

# Recipe Manager Skill

## Your Role

You specialize in managing recipe data for CookMode V2. You help users create, edit, and maintain recipe entries in the `recipes.js` file following the established schema and patterns.

## When to Use This Skill

Invoke this skill when the user wants to:
- Add a new recipe
- Edit an existing recipe
- Fix recipe formatting or structure
- Validate recipe data
- Convert recipe formats
- Bulk update recipe properties

## Recipe Data Schema (Structured Object Format)

### Standard Recipe Structure

```javascript
'recipe-slug': {
    name: 'Display Name',
    category: 'Entree' | 'Side' | 'Soup' | 'Dessert',
    components: {
        'Component Name': [
            {
                amount: number | string,    // 2, 0.5, '1/4', '1/3'
                unit: string,              // 'cup', 'tbsp', 'oz', 'lb', etc.
                ingredient: string,        // 'carrots', 'olive oil'
                prep: string               // Optional: 'diced', 'minced'
            }
        ]
    },
    instructions: [
        'Step 1 instructions',
        'Step 2 instructions'
    ],
    notes: 'Single string' | ['Array', 'of', 'strings'],
    images: ['url1.jpg', 'url2.jpg'] // optional
}
```

### Required Fields
- `name` (string): Display name of the recipe
- `category` (string): One of: Entree, Side, Soup, Dessert
- `components` (object): Ingredient lists grouped by component (array of objects)
- `instructions` (array): Step-by-step cooking instructions

### Optional Fields
- `notes` (string or array): Additional tips or information
- `images` (array): URLs to recipe photos

## Ingredient Object Structure

### Required Fields (per ingredient)
- `amount`: Number or fraction string
  - Numbers: `2`, `0.5`, `1.5`
  - Fractions: `'1/2'`, `'1/4'`, `'1/3'`
- `unit`: Unit of measurement
  - Volume: `'cup'`, `'tbsp'`, `'tsp'`
  - Weight: `'oz'`, `'lb'`, `'g'`, `'kg'`
  - Count: `'large'`, `'medium'`, `'small'`, `'cloves'`, `'whole'`
  - Other: `'recipe'`, `'pinch'`, `'dash'`
- `ingredient`: The ingredient name
  - Descriptive: `'all-purpose flour'`, `'cremini mushrooms'`
  - Simple: `'carrots'`, `'garlic'`, `'olive oil'`

### Optional Fields (per ingredient)
- `prep`: Preparation instructions
  - Cutting: `'diced'`, `'minced'`, `'sliced'`, `'chopped'`
  - State: `'softened'`, `'melted'`, `'room temperature'`
  - Additional: `'divided'`, `'plus more to taste'`, `'Pinot Noir recommended'`

### Examples

```javascript
// Simple ingredient
{ amount: 2, unit: 'cups', ingredient: 'flour' }

// With preparation
{ amount: 1, unit: 'large', ingredient: 'onion', prep: 'diced' }

// Fraction amount
{ amount: '1/4', unit: 'tsp', ingredient: 'salt' }

// Complex prep note
{ amount: 5, unit: 'large', ingredient: 'carrots', prep: 'peeled and sliced into large chunks' }

// Non-standard unit
{ amount: 1, unit: 'recipe', ingredient: 'mashed potatoes', prep: 'or serve with rice' }
```

### Scaling Logic (New)
Much simpler with object format!

```javascript
function scaleIngredient(ingredientObj, multiplier) {
    const scaledAmount = parseAmount(ingredientObj.amount) * multiplier;
    return {
        ...ingredientObj,
        amount: scaledAmount
    };
}

function parseAmount(amount) {
    if (typeof amount === 'number') return amount;
    if (amount.includes('/')) {
        const [num, den] = amount.split('/').map(Number);
        return num / den;
    }
    return parseFloat(amount);
}
```

### Display Formatting

```javascript
function formatIngredient(obj, orderCount = 1) {
    const scaledAmount = parseAmount(obj.amount) * orderCount;
    const prep = obj.prep ? `, ${obj.prep}` : '';
    return `${scaledAmount.toFixed(2)} ${obj.unit} ${obj.ingredient}${prep}`;
}

// Examples:
// { amount: 2, unit: 'cups', ingredient: 'flour' }
// → "2.00 cups flour"

// { amount: 1, unit: 'large', ingredient: 'onion', prep: 'diced' }
// → "1.00 large onion, diced"

// { amount: '1/4', unit: 'tsp', ingredient: 'salt', prep: 'plus more to taste' }
// → "0.25 tsp salt, plus more to taste"
```

## Category Order

Recipes display in this category order:
1. Entree
2. Side
3. Soup
4. Dessert

Defined in `/js/components/RecipeGrid.js:20`

## Notes Field Handling

The `RecipeModal.js` component handles notes in two formats:

1. **String**: Renders as single paragraph
2. **Array**: Renders each item as separate paragraph

```javascript
// Single note
notes: "Use a hand mixer for whipped texture."

// Multiple notes
notes: [
    "Use a hand mixer for whipped texture.",
    "Pairs well with mushroom bourguignon."
]
```

## Component Groups

Common component patterns:
- **Simple recipes**: Single component (e.g., 'Ingredients')
- **Complex recipes**: Multiple components (e.g., 'Dough', 'Filling', 'Topping')
- **Sauces**: Often separate component (e.g., 'Base', 'Sauce')

## Validation Checklist

When adding/editing recipes, verify:

- [ ] Slug is kebab-case (lowercase, hyphens)
- [ ] Name is human-readable
- [ ] Category is one of: Entree, Side, Soup, Dessert
- [ ] All ingredients are objects with `amount`, `unit`, `ingredient` fields
- [ ] `amount` is a number or fraction string ('1/2', '1/4')
- [ ] `unit` is a string (never empty)
- [ ] `ingredient` is a string (never empty)
- [ ] `prep` is optional string
- [ ] Components object has at least one entry
- [ ] Each component has array of ingredient objects
- [ ] Instructions array has at least one step
- [ ] Notes field is string OR array (not object)
- [ ] Images are valid URLs (if provided)
- [ ] No trailing commas in arrays/objects
- [ ] Proper JavaScript syntax

## Common Tasks

### Adding a New Recipe

1. Create kebab-case slug
2. Follow schema structure (object format)
3. Ensure all ingredients have `amount`, `unit`, `ingredient` fields
4. Add optional `prep` field for preparation notes
5. Add to appropriate category
6. Validate syntax

### Converting String Format to Object Format

**Old string format**:
```javascript
'2 cups all-purpose flour, sifted'
```

**New object format**:
```javascript
{ amount: 2, unit: 'cups', ingredient: 'all-purpose flour', prep: 'sifted' }
```

**Use ChatGPT/Claude to batch convert**:
> "Convert these recipe ingredients to structured format with amount, unit, ingredient, prep fields"

### Converting Recipes

When importing from external sources:
1. Extract name, category, ingredients, instructions
2. Group ingredients into components
3. Format ingredients with quantities first
4. Convert steps to array
5. Add to recipes.js

## File Location

**recipes.js**: `/Users/adamfehse/Documents/gitrepos/cookmodeV2/recipes.js`

This file is loaded as a global `window.RECIPES` object and accessed by:
- `App.js` - Passes to RecipeGrid and RecipeModal
- `RecipeGrid.js` - Displays cards and filters
- `RecipeModal.js` - Shows full recipe details

## Best Practices

1. **Keep it simple**: Pico CSS philosophy applies to data too
2. **Consistent formatting**: Follow existing patterns
3. **Clear component names**: 'Sauce', 'Dough', 'Filling' not 'Component 1'
4. **Precise quantities**: Include unit of measure
5. **Actionable instructions**: Each step should be clear

## Example: Adding a New Recipe (New Object Format)

```javascript
'chocolate-chip-cookies': {
    name: 'Chocolate Chip Cookies',
    category: 'Dessert',
    components: {
        'Dough': [
            { amount: 2, unit: 'cups', ingredient: 'all-purpose flour' },
            { amount: 1, unit: 'tsp', ingredient: 'baking soda' },
            { amount: 0.5, unit: 'tsp', ingredient: 'salt' },
            { amount: 1, unit: 'cup', ingredient: 'butter', prep: 'softened' },
            { amount: 0.75, unit: 'cup', ingredient: 'granulated sugar' },
            { amount: 0.75, unit: 'cup', ingredient: 'brown sugar' },
            { amount: 2, unit: 'large', ingredient: 'eggs' },
            { amount: 2, unit: 'tsp', ingredient: 'vanilla extract' }
        ],
        'Mix-ins': [
            { amount: 2, unit: 'cups', ingredient: 'chocolate chips' }
        ]
    },
    instructions: [
        'Preheat oven to 375°F.',
        'Mix flour, baking soda, and salt in a bowl.',
        'Cream butter and sugars until fluffy.',
        'Beat in eggs and vanilla.',
        'Gradually blend in flour mixture.',
        'Stir in chocolate chips.',
        'Drop rounded tablespoons onto ungreased cookie sheets.',
        'Bake 9-11 minutes or until golden brown.'
    ],
    notes: 'For chewier cookies, slightly underbake and let cool on baking sheet.'
}
```

### ChatGPT Conversion Prompt

Use this to convert existing recipes:

```
Convert this recipe to JavaScript object format with the following structure:
- amount: number or fraction string ('1/2', '1/4')
- unit: string (cup, tbsp, tsp, oz, lb, etc.)
- ingredient: string (the ingredient name)
- prep: string (optional, preparation notes like 'diced', 'softened')

[Paste recipe here]
```

Remember: Keep recipes cook-friendly and maintainable!
