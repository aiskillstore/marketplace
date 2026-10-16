# Themes, presets and tokens

Load public global styles first; see [installation](installation.md). Defaults work without a preset. For customization use the compiled [theme.ts](../examples/theme.ts), [root configuration API](api/core.md) and [public token catalog](api/tokens.md).

defineNeuPreset from the root entrypoint defines a named, typed light/dark token map. Register that object via provideNeuralUI with theme.preset in the application's providers. The repository's integration app uses exactly that configuration. Missing tokens retain their mode defaults; a preset does not select the current mode.

The application selects the mode through data-theme="light" or data-theme="dark" on the document element. Use Angular's injected DOCUMENT and apply browser-only preference detection in a browser render phase. Keep server/browser initial mode identical; do not read localStorage or matchMedia at module scope. The example switches mode in response to a user action and starts consistently in light mode.

Use public token names from the generated catalog or NeuTokenName exported by foundation. Never invent a token, copy private component variables, or assume a v1 variable survives. CSS cannot type-check token names: this repository scans authored SCSS as well as compiling typed presets.

The preset example changes only a few tokens. For a production palette, review the complete foreground/background pairs, button-specific tokens, focus indicators, disabled states and contrast in every mode. A successful typed preset compilation is not a contrast audit.

Root data-neu-theme="high-contrast" and forced-colors handling take precedence over custom preset values. Preserve these behaviors, reduced motion and focus visibility. Do not force themes by replacing internal component styles.

For build-time CSS generation, neuPresetCss is available from [foundation](api/foundation.md); the ordinary application path is defineNeuPreset plus provideNeuralUI. Keep CSS configuration trusted; do not accept arbitrary untrusted CSS as a preset.

Source: [official v2 theming](https://ui.neuralui.org/v2/en/foundations/theming).
