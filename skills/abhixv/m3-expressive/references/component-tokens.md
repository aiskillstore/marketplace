# Component token geometry

Every dp/sp measurement, shape assignment, and elevation level for M3 components, from the
**generated `androidx.compose.material3.tokens` files** (the `md.comp.*` token set expressed in
Kotlin). Use this when `components/*.md` records a measurement as a gap — m3.material.io publishes
many of these only inside images, so this is the machine-readable source for them.

**Provenance matters.** These are the *Compose* token values. They are authoritative for
implementation and match the guidelines where the guidelines state a number, but a value here is
not the same as a value quoted on m3.material.io. When it matters, say "per the Compose M3 tokens"
rather than "per the M3 guidelines". Each group carries the generator VERSION stamp it came from —
different components are generated from different token versions, which is normal.

Shape values are scale steps, not numbers. Resolve them with the corner radius scale in
`tokens.md`: CornerNone 0 · ExtraSmall 4 · Small 8 · Medium 12 · Large 16 · LargeIncreased 20 ·
ExtraLarge 28 · ExtraLargeIncreased 32 · ExtraExtraLarge 48 · Full = fully rounded.
Elevation levels resolve as: Level0 0dp · Level1 1dp · Level2 3dp · Level3 6dp · Level4 8dp ·
Level5 12dp.

Refresh with: `node scripts/refresh-component-tokens.js`

---

## Buttons

Design guidance for these lives in `components/buttons.md`.

### BaselineButton  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerHeight` | 40.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerMedium |
| `DisabledContainerElevation` | elevation Level0 |
| `DisabledContainerOpacity` | 0.1f |
| `DisabledIconOpacity` | 0.38f |
| `DisabledLabelTextOpacity` | 0.38f |
| `FocusedContainerElevation` | elevation Level0 |
| `HoveredContainerElevation` | elevation Level1 |
| `IconLabelSpace` | 8.0.dp |
| `IconSize` | 20.0.dp |
| `LeadingSpace` | 24.0.dp |
| `PressedContainerElevation` | elevation Level0 |
| `PressedContainerShape` | shape CornerSmall |
| `SelectedContainerShapeRound` | shape CornerFull |
| `SelectedContainerShapeSquare` | shape CornerMedium |
| `TrailingSpace` | 24.0.dp |

### ButtonXSmall  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 32.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerMedium |
| `IconLabelSpace` | 8.0.dp |
| `IconSize` | 20.0.dp |
| `LeadingSpace` | 16.0.dp |
| `OutlinedOutlineWidth` | 1.0.dp |
| `PressedContainerShape` | shape CornerSmall |
| `SelectedContainerShapeRound` | shape CornerFull |
| `SelectedContainerShapeSquare` | shape CornerMedium |
| `TrailingSpace` | 16.0.dp |

### ButtonSmall  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 40.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerMedium |
| `IconLabelSpace` | 8.0.dp |
| `IconSize` | 20.0.dp |
| `LeadingSpace` | 16.0.dp |
| `OutlinedOutlineWidth` | 1.0.dp |
| `PressedContainerShape` | shape CornerSmall |
| `SelectedContainerShapeRound` | shape CornerFull |
| `SelectedContainerShapeSquare` | shape CornerMedium |
| `TrailingSpace` | 16.0.dp |

### ButtonMedium  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 56.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerLarge |
| `IconLabelSpace` | 8.0.dp |
| `IconSize` | 24.0.dp |
| `LeadingSpace` | 24.0.dp |
| `OutlinedOutlineWidth` | 1.0.dp |
| `PressedContainerShape` | shape CornerMedium |
| `SelectedContainerShapeRound` | shape CornerFull |
| `SelectedContainerShapeSquare` | shape CornerLarge |
| `TrailingSpace` | 24.0.dp |

### ButtonLarge  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 96.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerExtraLarge |
| `IconLabelSpace` | 12.0.dp |
| `IconSize` | 32.0.dp |
| `LeadingSpace` | 48.0.dp |
| `OutlinedOutlineWidth` | 2.0.dp |
| `PressedContainerShape` | shape CornerLarge |
| `SelectedContainerShapeRound` | shape CornerFull |
| `SelectedContainerShapeSquare` | shape CornerExtraLarge |
| `TrailingSpace` | 48.0.dp |

### ButtonXLarge  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 136.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerExtraLarge |
| `IconLabelSpace` | 16.0.dp |
| `IconSize` | 40.0.dp |
| `LeadingSpace` | 64.0.dp |
| `OutlinedOutlineWidth` | 3.0.dp |
| `PressedContainerShape` | shape CornerLarge |
| `SelectedContainerShapeRound` | shape CornerFull |
| `SelectedContainerShapeSquare` | shape CornerExtraLarge |
| `TrailingSpace` | 64.0.dp |

### FilledButton  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `DisabledContainerElevation` | elevation Level0 |
| `DisabledContainerOpacity` | 0.1f |
| `DisabledIconOpacity` | 0.38f |
| `DisabledLabelTextOpacity` | 0.38f |
| `FocusedContainerElevation` | elevation Level0 |
| `HoveredContainerElevation` | elevation Level1 |
| `PressedContainerElevation` | elevation Level0 |

### FilledTonalButton  *(VERSION v0_103)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerHeight` | 40.0.dp |
| `ContainerShape` | shape CornerFull |
| `DisabledContainerElevation` | elevation Level0 |
| `DisabledContainerOpacity` | 0.12f |
| `DisabledLabelTextOpacity` | 0.38f |
| `FocusContainerElevation` | elevation Level0 |
| `HoverContainerElevation` | elevation Level1 |
| `PressedContainerElevation` | elevation Level0 |
| `DisabledIconOpacity` | 0.38f |
| `IconSize` | 18.0.dp |

### TonalButton  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `DisabledContainerElevation` | elevation Level0 |
| `DisabledContainerOpacity` | 0.1f |
| `DisabledIconOpacity` | 0.38f |
| `DisabledLabelTextOpacity` | 0.38f |
| `FocusedContainerElevation` | elevation Level0 |
| `HoveredContainerElevation` | elevation Level1 |
| `PressedContainerElevation` | elevation Level0 |

### ElevatedButton  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level1 |
| `DisabledContainerElevation` | elevation Level0 |
| `DisabledContainerOpacity` | 0.1f |
| `DisabledIconOpacity` | 0.38f |
| `DisabledLabelTextOpacity` | 0.38f |
| `FocusedContainerElevation` | elevation Level1 |
| `HoveredContainerElevation` | elevation Level2 |
| `PressedContainerElevation` | elevation Level1 |

### OutlinedButton  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `DisabledContainerOpacity` | 0.1f |
| `DisabledIconOpacity` | 0.38f |
| `DisabledLabelTextOpacity` | 0.38f |

### TextButton  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `DisabledContainerOpacity` | 0.1f |
| `DisabledIconOpacity` | 0.38f |
| `DisabledLabelOpacity` | 0.38f |

### ButtonGroupSmall  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `BetweenSpace` | 12.0.dp |
| `ContainerHeight` | 40.0.dp |

### ConnectedButtonGroupSmall  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `BetweenSpace` | 2.0.dp |
| `ContainerHeight` | 40.0.dp |
| `ContainerShape` | shape CornerFull |
| `SelectedInnerCornerCornerSizePercent` | 50.0f |

