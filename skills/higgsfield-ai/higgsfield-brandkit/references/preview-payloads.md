# Exact Brandkit preview payloads

Use with `preview --input`. Keep one to three complete review objects in `reviews`.

## Palette review

```json
{
  "reviews": [
    {
      "stage": "palette",
      "name": "Ink and Signal",
      "premise": "A restrained neutral base with one precise signal color.",
      "keywords": [
        "precise",
        "technical",
        "confident"
      ],
      "palette": [
        {
          "hex": "#101820",
          "name": "Ink"
        },
        {
          "hex": "#F7F7F5",
          "name": "Paper"
        },
        {
          "hex": "#00AEEF",
          "name": "Signal Blue"
        }
      ],
      "logo_ideas": [
        "A compact directional monogram",
        "A modular signal-shaped symbol"
      ],
      "background_color": "#F7F7F5",
      "text_color": "#101820"
    }
  ]
}
```

## Typography review

```json
{
  "reviews": [
    {
      "stage": "typography",
      "name": "Editorial Precision",
      "premise": "Expressive display type balanced by a neutral interface face.",
      "keywords": [
        "editorial",
        "clear",
        "warm"
      ],
      "palette": [],
      "logo_ideas": [],
      "display_font": {
        "family": "Fraunces",
        "source": "google:Fraunces",
        "weight": 700
      },
      "body_font": {
        "family": "Inter",
        "source": "google:Inter",
        "weight": 400
      },
      "headline": "Built for clear momentum",
      "body": "A compact specimen showing hierarchy, rhythm, and readability.",
      "background_color": "#F7F7F5",
      "text_color": "#101820"
    }
  ]
}
```

## Combined Essential Kit review

```json
{
  "reviews": [
    {
      "stage": "essential",
      "name": "Approved Northline system",
      "premise": "The separately approved logo, palette, and type system shown together.",
      "keywords": [
        "precise",
        "technical",
        "confident"
      ],
      "palette": [
        {
          "hex": "#101820",
          "name": "Ink"
        },
        {
          "hex": "#F7F7F5",
          "name": "Paper"
        },
        {
          "hex": "#00AEEF",
          "name": "Signal Blue"
        }
      ],
      "logo_ideas": [],
      "logo_svg": "/absolute/path/to/brandkit/logo/northline-symbol.svg",
      "display_font": {
        "family": "Fraunces",
        "source": "google:Fraunces",
        "weight": 700
      },
      "body_font": {
        "family": "Inter",
        "source": "google:Inter",
        "weight": 400
      },
      "headline": "Built for clear momentum",
      "body": "A compact specimen showing hierarchy, rhythm, and readability.",
      "background_color": "#F7F7F5",
      "text_color": "#101820"
    }
  ]
}
```

After the script succeeds, follow `inline-widgets.md`: screenshot each HTML board to a local PNG, inspect it, show the PNG inline when supported, and provide the absolute editable HTML path.
