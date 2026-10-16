# Installation and configuration

Baseline: @neural-ui/core **2.0.1**, Angular/CDK **22**. Inspect the application's existing versions before installing. Do not use a floating latest tag for this verified baseline.

In an existing Angular 22 application:

```sh
npm install @neural-ui/core@2.0.1 @angular/cdk@22
npm ls @neural-ui/core @angular/core @angular/common @angular/forms @angular/router @angular/cdk
```

The published peers also require @schematics/angular and @angular-devkit/schematics in the 22.x range; these normally come with Angular CLI. Respect the package peer ranges and use compatible Angular packages. Never resolve conflicts with --force or --legacy-peer-deps. The repository's integration fixture pins all Angular packages to 22.2.2 and TypeScript to 6.0.3; that is the tested toolchain, not a promise about every 22.x release.

Load the global stylesheet once in the Angular build's global SCSS:

```scss
@use '@neural-ui/core/styles' as *;
```

Do not also register it a second time via a schematic. The ng-add schematic is available, but this skill tests the manual path. In a CSS-only application, create a global SCSS file and register it in angular.json. Shared overlay styles are included by the public style entrypoint.

Import components into the standalone component that owns the template. Follow [the generated API index](api/index.md), rather than importing UI components from the root barrel. For example the verified [forms example](../examples/forms.ts) uses /input, /select and /button.

Basic components need no global Neural provider. The optional provideNeuralUI root export configures locale, timeZone, now and theme.preset; see [the root configuration contract](api/core.md). Do not invent a theme mode option in that provider.

Core supplies structural icon fallbacks. For application icons, project SVG where the component supports projection or integrate the public provideNeuIconResolver from [foundation](api/foundation.md). A random icon string does not install an icon catalog. Neural Icons is a separate optional package; it is not a dependency of this skill or its examples.

Source: [official v2 installation](https://ui.neuralui.org/v2/en/getting-started/installation).