### SplitButtonXSmall  *(VERSION 18_0_18)*

| Token | Value |
|---|---|
| `BetweenSpace` | 2.0.dp |
| `ContainerHeight` | 32.0.dp |
| `ContainerShape` | shape CornerFull |
| `LeadingButtonLeadingSpace` | 12.0.dp |
| `LeadingButtonTrailingSpace` | 10.0.dp |
| `OuterCornerCornerSizePercent` | 50.0f |
| `TrailingIconSize` | 22.0.dp |
| `TrailingInnerSelectedCornerCornerSizePercent` | 50.0f |
| `TrailingButtonLeadingSpace` | 13.0.dp |
| `TrailingButtonTrailingSpace` | 13.0.dp |

### SplitButtonSmall  *(VERSION 18_0_18)*

| Token | Value |
|---|---|
| `BetweenSpace` | 2.0.dp |
| `ContainerHeight` | 40.0.dp |
| `ContainerShape` | shape CornerFull |
| `LeadingButtonLeadingSpace` | 16.0.dp |
| `LeadingButtonTrailingSpace` | 12.0.dp |
| `TrailingIconSize` | 22.0.dp |
| `TrailingInnerSelectedCornerCornerSizePercent` | 50.0f |
| `TrailingButtonLeadingSpace` | 13.0.dp |
| `TrailingButtonTrailingSpace` | 13.0.dp |

### SplitButtonMedium  *(VERSION 18_0_18)*

| Token | Value |
|---|---|
| `BetweenSpace` | 2.0.dp |
| `ContainerHeight` | 56.0.dp |
| `ContainerShape` | shape CornerFull |
| `LeadingButtonLeadingSpace` | 24.0.dp |
| `LeadingButtonTrailingSpace` | 24.0.dp |
| `TrailingIconSize` | 26.0.dp |
| `TrailingInnerSelectedCornerCornerSizePercent` | 50.0f |
| `TrailingButtonLeadingSpace` | 15.0.dp |
| `TrailingButtonTrailingSpace` | 15.0.dp |

### SplitButtonLarge  *(VERSION 18_0_18)*

| Token | Value |
|---|---|
| `BetweenSpace` | 2.0.dp |
| `ContainerHeight` | 96.0.dp |
| `ContainerShape` | shape CornerFull |
| `LeadingButtonLeadingSpace` | 48.0.dp |
| `LeadingButtonTrailingSpace` | 48.0.dp |
| `TrailingIconSize` | 38.0.dp |
| `TrailingInnerSelectedCornerCornerSizePercent` | 50.0f |
| `TrailingButtonLeadingSpace` | 29.0.dp |
| `TrailingButtonTrailingSpace` | 29.0.dp |

### SplitButtonXLarge  *(VERSION 18_0_18)*

| Token | Value |
|---|---|
| `BetweenSpace` | 2.0.dp |
| `ContainerHeight` | 136.0.dp |
| `ContainerShape` | shape CornerFull |
| `LeadingButtonLeadingSpace` | 64.0.dp |
| `LeadingButtonTrailingSpace` | 64.0.dp |
| `TrailingIconSize` | 50.0.dp |
| `TrailingInnerSelectedCornerCornerSizePercent` | 50.0f |
| `TrailingButtonLeadingSpace` | 43.0.dp |
| `TrailingButtonTrailingSpace` | 43.0.dp |

### IconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `DisabledOpacity` | 0.38f |

### XSmallIconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 32.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerMedium |
| `DefaultLeadingSpace` | 6.0.dp |
| `DefaultTrailingSpace` | 6.0.dp |
| `IconSize` | 20.0.dp |
| `NarrowLeadingSpace` | 4.0.dp |
| `NarrowTrailingSpace` | 4.0.dp |
| `OutlinedOutlineWidth` | 1.0.dp |
| `PressedContainerShape` | shape CornerSmall |
| `SelectedContainerShapeRound` | shape CornerMedium |
| `SelectedContainerShapeSquare` | shape CornerFull |
| `WideLeadingSpace` | 10.0.dp |
| `WideTrailingSpace` | 10.0.dp |

### SmallIconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 40.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerMedium |
| `DefaultLeadingSpace` | 8.0.dp |
| `DefaultTrailingSpace` | 8.0.dp |
| `IconSize` | 24.0.dp |
| `NarrowLeadingSpace` | 4.0.dp |
| `NarrowTrailingSpace` | 4.0.dp |
| `OutlinedOutlineWidth` | 1.0.dp |
| `PressedContainerShape` | shape CornerSmall |
| `SelectedContainerShapeRound` | shape CornerMedium |
| `SelectedContainerShapeSquare` | shape CornerFull |
| `WideLeadingSpace` | 14.0.dp |
| `WideTrailingSpace` | 14.0.dp |

### MediumIconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 56.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerLarge |
| `DefaultLeadingSpace` | 16.0.dp |
| `DefaultTrailingSpace` | 16.0.dp |
| `IconSize` | 24.0.dp |
| `NarrowLeadingSpace` | 12.0.dp |
| `NarrowTrailingSpace` | 12.0.dp |
| `OutlinedOutlineWidth` | 1.0.dp |
| `PressedContainerShape` | shape CornerMedium |
| `SelectedContainerShapeRound` | shape CornerLarge |
| `SelectedContainerShapeSquare` | shape CornerFull |
| `WideLeadingSpace` | 24.0.dp |
| `WideTrailingSpace` | 24.0.dp |

### LargeIconButton  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 96.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerExtraLarge |
| `IconSize` | 32.0.dp |
| `NarrowLeadingSpace` | 16.0.dp |
| `NarrowTrailingSpace` | 16.0.dp |
| `OutlinedOutlineWidth` | 2.0.dp |
| `PressedContainerShape` | shape CornerLarge |
| `SelectedContainerShapeRound` | shape CornerExtraLarge |
| `SelectedContainerShapeSquare` | shape CornerFull |
| `UniformLeadingSpace` | 32.0.dp |
| `UniformTrailingSpace` | 32.0.dp |
| `WideLeadingSpace` | 48.0.dp |
| `WideTrailingSpace` | 48.0.dp |

### XLargeIconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 136.0.dp |
| `ContainerShapeRound` | shape CornerFull |
| `ContainerShapeSquare` | shape CornerExtraLarge |
| `DefaultLeadingSpace` | 48.0.dp |
| `DefaultTrailingSpace` | 48.0.dp |
| `IconSize` | 40.0.dp |
| `NarrowLeadingSpace` | 32.0.dp |
| `NarrowTrailingSpace` | 32.0.dp |
| `OutlinedOutlineWidth` | 3.0.dp |
| `PressedContainerShape` | shape CornerLarge |
| `SelectedContainerShapeRound` | shape CornerExtraLarge |
| `SelectedContainerShapeSquare` | shape CornerFull |
| `WideLeadingSpace` | 72.0.dp |
| `WideTrailingSpace` | 72.0.dp |

### FilledIconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `DisabledContainerOpacity` | 0.1f |
| `DisabledOpacity` | 0.38f |

### FilledTonalIconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `DisabledContainerOpacity` | 0.1f |
| `DisabledOpacity` | 0.38f |

