# Input contract

The calculator accepts one JSON object.

| Field | Requirement |
|---|---|
| `total_guests` | Integer from 1 through 10,000 |
| `drinking_guests` | Integer from 0 through `total_guests` |
| `duration_hours` | Number from 1 through 12 |
| `country` | Non-empty planning jurisdiction |
| `mix` | Object with non-negative `beer`, `wine`, and `cocktails` shares totaling 1.0 |
| `buffer_percent` | Optional number from 0 through 25, default 10 |
| `planning_assumptions` | Required object described below |
| `package_yields` | Required positive serving yields for `beer_units`, `wine_bottles`, and `spirit_bottles` |
| `inventory` | Optional counts for `beer_units`, `wine_bottles`, and `spirit_bottles` |
| `cocktail_recipes` | Optional list of recipes with `name`, positive `share`, and non-empty `ingredients` |

Each ingredient contains `name` and a positive `amount_oz` per serving. Add `inventory_oz` when the available amount is known.

`planning_assumptions` contains these fields.

| Field | Requirement |
|---|---|
| `alcoholic_servings_per_drinking_guest` | Number from 0 through 12 |
| `nonalcoholic_servings_per_guest` | Number from 0 through 24 |
| `water_liters_per_guest` | Number from 0 through 10 |
| `ice_amount_per_guest` | Number from 0 through 10 |
| `ice_unit` | `lb` or `kg` |
| `source` | Non-empty source, rationale, or named approver |
| `reviewed_on` | Date or review label supplied by the user |

This example exercises the named-cocktail and inventory branches.

```json
{
  "total_guests": 24,
  "drinking_guests": 18,
  "duration_hours": 4,
  "country": "US",
  "mix": {
    "beer": 0.35,
    "wine": 0.25,
    "cocktails": 0.4
  },
  "planning_assumptions": {
    "alcoholic_servings_per_drinking_guest": 4,
    "nonalcoholic_servings_per_guest": 3,
    "water_liters_per_guest": 1.2,
    "ice_amount_per_guest": 1.5,
    "ice_unit": "lb",
    "source": "host-approved base scenario",
    "reviewed_on": "2026-07-27"
  },
  "package_yields": {
    "beer_units": 1,
    "wine_bottles": 5,
    "spirit_bottles": 16
  },
  "buffer_percent": 10,
  "inventory": {
    "beer_units": 12,
    "wine_bottles": 2,
    "spirit_bottles": 1
  },
  "cocktail_recipes": [
    {
      "name": "Daiquiri",
      "share": 1,
      "ingredients": [
        {
          "name": "light rum",
          "amount_oz": 2,
          "inventory_oz": 12
        },
        {
          "name": "lime juice",
          "amount_oz": 1
        },
        {
          "name": "simple syrup",
          "amount_oz": 0.75
        }
      ]
    }
  ]
}
```

The calculator applies the buffer after the approved alcoholic-serving
assumption. It never inserts a servings rate, hydration quantity, ice factor, or
package yield.

Named cocktail ingredients are reported in fluid ounces and milliliters. The
user remains responsible for checking local package labels and service rules.
