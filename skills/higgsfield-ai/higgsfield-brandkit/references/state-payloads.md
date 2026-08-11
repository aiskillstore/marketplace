# Exact Brandkit state payloads

Write these complete JSON shapes into files under `"$BRANDKIT_WORKDIR"`. Replace values only. Keep asset objects, arrays, key names, and nesting unchanged.

## Visual axes

Use with `state --action set_visual_axes`:

```json
{
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  }
}
```

## Logo

Use with `state --action approve_logo`. For a user-supplied official logo, use the same `logo` object with `lock_authoritative_logo` and replace `approval_summary` with `source_summary`.

```json
{
  "approval_summary": "User selected the Northline symbol.",
  "logo": {
    "name": "Northline symbol",
    "asset": {
      "id": "replace-with-upload-or-job-id",
      "url": "https://replace-with-exact-approved-logo.svg"
    },
    "geometry_fingerprint": "replace-with-logo-inspect-fingerprint"
  }
}
```

`logo.asset` is always an object, never a URL string. It requires at least one durable locator: `id`, `url`, or an absolute local `path`. For a user-supplied local SVG, use:

```json
{"path": "/absolute/path/to/official-logo.svg"}
```

Get `geometry_fingerprint` from `logo-inspect --source <exact SVG URL or absolute path>` before approval. This uses the same full-canvas-background handling as `logo-export`.

## Palette

Use with `state --action approve_palette`. For a user-supplied official palette, use `lock_authoritative_palette` and replace `approval_summary` with `source_summary`.

```json
{
  "approval_summary": "User selected the Ink and Signal palette.",
  "palette": {
    "colors": [
      {
        "hex": "#101820",
        "name": "Ink",
        "role": "background"
      },
      {
        "hex": "#F7F7F5",
        "name": "Paper",
        "role": "text"
      },
      {
        "hex": "#00AEEF",
        "name": "Signal Blue",
        "role": "accent"
      }
    ],
    "gradients": []
  }
}
```

`palette.colors` contains 2–12 color objects. Every hex value includes `#`.

## Typography

Use with `state --action approve_typography`. For user-supplied official typography, use `lock_authoritative_typography` and replace `approval_summary` with `source_summary`.

```json
{
  "approval_summary": "User selected Fraunces with Inter.",
  "typography": {
    "display": {
      "family": "Fraunces",
      "source": "google:Fraunces",
      "style": "normal",
      "weight": 700
    },
    "body": {
      "family": "Inter",
      "source": "google:Inter",
      "style": "normal",
      "weight": 400
    },
    "font_links": [
      "https://fonts.google.com/specimen/Fraunces",
      "https://fonts.google.com/specimen/Inter"
    ]
  }
}
```

## Approved downstream element

Use with `state --action approve_brandbook_element` only after explicit approval:

```json
{
  "approval_summary": "User approved the primary poster.",
  "required_slots": [
    "logo",
    "palette",
    "typography"
  ],
  "brandbook_element": {
    "key": "poster-primary",
    "kind": "poster",
    "name": "Primary campaign poster",
    "asset": {
      "path": "/absolute/path/to/approved-poster.svg"
    }
  }
}
```