### OutlinedIconButton  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `DisabledOpacity` | 0.38f |
| `SelectedDisabledContainerOpacity` | 0.1f |

### OutlinedSegmentedButton  *(VERSION v0_162)*

| Token | Value |
|---|---|
| `ContainerHeight` | 40.0.dp |
| `DisabledIconOpacity` | 0.38f |
| `DisabledLabelTextOpacity` | 0.38f |
| `DisabledOutlineOpacity` | 0.12f |
| `OutlineWidth` | 1.0.dp |
| `Shape` | shape CornerFull |
| `IconSize` | 18.0.dp |

## FABs

Design guidance for these lives in `components/fabs.md`.

### FabBaseline  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 56.0.dp |
| `ContainerShape` | shape CornerLarge |
| `ContainerWidth` | 56.0.dp |
| `IconSize` | 24.0.dp |

### FabSmall  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 40.0.dp |
| `ContainerShape` | shape CornerMedium |
| `ContainerWidth` | 40.0.dp |
| `IconSize` | 24.0.dp |

### FabMedium  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 80.0.dp |
| `ContainerWidth` | 80.0.dp |
| `IconSize` | 28.0.dp |

### FabLarge  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 96.0.dp |
| `ContainerShape` | shape CornerExtraLarge |
| `ContainerWidth` | 96.0.dp |
| `IconSize` | 32.0.dp |

### FabPrimaryContainer  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `FocusedContainerElevation` | elevation Level3 |
| `HoveredContainerElevation` | elevation Level4 |
| `PressedContainerElevation` | elevation Level3 |

### FabSecondaryContainer  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `FocusedContainerElevation` | elevation Level3 |
| `HoveredContainerElevation` | elevation Level4 |
| `PressedContainerElevation` | elevation Level3 |

### ExtendedFabPrimary  *(VERSION v0_103)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `ContainerHeight` | 56.0.dp |
| `ContainerShape` | shape CornerLarge |
| `FocusContainerElevation` | elevation Level3 |
| `HoverContainerElevation` | elevation Level4 |
| `IconSize` | 24.0.dp |
| `LoweredContainerElevation` | elevation Level1 |
| `LoweredFocusContainerElevation` | elevation Level1 |
| `LoweredHoverContainerElevation` | elevation Level2 |
| `LoweredPressedContainerElevation` | elevation Level1 |
| `PressedContainerElevation` | elevation Level3 |

### ExtendedFabSmall  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 56.0.dp |
| `ContainerShape` | shape CornerLarge |
| `IconLabelSpace` | 8.0.dp |
| `IconSize` | 24.0.dp |
| `LeadingSpace` | 16.0.dp |
| `TrailingSpace` | 16.0.dp |

### ExtendedFabMedium  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 80.0.dp |
| `IconLabelSpace` | 16.0.dp |
| `IconSize` | 28.0.dp |
| `LeadingSpace` | 26.0.dp |
| `TrailingSpace` | 26.0.dp |

### ExtendedFabLarge  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 96.0.dp |
| `ContainerShape` | shape CornerExtraLarge |
| `IconLabelSpace` | 20.0.dp |
| `IconSize` | 32.0.dp |
| `LeadingSpace` | 28.0.dp |
| `TrailingSpace` | 28.0.dp |

### FabMenuBaseline  *(VERSION v0_14_0)*

| Token | Value |
|---|---|
| `CloseButtonBetweenSpace` | 8.0.dp |
| `CloseButtonContainerElevation` | elevation Level3 |
| `CloseButtonContainerHeight` | 56.0.dp |
| `CloseButtonContainerShape` | shape CornerFull |
| `CloseButtonContainerWidth` | 56.0.dp |
| `CloseButtonIconSize` | 20.0.dp |
| `ListItemBetweenSpace` | 4.0.dp |
| `ListItemContainerElevation` | elevation Level3 |
| `ListItemContainerHeight` | 56.0.dp |
| `ListItemContainerShape` | shape CornerFull |
| `ListItemIconLabelSpace` | 8.0.dp |
| `ListItemIconSize` | 24.0.dp |
| `ListItemLeadingSpace` | 24.0.dp |
| `ListItemTrailingSpace` | 24.0.dp |

## Navigation

Design guidance for these lives in `components/navigation.md`.

### NavigationBar  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level2 |
| `ContainerHeight` | 64.0.dp |
| `ItemActiveIndicatorIconLabelSpace` | 4.0.dp |
| `ItemActiveIndicatorShape` | shape CornerFull |
| `ItemBetweenSpace` | 0.0.dp |
| `NavShape` | shape CornerNone |
| `TallContainerHeight` | 80.0.dp |

### NavigationBarHorizontalItem  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ActiveIndicatorHeight` | 40.0.dp |
| `ActiveIndicatorLeadingSpace` | 16.0.dp |
| `ActiveIndicatorTrailingSpace` | 16.0.dp |
| `IconSize` | 24.0.dp |

### NavigationBarVerticalItem  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ActiveIndicatorHeight` | 32.0.dp |
| `ActiveIndicatorWidth` | 56.0.dp |
| `ContainerBetweenSpace` | 6.0.dp |
| `IconSize` | 24.0.dp |

### NavigationRailCollapsed  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerShape` | shape CornerNone |
| `ContainerWidth` | 96.0.dp |
| `ItemVerticalSpace` | 4.0.dp |
| `TopSpace` | 44.0.dp |
| `NarrowContainerWidth` | 80.0.dp |

### NavigationRailExpanded  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerShape` | shape CornerNone |
| `ContainerWidthMaximum` | 360.0.dp |
| `ContainerWidthMinimum` | 220.0.dp |
| `ModalContainerElevation` | elevation Level2 |
| `ModalContainerShape` | shape CornerLarge |
| `TopSpace` | 44.0.dp |

### NavigationRailBaselineItem  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ActiveIndicatorIconLabelSpace` | 8.0.dp |
| `ActiveIndicatorLeadingSpace` | 16.0.dp |
| `ActiveIndicatorShape` | shape CornerFull |
| `ActiveIndicatorTrailingSpace` | 16.0.dp |
| `ContainerHeight` | 64.0.dp |
| `ContainerShape` | shape CornerNone |
| `ContainerVerticalSpace` | 6.0.dp |
| `HeaderSpaceMinimum` | 40.0.dp |
| `IconSize` | 24.0.dp |

### NavigationRailHorizontalItem  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ActiveIndicatorHeight` | 56.0.dp |
| `FullWidthLeadingSpace` | 16.0.dp |
| `FullWidthTrailingSpace` | 16.0.dp |
| `IconLabelSpace` | 8.0.dp |
| `LeadingSpace` | 16.0.dp |

### NavigationRailVerticalItem  *(VERSION v0_11_0)*

| Token | Value |
|---|---|
| `ActiveIndicatorHeight` | 32.0.dp |
| `ActiveIndicatorWidth` | 56.0.dp |
| `IconLabelSpace` | 4.0.dp |
| `LeadingSpace` | 16.0.dp |
| `TrailingSpace` | 16.0.dp |

