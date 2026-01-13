---
name: ui-design-system
description: The Design System, Theme, and UX rules for the Physical AI Hub.
---

# UI Design System & Theme

## Core Philosophy
- **Aesthetic**: Premium, Modern, "Physical AI" (Dark, Sleek, Futuristic).
- **Feel**: Smooth, Responsive, High-End.

## Typography
- **Font**: **Poppins** (Geometric Sans-Serif).
- **Weights**: 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold).
- **Usage**: Clean, legible, widely spaced.

## Color Palette (Dark Mode - Primary)
- **Background**: `linear-gradient(135deg, #1a1f28 0%, #161b23 50%, #0f1419 100%)`
- **Primary Accent**: `#2d7d6c` (Teal/Greenish) used in buttons and highlights.
- **Text**: `#ededed` (Off-white for readability).
- **Borders**: Subtle, often `rgba(255, 255, 255, 0.1)`.

## Components
- **Buttons**: Rounded corners, smooth hover transitions, subtle shadows.
- **Cards**: Glassmorphism effect (blur + transparency), rounded corners (`12px` or `16px`).
- **Inputs**: Rounded (`24px`), borderless or subtle border, focus rings.
- **Dropdowns**: Floating, animated slide-in, shadow depth.

## Animations
- **Transitions**: `all 0.2s ease` or `cubic-bezier` for premium feel.
- **Keyframes**: `fadeIn`, `slideIn`, `dropdownSlideIn`.

## CSS Structure
- **Global**: `app/globals.css` (Tailwind + Variables).
- **Docusaurus**: `textbook/src/css/custom.css` (Overrides).
- **Modules**: `styles.module.css` for complex components (like Chatbot, Dropdown).
