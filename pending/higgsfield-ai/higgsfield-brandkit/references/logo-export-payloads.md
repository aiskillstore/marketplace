# Exact Brandkit logo-export payloads

Use with `logo-export --input`:

```json
{
  "name": "northline-symbol",
  "logo_svg": "https://replace-with-selected-recraft-result.svg",
  "delivery": "user",
  "replacements": [],
  "include_monochrome": false
}
```

For an explicitly requested one-color export, add `"single_color": "#101820"`.

For explicitly requested black/white production variants, set `"include_monochrome": true` and add `"primary_color": "#00AEEF"`.

Keep returned SVG and PNG files in `"$BRANDKIT_WORKDIR/logo"`. Deliver their absolute paths. Use the local PNG for later `--image` generation references; keep the SVG as the editable geometry source. Never label a rasterized `.png` as SVG.