### NavigationDrawer  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ActiveIndicatorHeight` | 56.0.dp |
| `ActiveIndicatorShape` | shape CornerFull |
| `ActiveIndicatorWidth` | 336.0.dp |
| `BottomContainerShape` | shape CornerLargeTop |
| `ContainerHeightPercent` | 100.0f |
| `ContainerShape` | shape CornerLargeEnd |
| `ContainerWidth` | 360.0.dp |
| `IconSize` | 24.0.dp |
| `ModalContainerElevation` | elevation Level1 |
| `StandardContainerElevation` | elevation Level0 |

### PrimaryNavigationTab  *(VERSION v0_162)*

| Token | Value |
|---|---|
| `ActiveIndicatorHeight` | 3.0.dp |
| `ActiveIndicatorShape` | RoundedCornerShape(3.0.dp) |
| `ContainerElevation` | elevation Level0 |
| `ContainerHeight` | 48.0.dp |
| `ContainerShape` | shape CornerNone |
| `IconAndLabelTextContainerHeight` | 64.0.dp |
| `IconSize` | 24.0.dp |

### SecondaryNavigationTab  *(VERSION v0_162)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerHeight` | 48.0.dp |
| `ContainerShape` | shape CornerNone |
| `DividerHeight` | 1.0.dp |
| `IconSize` | 24.0.dp |

## App bars and toolbars

Design guidance for these lives in `components/bars.md`.

### AppBar  *(VERSION 14_0_0)*

| Token | Value |
|---|---|
| `AvatarSize` | 32.0.dp |
| `ContainerElevation` | elevation Level0 |
| `ContainerShape` | shape CornerNone |
| `IconButtonSpace` | 0.0.dp |
| `IconSize` | 24.0.dp |
| `LeadingSpace` | 4.0.dp |
| `OnScrollContainerElevation` | elevation Level2 |
| `TrailingSpace` | 4.0.dp |

### AppBarSmall  *(VERSION 14_0_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 64.0.dp |

### AppBarMedium  *(VERSION 14_0_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 112.0.dp |

### AppBarMediumFlexible  *(VERSION 14_0_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 112.0.dp |
| `LargeContainerHeight` | 136.0.dp |

### AppBarLarge  *(VERSION 14_0_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 152.0.dp |

### AppBarLargeFlexible  *(VERSION 14_0_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 120.0.dp |
| `LargeContainerHeight` | 152.0.dp |

### BottomAppBar  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level2 |
| `ContainerHeight` | 80.0.dp |
| `ContainerShape` | shape CornerNone |

### DockedToolbar  *(VERSION 14_0_0)*

| Token | Value |
|---|---|
| `ContainerHeight` | 64.0.dp |
| `ContainerLeadingSpace` | 16.0.dp |
| `ContainerMaxSpacing` | 32.0.dp |
| `ContainerMinSpacing` | 4.0.dp |
| `ContainerShape` | shape CornerNone |
| `ContainerTrailingSpace` | 16.0.dp |

### FloatingToolbar  *(VERSION 12_0_0)*

| Token | Value |
|---|---|
| `ContainerBetweenSpace` | 4.0.dp |
| `ContainerExternalPadding` | 16.0.dp |
| `ContainerHeight` | 64.0.dp |
| `ContainerLeadingSpace` | 8.0.dp |
| `ContainerShape` | shape CornerFull |
| `ContainerTrailingSpace` | 8.0.dp |

## Containment

Design guidance for these lives in `components/containment.md`.

### FilledCard  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerShape` | shape CornerMedium |
| `DisabledContainerElevation` | elevation Level0 |
| `DisabledContainerOpacity` | 0.38f |
| `DraggedContainerElevation` | elevation Level3 |
| `FocusContainerElevation` | elevation Level0 |
| `HoverContainerElevation` | elevation Level1 |
| `IconSize` | 24.0.dp |
| `PressedContainerElevation` | elevation Level0 |

### ElevatedCard  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level1 |
| `ContainerShape` | shape CornerMedium |
| `DisabledContainerElevation` | elevation Level1 |
| `DisabledContainerOpacity` | 0.38f |
| `DraggedContainerElevation` | elevation Level4 |
| `FocusContainerElevation` | elevation Level1 |
| `HoverContainerElevation` | elevation Level2 |
| `IconSize` | 24.0.dp |
| `PressedContainerElevation` | elevation Level1 |

### OutlinedCard  *(VERSION v0_192)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerShape` | shape CornerMedium |
| `DisabledContainerElevation` | elevation Level0 |
| `DisabledOutlineOpacity` | 0.12f |
| `DraggedContainerElevation` | elevation Level3 |
| `FocusContainerElevation` | elevation Level0 |
| `HoverContainerElevation` | elevation Level1 |
| `IconSize` | 24.0.dp |
| `OutlineWidth` | 1.0.dp |
| `PressedContainerElevation` | elevation Level0 |

### List  *(VERSION 29.0.0)*

| Token | Value |
|---|---|
| `ContainerShape` | shape CornerLarge |
| `DividerBottomSpace` | 0.0.dp |
| `DividerLeadingSpace` | 16.0.dp |
| `DividerTopSpace` | 0.0.dp |
| `DividerTrailingSpace` | 16.0.dp |
| `ItemBetweenSpace` | 12.0.dp |
| `ItemBottomSpace` | 10.0.dp |
| `ItemContainerElevation` | elevation Level0 |
| `ItemContainerExpressiveShape` | shape CornerExtraSmall |
| `ItemContainerShape` | shape CornerNone |
| `ItemDisabledContainerExpressiveShape` | shape CornerExtraSmall |
| `ItemDisabledLabelTextOpacity` | 0.38f |
| `ItemDisabledLeadingIconOpacity` | 0.38f |
| `ItemDisabledOverlineOpacity` | 0.38f |
| `ItemDisabledStateLayerOpacity` | 0.1f |
| `ItemDisabledSupportingTextOpacity` | 0.38f |
| `ItemDisabledTrailingIconOpacity` | 0.38f |
| `ItemDraggedContainerElevation` | elevation Level4 |
| `ItemDraggedContainerExpressiveShape` | shape CornerLarge |
| `ItemFocusedContainerExpressiveShape` | shape CornerLarge |
| `ItemHoveredContainerExpressiveShape` | shape CornerMedium |
| `ItemLargeLeadingVideoHeight` | 64.0.dp |
| `ItemLargeLeadingVideoWidth` | 114.0.dp |
| `ItemLeadingAvatarShape` | shape CornerFull |
| `ItemLeadingAvatarSize` | 40.0.dp |
| `ItemLeadingIconExpressiveSize` | 20.0.dp |
| `ItemLeadingIconSize` | 24.0.dp |
| `ItemLeadingImageExpressiveShape` | shape CornerSmall |
| `ItemLeadingImageHeight` | 56.0.dp |
| `ItemLeadingImageShape` | shape CornerNone |
| `ItemLeadingImageWidth` | 56.0.dp |
| `ItemLeadingSpace` | 16.0.dp |
| `ItemLeadingVideoShape` | shape CornerSmall |
| `ItemLeadingVideoWidth` | 100.0.dp |
| `ItemOneLineContainerHeight` | 56.0.dp |
| `ItemPressedContainerExpressiveShape` | shape CornerLarge |
| `ItemSelectedContainerExpressiveShape` | shape CornerLarge |
| `ItemSelectedContainerShape` | shape CornerLarge |
| `ItemSelectedDisabledContainerExpressiveShape` | shape CornerLarge |
| `ItemSelectedDisabledContainerOpacity` | 0.38f |
| `ItemSelectedDisabledLabelTextOpacity` | 0.38f |
| `ItemSelectedDisabledLeadingIconOpacity` | 0.38f |
| `ItemSelectedDisabledOverlineOpacity` | 0.38f |
| `ItemSelectedDisabledStateLayerOpacity` | 0.1f |
| `ItemSelectedDisabledSupportingTextOpacity` | 0.38f |
| `ItemSelectedDisabledTrailingIconOpacity` | 0.38f |
| `ItemSelectedDisabledTrailingSupportingTextOpacity` | 0.38f |
| `ItemSelectedDraggedContainerExpressiveShape` | shape CornerLarge |
| `ItemSelectedFocusedContainerExpressiveShape` | shape CornerLarge |
| `ItemSelectedHoveredContainerExpressiveShape` | shape CornerLarge |
| `ItemSelectedPressedContainerExpressiveShape` | shape CornerLarge |
| `ItemSmallLeadingVideoHeight` | 56.0.dp |
| `ItemSmallLeadingVideoWidth` | 100.0.dp |
| `ItemThreeLineContainerHeight` | 88.0.dp |
| `ItemTopSpace` | 10.0.dp |
| `ItemTrailingIconExpressiveSize` | 20.0.dp |
| `ItemTrailingIconSize` | 24.0.dp |
| `ItemTrailingSpace` | 16.0.dp |
| `ItemTwoLineContainerHeight` | 72.0.dp |
| `SegmentedGap` | 2.0.dp |

