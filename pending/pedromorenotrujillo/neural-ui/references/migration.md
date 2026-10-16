# Migration from v1 to the verified v2 baseline

Treat old application code as migration input, never as evidence of the v2 API. Inventory existing imports, template bindings, models and state owners. Keep the migration scoped to the application's intended release. Pin 2.0.1 for this skill's verified baseline and confirm Angular 22 peers before editing templates.

Replace CVA bindings on Neural controls with Signal Forms or the individual control's explicit model contract. Rebuild validation and reset behavior deliberately; do not simply rename ngModel to value while retaining a second state owner. See [forms](forms.md).

Resolve each legacy import against the generated [public API](api/index.md). The absence of an export is a migration blocker for that API, not permission to import an implementation file. OrganizationChart and SchedulerGantt were removed; do not generate those legacy components. Choose application-owned alternatives only after understanding the feature requirement. Neural Native is a separate product and is never a replacement API source for this skill.

Rebuild table state using the current query/selection/metadata contracts. Current table selectionChange exposes next; old planning documents and older releases can use different selection terminology. Inspect the installed 2.0.1 types and use the [compiled table example](../examples/table.ts).

Check Select modes, option accessors and nullability against the current /select and /option-api types. Do not assume a former standalone multiselect export remains. Map each use case to the present catalog after checking behavior.

Review Dialog visibility and close requests, Tabs controlled versus initial state, and event payloads independently. Remove guessed compatibility aliases instead of suppressing strict template errors. Migrate tokens and visual inputs using each current component's declared union types; not every component offers every shared tone/variant/size.

Compile after each small migration and test the real interaction: form edit/reset, table proposal acceptance, navigation, focus restoration and themes. No v1 runtime is shipped in this skill. This is a migration checklist, not an automatic codemod or a universal mapping of every historical 1.x API.

Evidence: [source removal record](https://github.com/PedroMorenoTrujillo/neural-ui-workspace/blob/b1b9822d064cf6615c3765ca57791ba2685de870/N2-D1-PHYSICAL-REMOVALS.md), plus the generated published-package contracts.
