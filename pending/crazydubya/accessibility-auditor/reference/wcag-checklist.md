# WCAG 2.1 Level AA Compliance Checklist

## Principle 1: Perceivable

### 1.1 Text Alternatives
- [ ] 1.1.1 Non-text Content (A): All images have alt text

### 1.2 Time-based Media
- [ ] 1.2.1 Audio-only and Video-only (A): Alternatives provided
- [ ] 1.2.2 Captions (A): Captions for videos
- [ ] 1.2.3 Audio Description or Media Alternative (A)
- [ ] 1.2.4 Captions (Live) (AA): Live captions
- [ ] 1.2.5 Audio Description (AA): Pre-recorded video

### 1.3 Adaptable
- [ ] 1.3.1 Info and Relationships (A): Semantic markup
- [ ] 1.3.2 Meaningful Sequence (A): Logical reading order
- [ ] 1.3.3 Sensory Characteristics (A): Not color/shape only
- [ ] 1.3.4 Orientation (AA): No orientation lock
- [ ] 1.3.5 Identify Input Purpose (AA): Autocomplete attributes

### 1.4 Distinguishable
- [ ] 1.4.1 Use of Color (A): Not sole indicator
- [ ] 1.4.2 Audio Control (A): Pause/stop audio
- [ ] 1.4.3 Contrast (Minimum) (AA): 4.5:1 ratio
- [ ] 1.4.4 Resize text (AA): 200% zoom without loss
- [ ] 1.4.5 Images of Text (AA): Use real text
- [ ] 1.4.10 Reflow (AA): No horizontal scrolling at 320px
- [ ] 1.4.11 Non-text Contrast (AA): UI components 3:1
- [ ] 1.4.12 Text Spacing (AA): Adjustable spacing
- [ ] 1.4.13 Content on Hover or Focus (AA): Dismissible

## Principle 2: Operable

### 2.1 Keyboard Accessible
- [ ] 2.1.1 Keyboard (A): All functionality keyboard accessible
- [ ] 2.1.2 No Keyboard Trap (A): Can navigate away
- [ ] 2.1.4 Character Key Shortcuts (A): Remappable

### 2.2 Enough Time
- [ ] 2.2.1 Timing Adjustable (A): Extend/turn off time limits
- [ ] 2.2.2 Pause, Stop, Hide (A): Control moving content

### 2.3 Seizures
- [ ] 2.3.1 Three Flashes or Below Threshold (A)

### 2.4 Navigable
- [ ] 2.4.1 Bypass Blocks (A): Skip navigation
- [ ] 2.4.2 Page Titled (A): Descriptive page titles
- [ ] 2.4.3 Focus Order (A): Logical tab order
- [ ] 2.4.4 Link Purpose (A): Link text is descriptive
- [ ] 2.4.5 Multiple Ways (AA): Multiple nav methods
- [ ] 2.4.6 Headings and Labels (AA): Descriptive
- [ ] 2.4.7 Focus Visible (AA): Visible focus indicator

### 2.5 Input Modalities
- [ ] 2.5.1 Pointer Gestures (A): No complex gestures only
- [ ] 2.5.2 Pointer Cancellation (A): Can abort/undo
- [ ] 2.5.3 Label in Name (A): Accessible name includes visible text
- [ ] 2.5.4 Motion Actuation (A): Disable motion triggers

## Principle 3: Understandable

### 3.1 Readable
- [ ] 3.1.1 Language of Page (A): `<html lang="en">`
- [ ] 3.1.2 Language of Parts (AA): lang attribute for changes

### 3.2 Predictable
- [ ] 3.2.1 On Focus (A): No context change on focus
- [ ] 3.2.2 On Input (A): No unexpected changes
- [ ] 3.2.3 Consistent Navigation (AA): Same order
- [ ] 3.2.4 Consistent Identification (AA): Same function = same label

### 3.3 Input Assistance
- [ ] 3.3.1 Error Identification (A): Errors identified
- [ ] 3.3.2 Labels or Instructions (A): Labels provided
- [ ] 3.3.3 Error Suggestion (AA): Correction suggested
- [ ] 3.3.4 Error Prevention (AA): Confirm/undo for legal/financial

## Principle 4: Robust

### 4.1 Compatible
- [ ] 4.1.1 Parsing (A): Valid HTML
- [ ] 4.1.2 Name, Role, Value (A): For custom widgets
- [ ] 4.1.3 Status Messages (AA): Announced to screen readers

## Testing Tools

- **Automated**: Lighthouse, axe, WAVE
- **Manual**: Keyboard navigation, screen reader
- **Color**: Contrast checker
- **Screen Readers**: NVDA (Windows), JAWS (Windows), VoiceOver (Mac/iOS)

## Common Failures

- Missing alt text
- Insufficient contrast
- No keyboard access
- Empty links/buttons
- Form inputs without labels
- Heading hierarchy skipped
- No focus indicators
- Using color alone