### ExpandedList  *(VERSION 29.0.0)*

| Token | Value |
|---|---|
| `ContainerShape` | shape CornerLarge |
| `TrailingIconShape` | shape CornerFull |

### ReorderList  *(VERSION 29.0.0)*

| Token | Value |
|---|---|
| `ItemShape` | shape CornerLarge |

### RevealList  *(VERSION 29.0.0)*

| Token | Value |
|---|---|
| `ItemContainerShape` | shape CornerLarge |
| `ItemIconButtonActionContainerShape` | shape CornerLarge |
| `ItemIconButtonContainerShape` | shape CornerFull |
| `ItemSegmentedContainerShape` | shape CornerLarge |

### Divider  *(VERSION v0_117)*

| Token | Value |
|---|---|
| `Thickness` | 1.0.dp |

### SheetBottom  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `DockedContainerShape` | shape CornerExtraLargeTop |
| `DockedDragHandleHeight` | 4.0.dp |
| `DockedDragHandleWidth` | 32.0.dp |
| `DockedMinimizedContainerShape` | shape CornerNone |
| `DockedModalContainerElevation` | elevation Level1 |
| `DockedStandardContainerElevation` | elevation Level1 |

### DragHandle  *(VERSION 7_0_1)*

| Token | Value |
|---|---|
| `ContainerWidth` | 24.0.dp |
| `DraggedElevation` | elevation Level0 |
| `DraggedHeight` | 52.0.dp |
| `DraggedShape` | shape CornerMedium |
| `DraggedWidth` | 12.0.dp |
| `Elevation` | elevation Level0 |
| `Height` | 48.0.dp |
| `PressedElevation` | elevation Level0 |
| `PressedHeight` | 52.0.dp |
| `PressedShape` | shape CornerMedium |
| `PressedWidth` | 12.0.dp |
| `Shape` | shape CornerFull |
| `Width` | 4.0.dp |

### Dialog  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `ContainerShape` | shape CornerExtraLarge |
| `IconSize` | 24.0.dp |

## Input and selection

Design guidance for these lives in `components/input.md`.

### Checkbox  *(VERSION 14_1_0)*

| Token | Value |
|---|---|
| `ContainerShape` | RoundedCornerShape(2.0.dp) |
| `ContainerSize` | 18.0.dp |
| `IconSize` | 18.0.dp |
| `SelectedDisabledContainerOpacity` | 0.38f |
| `SelectedDisabledContainerOutlineWidth` | 0.0.dp |
| `SelectedFocusOutlineWidth` | 0.0.dp |
| `SelectedHoverOutlineWidth` | 0.0.dp |
| `SelectedOutlineWidth` | 0.0.dp |
| `SelectedPressedOutlineWidth` | 0.0.dp |
| `StateLayerShape` | shape CornerFull |
| `StateLayerSize` | 40.0.dp |
| `UnselectedDisabledContainerOpacity` | 0.38f |
| `UnselectedDisabledOutlineWidth` | 2.0.dp |
| `UnselectedFocusOutlineWidth` | 2.0.dp |
| `UnselectedHoverOutlineWidth` | 2.0.dp |
| `UnselectedOutlineWidth` | 2.0.dp |
| `UnselectedPressedOutlineWidth` | 2.0.dp |

### RadioButton  *(VERSION v0_117)*

| Token | Value |
|---|---|
| `DisabledSelectedIconOpacity` | 0.38f |
| `DisabledUnselectedIconOpacity` | 0.38f |
| `IconSize` | 20.0.dp |
| `StateLayerSize` | 40.0.dp |

### Switch  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `DisabledSelectedHandleOpacity` | 1.0f |
| `DisabledSelectedIconOpacity` | 0.38f |
| `DisabledTrackOpacity` | 0.12f |
| `DisabledUnselectedHandleOpacity` | 0.38f |
| `DisabledUnselectedIconOpacity` | 0.38f |
| `HandleShape` | shape CornerFull |
| `PressedHandleHeight` | 28.0.dp |
| `PressedHandleWidth` | 28.0.dp |
| `SelectedHandleHeight` | 24.0.dp |
| `SelectedHandleWidth` | 24.0.dp |
| `SelectedIconSize` | 16.0.dp |
| `StateLayerShape` | shape CornerFull |
| `StateLayerSize` | 40.0.dp |
| `TrackHeight` | 32.0.dp |
| `TrackOutlineWidth` | 2.0.dp |
| `TrackShape` | shape CornerFull |
| `TrackWidth` | 52.0.dp |
| `UnselectedHandleHeight` | 16.0.dp |
| `UnselectedHandleWidth` | 16.0.dp |
| `UnselectedIconSize` | 16.0.dp |
| `IconHandleHeight` | 24.0.dp |
| `IconHandleWidth` | 24.0.dp |

### Slider  *(VERSION ?)*

| Token | Value |
|---|---|
| `ActiveContainerOpacity` | 1.0f |
| `ActiveHandleHeight` | 44.0.dp |
| `ActiveHandleLeadingSpace` | 6.0.dp |
| `ActiveHandlePadding` | 6.0.dp |
| `ActiveHandleShape` | shape CornerFull |
| `ActiveHandleTrailingSpace` | 6.0.dp |
| `ActiveHandleWidth` | 4.0.dp |
| `ActiveTrackHeight` | 16.0.dp |
| `ActiveTrackShape` | shape CornerFull |
| `ActiveTrackShapeLeading` | shape CornerFull |
| `DisabledActiveTrackOpacity` | 0.38f |
| `DisabledHandleOpacity` | 0.38f |
| `DisabledHandleWidth` | 4.0.dp |
| `DisabledInactiveTrackOpacity` | 0.12f |
| `FocusHandleWidth` | 2.0.dp |
| `HandleHeight` | 44.0.dp |
| `HandleShape` | shape CornerFull |
| `HandleWidth` | 4.0.dp |
| `HoverHandleWidth` | 4.0.dp |
| `InactiveContainerOpacity` | 1.0f |
| `InactiveTrackHeight` | 16.0.dp |
| `InactiveTrackShape` | shape CornerFull |
| `PressedHandleWidth` | 2.0.dp |
| `StopIndicatorShape` | shape CornerFull |
| `StopIndicatorSize` | 4.0.dp |
| `StopIndicatorTrailingSpace` | 6.0.dp |
| `ValueIndicatorActiveBottomSpace` | 12.0.dp |

### Chips  *(VERSION 37.2.1)*

| Token | Value |
|---|---|
| `AvatarShape` | shape CornerFull |
| `AvatarSize` | 24.0.dp |
| `ContainerElevation` | elevation Level0 |
| `DraggedContainerElevation` | elevation Level4 |
| `Height` | 32.0.dp |
| `LeadingIconSize` | 18.0.dp |
| `PressedShape` | shape CornerSmall |
| `SelectedDisabledContainerOpacity` | 0.12f |
| `SelectedOutlineWidth` | 0.0.dp |
| `SelectedShape` | shape CornerFull |
| `TrailingIconSize` | 18.0.dp |
| `UnselectedDisabledOutlineOpacity` | 0.1f |
| `UnselectedOutlineWidth` | 1.0.dp |
| `UnselectedShape` | shape CornerMedium |

### AssistChip  *(VERSION 7_0_1)*

| Token | Value |
|---|---|
| `ContainerHeight` | 32.0.dp |
| `ContainerShape` | shape CornerSmall |
| `DisabledLabelTextOpacity` | 0.38f |
| `DraggedContainerElevation` | elevation Level4 |
| `ElevatedContainerElevation` | elevation Level1 |
| `ElevatedDisabledContainerElevation` | elevation Level0 |
| `ElevatedDisabledContainerOpacity` | 0.12f |
| `ElevatedFocusContainerElevation` | elevation Level1 |
| `ElevatedHoverContainerElevation` | elevation Level2 |
| `ElevatedPressedContainerElevation` | elevation Level1 |
| `FlatContainerElevation` | elevation Level0 |
| `FlatDisabledOutlineOpacity` | 0.12f |
| `FlatOutlineWidth` | 1.0.dp |
| `DisabledIconOpacity` | 0.38f |
| `IconSize` | 18.0.dp |

### FilterChip  *(VERSION 7_0_1)*

| Token | Value |
|---|---|
| `ContainerHeight` | 32.0.dp |
| `ContainerShape` | shape CornerSmall |
| `DisabledLabelTextOpacity` | 0.38f |
| `DraggedContainerElevation` | elevation Level4 |
| `ElevatedContainerElevation` | elevation Level1 |
| `ElevatedDisabledContainerElevation` | elevation Level0 |
| `ElevatedDisabledContainerOpacity` | 0.12f |
| `ElevatedFocusContainerElevation` | elevation Level1 |
| `ElevatedHoverContainerElevation` | elevation Level2 |
| `ElevatedPressedContainerElevation` | elevation Level1 |
| `FlatContainerElevation` | elevation Level0 |
| `FlatDisabledSelectedContainerOpacity` | 0.12f |
| `FlatDisabledUnselectedOutlineOpacity` | 0.12f |
| `FlatSelectedFocusContainerElevation` | elevation Level0 |
| `FlatSelectedHoverContainerElevation` | elevation Level1 |
| `FlatSelectedOutlineWidth` | 0.0.dp |
| `FlatSelectedPressedContainerElevation` | elevation Level0 |
| `FlatUnselectedFocusContainerElevation` | elevation Level0 |
| `FlatUnselectedHoverContainerElevation` | elevation Level0 |
| `FlatUnselectedOutlineWidth` | 1.0.dp |
| `FlatUnselectedPressedContainerElevation` | elevation Level0 |
| `IconSize` | 18.0.dp |
| `DisabledLeadingIconOpacity` | 0.38f |
| `DisabledTrailingIconOpacity` | 0.38f |

### InputChip  *(VERSION 7_0_1)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level0 |
| `ContainerHeight` | 32.0.dp |
| `ContainerShape` | shape CornerSmall |
| `DisabledLabelTextOpacity` | 0.38f |
| `DisabledSelectedContainerOpacity` | 0.12f |
| `DisabledUnselectedOutlineOpacity` | 0.12f |
| `DraggedContainerElevation` | elevation Level4 |
| `SelectedOutlineWidth` | 0.0.dp |
| `UnselectedOutlineWidth` | 1.0.dp |
| `AvatarShape` | shape CornerFull |
| `AvatarSize` | 24.0.dp |
| `DisabledAvatarOpacity` | 0.38f |
| `DisabledLeadingIconOpacity` | 0.38f |
| `LeadingIconSize` | 18.0.dp |
| `DisabledTrailingIconOpacity` | 0.38f |
| `TrailingIconSize` | 18.0.dp |

### SuggestionChip  *(VERSION 7_0_1)*

| Token | Value |
|---|---|
| `ContainerHeight` | 32.0.dp |
| `ContainerShape` | shape CornerSmall |
| `DisabledLabelTextOpacity` | 0.38f |
| `DraggedContainerElevation` | elevation Level4 |
| `ElevatedContainerElevation` | elevation Level1 |
| `ElevatedDisabledContainerElevation` | elevation Level0 |
| `ElevatedDisabledContainerOpacity` | 0.12f |
| `ElevatedFocusContainerElevation` | elevation Level1 |
| `ElevatedHoverContainerElevation` | elevation Level2 |
| `ElevatedPressedContainerElevation` | elevation Level1 |
| `FlatContainerElevation` | elevation Level0 |
| `FlatDisabledOutlineOpacity` | 0.12f |
| `FlatOutlineWidth` | 1.0.dp |
| `DisabledLeadingIconOpacity` | 0.38f |
| `LeadingIconSize` | 18.0.dp |

### FilledTextField  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ActiveIndicatorHeight` | 1.0.dp |
| `ContainerShape` | shape CornerExtraSmallTop |
| `DisabledActiveIndicatorHeight` | 1.0.dp |
| `DisabledActiveIndicatorOpacity` | 0.38f |
| `DisabledContainerOpacity` | 0.04f |
| `DisabledInputOpacity` | 0.38f |
| `DisabledLabelOpacity` | 0.38f |
| `DisabledLeadingIconOpacity` | 0.38f |
| `DisabledSupportingOpacity` | 0.38f |
| `DisabledTrailingIconOpacity` | 0.38f |
| `FocusActiveIndicatorHeight` | 2.0.dp |
| `HoverActiveIndicatorHeight` | 1.0.dp |
| `LeadingIconSize` | 24.0.dp |
| `TrailingIconSize` | 24.0.dp |

### OutlinedTextField  *(VERSION v0_103)*

| Token | Value |
|---|---|
| `ContainerHeight` | 56.0.dp |
| `ContainerShape` | shape CornerExtraSmall |
| `DisabledInputOpacity` | 0.38f |
| `DisabledLabelOpacity` | 0.38f |
| `DisabledLeadingIconOpacity` | 0.38f |
| `DisabledOutlineOpacity` | 0.12f |
| `DisabledOutlineWidth` | 1.0.dp |
| `DisabledSupportingOpacity` | 0.38f |
| `DisabledTrailingIconOpacity` | 0.38f |
| `FocusOutlineWidth` | 2.0.dp |
| `HoverOutlineWidth` | 1.0.dp |
| `LeadingIconSize` | 24.0.dp |
| `OutlineWidth` | 1.0.dp |
| `TrailingIconSize` | 24.0.dp |

### FilledAutocomplete  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `MenuContainerElevation` | elevation Level2 |
| `MenuContainerShape` | shape CornerExtraSmall |
| `TextFieldActiveIndicatorHeight` | 1.0.dp |
| `TextFieldContainerShape` | shape CornerExtraSmallTop |
| `TextFieldDisabledActiveIndicatorHeight` | 1.0.dp |
| `TextFieldDisabledActiveIndicatorOpacity` | 0.38f |
| `TextFieldDisabledContainerOpacity` | 0.04f |
| `FieldDisabledInputTextOpacity` | 0.38f |
| `FieldDisabledLabelTextOpacity` | 0.38f |
| `TextFieldDisabledLeadingIconOpacity` | 0.38f |
| `FieldDisabledSupportingTextOpacity` | 0.38f |
| `TextFieldDisabledTrailingIconOpacity` | 0.38f |
| `TextFieldFocusActiveIndicatorHeight` | 2.0.dp |
| `TextFieldHoverActiveIndicatorHeight` | 1.0.dp |
| `TextFieldLeadingIconSize` | 20.0.dp |
| `TextFieldTrailingIconSize` | 24.0.dp |

### OutlinedAutocomplete  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `MenuContainerElevation` | elevation Level2 |
| `MenuContainerShape` | shape CornerExtraSmall |
| `TextFieldContainerShape` | shape CornerExtraSmall |
| `FieldDisabledInputTextOpacity` | 0.38f |
| `FieldDisabledLabelTextOpacity` | 0.38f |
| `TextFieldDisabledLeadingIconOpacity` | 0.38f |
| `TextFieldDisabledOutlineOpacity` | 0.12f |
| `TextFieldDisabledOutlineWidth` | 1.0.dp |
| `FieldDisabledSupportingTextOpacity` | 0.38f |
| `TextFieldDisabledTrailingIconOpacity` | 0.38f |
| `TextFieldFocusOutlineWidth` | 2.0.dp |
| `TextFieldHoverOutlineWidth` | 1.0.dp |
| `TextFieldLeadingIconSize` | 24.0.dp |
| `TextFieldOutlineWidth` | 1.0.dp |
| `TextFieldTrailingIconSize` | 24.0.dp |

### SearchBar  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `AvatarShape` | shape CornerFull |
| `AvatarSize` | 30.0.dp |
| `ContainerElevation` | elevation Level3 |
| `ContainerHeight` | 56.0.dp |
| `ContainerShape` | shape CornerFull |

### SearchView  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `DockedContainerShape` | shape CornerExtraLarge |
| `DockedHeaderContainerHeight` | 56.0.dp |
| `FullScreenContainerShape` | shape CornerNone |
| `FullScreenHeaderContainerHeight` | 72.0.dp |

## Feedback and overlays

Design guidance for these lives in `components/feedback.md`.

### Badge  *(VERSION v0_103)*

| Token | Value |
|---|---|
| `LargeShape` | shape CornerFull |
| `LargeSize` | 16.0.dp |
| `Shape` | shape CornerFull |
| `Size` | 6.0.dp |

### ProgressIndicator  *(VERSION v0_4_0)*

| Token | Value |
|---|---|
| `ActiveShape` | shape CornerFull |
| `StopShape` | shape CornerFull |
| `TrackShape` | shape CornerFull |

### LinearProgressIndicator  *(VERSION v0_7_0)*

| Token | Value |
|---|---|
| `ActiveThickness` | 4.0.dp |
| `ActiveWaveAmplitude` | 3.0.dp |
| `ActiveWaveWavelength` | 40.0.dp |
| `Height` | 4.0.dp |
| `IndeterminateActiveWaveWavelength` | 20.0.dp |
| `StopSize` | 4.0.dp |
| `StopTrailingSpace` | 0.0.dp |
| `TrackActiveSpace` | 4.0.dp |
| `TrackThickness` | 4.0.dp |
| `WaveHeight` | 10.0.dp |

### CircularProgressIndicator  *(VERSION v0_7_0)*

| Token | Value |
|---|---|
| `ActiveThickness` | 4.0.dp |
| `ActiveWaveAmplitude` | 1.6.dp |
| `ActiveWaveWavelength` | 15.0.dp |
| `Size` | 40.0.dp |
| `TrackActiveSpace` | 4.0.dp |
| `TrackThickness` | 4.0.dp |
| `WaveSize` | 48.0.dp |

### LoadingIndicator  *(VERSION v0_7_0)*

| Token | Value |
|---|---|
| `ActiveSize` | 38.0.dp |
| `ContainerHeight` | 48.0.dp |
| `ContainerShape` | shape CornerFull |
| `ContainerWidth` | 48.0.dp |

### Snackbar  *(VERSION v0_103)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `ContainerShape` | shape CornerExtraSmall |
| `IconSize` | 24.0.dp |
| `SingleLineContainerHeight` | 48.0.dp |
| `TwoLinesContainerHeight` | 68.0.dp |

### PlainTooltip  *(VERSION ?)*

| Token | Value |
|---|---|
| `ContainerShape` | shape CornerExtraSmall |

### RichTooltip  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level2 |
| `ContainerShape` | shape CornerMedium |

### Menu  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level2 |
| `ContainerShape` | shape CornerExtraSmall |

### StandardMenu  *(VERSION 24.1.2)*

| Token | Value |
|---|---|
| `ItemDisabledLabelTextOpacity` | 0.38f |
| `ItemDisabledLeadingIconOpacity` | 0.38f |
| `ItemDisabledSupportingTextOpacity` | 0.38f |
| `ItemDisabledTrailingIconOpacity` | 0.38f |
| `ItemDisabledTrailingSupportingTextOpacity` | 0.38f |
| `ItemSelectedDisabledContainerOpacity` | 0.38f |
| `ItemSelectedDisabledLabelTextOpacity` | 0.38f |
| `ItemSelectedDisabledLeadingIconOpacity` | 0.38f |
| `ItemSelectedDisabledTrailingIconOpacity` | 0.38f |

### VibrantMenu  *(VERSION 24.1.2)*

| Token | Value |
|---|---|
| `ItemDisabledLabelTextOpacity` | 0.38f |
| `ItemDisabledLeadingIconOpacity` | 0.38f |
| `ItemDisabledSupportingTextOpacity` | 0.38f |
| `ItemDisabledTrailingIconOpacity` | 0.38f |
| `ItemDisabledTrailingSupportingTextOpacity` | 0.38f |
| `ItemSelectedDisabledLabelTextOpacity` | 0.38f |
| `ItemSelectedDisabledLeadingIconOpacity` | 0.38f |
| `ItemSelectedDisabledSupportingTextOpacity` | 0.38f |
| `ItemSelectedDisabledTrailingIconOpacity` | 0.38f |
| `ItemSelectedDisabledTrailingSupportingTextOpacity` | 0.38f |

### SegmentedMenu  *(VERSION 24.1.2)*

| Token | Value |
|---|---|
| `ActiveContainerShape` | 24.0.dp |
| `ContainerElevation` | elevation Level2 |
| `ContainerShape` | shape CornerLarge |
| `GroupPadding` | 4.0.dp |
| `GroupShape` | shape CornerSmall |
| `HorizontalContainerBottomSpace` | 8.0.dp |
| `HorizontalContainerTopSpace` | 8.0.dp |
| `HorizontalIconOnlyItemBottomSpace` | 16.0.dp |
| `HorizontalIconOnlyItemLeadingSpace` | 16.0.dp |
| `HorizontalIconOnlyItemSelectedShape` | shape CornerFull |
| `HorizontalIconOnlyItemTopSpace` | 16.0.dp |
| `HorizontalIconOnlyItemTrailingSpace` | 16.0.dp |
| `HorizontalIconOnlySegmentedGap` | 4.0.dp |
| `HorizontalItemBetweenSpace` | 12.0.dp |
| `HorizontalItemBottomSpace` | 6.0.dp |
| `HorizontalItemFocusedShape` | shape CornerMedium |
| `HorizontalItemHoveredShape` | shape CornerMedium |
| `HorizontalItemLeadingSpace` | 12.0.dp |
| `HorizontalItemPressedShape` | shape CornerMedium |
| `HorizontalItemSelectedFocusedShape` | shape CornerFull |
| `HorizontalItemSelectedHoveredShape` | shape CornerFull |
| `HorizontalItemSelectedPressedShape` | shape CornerFull |
| `HorizontalItemTopSpace` | 6.0.dp |
| `HorizontalItemTrailingSpace` | 12.0.dp |
| `HorizontalSegmentedGap` | 2.0.dp |
| `InactiveContainerShape` | shape CornerSmall |
| `Item` | 44.0.dp |
| `ItemBetweenSpace` | 12.0.dp |
| `ItemBottomSpace` | 8.0.dp |
| `ItemFirstChildInnerCornerCornerSize` | shape CornerExtraSmall |
| `ItemFirstChildShape` | shape CornerMedium |
| `ItemLastChildInnerCornerCornerSize` | shape CornerExtraSmall |
| `ItemLastChildShape` | shape CornerMedium |
| `ItemLeadingIconSize` | 20.0.dp |
| `ItemLeadingSpace` | 16.0.dp |
| `ItemSelectedShape` | shape CornerMedium |
| `ItemShape` | shape CornerExtraSmall |
| `ItemTopSpace` | 8.0.dp |
| `ItemTrailingIconSize` | 20.0.dp |
| `ItemTrailingSpace` | 16.0.dp |
| `SegmentedGap` | 2.0.dp |

### DatePickerModal  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `ContainerHeight` | 568.0.dp |
| `ContainerShape` | shape CornerExtraLarge |
| `ContainerWidth` | 360.0.dp |
| `DateContainerHeight` | 40.0.dp |
| `DateContainerShape` | shape CornerFull |
| `DateContainerWidth` | 40.0.dp |
| `DateStateLayerHeight` | 40.0.dp |
| `DateStateLayerShape` | shape CornerFull |
| `DateStateLayerWidth` | 40.0.dp |
| `DateTodayContainerOutlineWidth` | 1.0.dp |
| `HeaderContainerHeight` | 120.0.dp |
| `HeaderContainerWidth` | 360.0.dp |
| `RangeSelectionActiveIndicatorContainerHeight` | 40.0.dp |
| `RangeSelectionActiveIndicatorContainerShape` | shape CornerFull |
| `RangeSelectionContainerElevation` | elevation Level0 |
| `RangeSelectionContainerShape` | shape CornerNone |
| `RangeSelectionHeaderContainerHeight` | 128.0.dp |
| `SelectionYearContainerHeight` | 36.0.dp |
| `SelectionYearContainerWidth` | 72.0.dp |
| `SelectionYearStateLayerHeight` | 36.0.dp |
| `SelectionYearStateLayerShape` | shape CornerFull |
| `SelectionYearStateLayerWidth` | 72.0.dp |

### DateInputModal  *(VERSION v0_161)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `ContainerHeight` | 512.0.dp |
| `ContainerShape` | shape CornerExtraLarge |
| `ContainerWidth` | 328.0.dp |
| `HeaderContainerHeight` | 120.0.dp |
| `HeaderContainerWidth` | 328.0.dp |

### TimePicker  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ClockDialContainerSize` | 256.0.dp |
| `ClockDialSelectorCenterContainerShape` | shape CornerFull |
| `ClockDialSelectorCenterContainerSize` | 8.0.dp |
| `ClockDialSelectorHandleContainerShape` | shape CornerFull |
| `ClockDialSelectorHandleContainerSize` | 48.0.dp |
| `ClockDialSelectorTrackContainerWidth` | 2.0.dp |
| `ClockDialShape` | shape CornerFull |
| `ContainerElevation` | elevation Level3 |
| `ContainerShape` | shape CornerExtraLarge |
| `PeriodSelectorContainerShape` | shape CornerSmall |
| `PeriodSelectorHorizontalContainerHeight` | 38.0.dp |
| `PeriodSelectorHorizontalContainerWidth` | 216.0.dp |
| `PeriodSelectorOutlineWidth` | 1.0.dp |
| `PeriodSelectorVerticalContainerHeight` | 80.0.dp |
| `PeriodSelectorVerticalContainerWidth` | 52.0.dp |
| `TimeSelector24HVerticalContainerWidth` | 114.0.dp |
| `TimeSelectorContainerHeight` | 80.0.dp |
| `TimeSelectorContainerShape` | shape CornerSmall |
| `TimeSelectorContainerWidth` | 96.0.dp |

### TimeInput  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `ContainerElevation` | elevation Level3 |
| `ContainerShape` | shape CornerExtraLarge |
| `PeriodSelectorContainerHeight` | 72.0.dp |
| `PeriodSelectorContainerShape` | shape CornerSmall |
| `PeriodSelectorContainerWidth` | 52.0.dp |
| `PeriodSelectorOutlineWidth` | 1.0.dp |
| `TimeFieldContainerHeight` | 72.0.dp |
| `TimeFieldContainerShape` | shape CornerSmall |
| `TimeFieldContainerWidth` | 96.0.dp |
| `TimeFieldFocusOutlineWidth` | 2.0.dp |

## Interaction states

Design guidance for these lives in `interaction.md`.

### State  *(VERSION v0_210)*

| Token | Value |
|---|---|
| `DraggedStateLayerOpacity` | 0.16f |
| `FocusStateLayerOpacity` | 0.1f |
| `HoverStateLayerOpacity` | 0.08f |
| `PressedStateLayerOpacity` | 0.1f |

### Scrim  *(VERSION v0_117)*

| Token | Value |
|---|---|
| `ContainerOpacity` | 0.32f |
