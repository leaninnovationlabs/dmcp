# Data MCP Theme System

This document describes the comprehensive theming system implemented for the Data MCP application.

## Overview

The theme system is built on top of shadcn/ui and Tailwind CSS v4, providing a consistent design language with support for light/dark modes and custom color schemes.

## Color Palette

### Primary Colors

- **Primary**: Thick yellow (`#FEBF23` equivalent) - Used for main actions, buttons, and highlights
- **Primary Foreground**: Dark text for contrast with primary background

### Secondary Colors

- **Secondary**: Lighter yellow - Used for secondary actions and accents
- **Secondary Foreground**: Dark text for contrast with secondary background

### Additional Colors

- **Success**: Green tones for success states
- **Warning**: Orange tones for warning states
- **Info**: Blue tones for informational states
- **Destructive**: Red tones for error/destructive actions

## Typography

### Font Families

- **Primary**: Inter - Modern, clean sans-serif for UI text
- **Monospace**: Fira Code - For code blocks and technical content

### Font Weights

- Light (300)
- Regular (400)
- Medium (500)
- Semi-bold (600)
- Bold (700)
- Extra-bold (800)
- Black (900)

## Theme Variables

All theme colors are defined as CSS custom properties in `src/index.css`:

```css
:root {
  /* Primary colors - Thick Yellow */
  --primary: oklch(0.85 0.15 85);
  --primary-foreground: oklch(0.145 0 0);

  /* Secondary colors - Lighter Yellow */
  --secondary: oklch(0.95 0.08 85);
  --secondary-foreground: oklch(0.145 0 0);

  /* Additional theme colors */
  --success: oklch(0.6 0.15 140);
  --warning: oklch(0.7 0.15 60);
  --info: oklch(0.6 0.15 240);
}
```

## Dark Mode

The theme automatically adapts to dark mode with adjusted color values:

```css
.dark {
  /* Primary colors adjusted for dark mode */
  --primary: oklch(0.75 0.15 85);
  --primary-foreground: oklch(0.145 0 0);

  /* Secondary colors adjusted for dark mode */
  --secondary: oklch(0.25 0.05 85);
  --secondary-foreground: oklch(0.985 0 0);
}
```

## Usage

### Using Theme Colors in Components

```tsx
// Using Tailwind classes
<div className="bg-primary text-primary-foreground">
  Primary colored element
</div>

<div className="bg-secondary text-secondary-foreground">
  Secondary colored element
</div>

// Using theme utilities
import { themeColors } from '@/lib/theme-utils'

<div style={{ backgroundColor: themeColors.primary.DEFAULT }}>
  Primary colored element
</div>
```

### Theme Provider

The `ThemeProvider` component manages theme state and persistence:

```tsx
import { ThemeProvider } from "@/components/theme-provider";

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="dmcp-ui-theme">
      {/* Your app content */}
    </ThemeProvider>
  );
}
```

### Theme Toggle

The `ThemeToggle` component provides a dropdown to switch between light, dark, and system themes:

```tsx
import { ThemeToggle } from "@/components/theme-toggle";

function Header() {
  return (
    <header>
      <ThemeToggle />
    </header>
  );
}
```

## Component Integration

### Updated Components

The following components have been updated to use the theme system:

- **HomeModule**: All hardcoded colors replaced with theme variables
- **Sidebar**: Uses sidebar-specific theme colors
- **Navigation**: Uses background and foreground theme colors
- **Button**: Inherits theme colors from shadcn/ui
- **Card**: Uses card theme colors
- **Badge**: Uses secondary theme colors

### Theme Classes

Common theme classes used throughout the application:

- `bg-primary` / `text-primary-foreground` - Primary color scheme
- `bg-secondary` / `text-secondary-foreground` - Secondary color scheme
- `bg-muted` / `text-muted-foreground` - Muted color scheme
- `bg-background` / `text-foreground` - Base background and text
- `bg-card` / `text-card-foreground` - Card backgrounds
- `border-border` - Consistent border colors

## Customization

### Adding New Colors

To add new theme colors:

1. Add CSS custom properties to `:root` and `.dark` in `src/index.css`
2. Add the color to the `@theme inline` section
3. Update `src/lib/theme-utils.ts` if needed

### Modifying Existing Colors

To modify existing colors, update the CSS custom properties in `src/index.css`. The OKLCH color space is used for better color manipulation and consistency.

## Best Practices

1. **Always use theme variables** instead of hardcoded colors
2. **Test in both light and dark modes** when making changes
3. **Use semantic color names** (primary, secondary) rather than descriptive names (yellow, blue)
4. **Maintain contrast ratios** for accessibility
5. **Use the theme utilities** for programmatic color access

## Accessibility

The theme system includes:

- High contrast ratios for text readability
- Consistent focus indicators using `--ring` colors
- Support for system preference detection
- Semantic color usage for better screen reader support

## Performance

- Fonts are preloaded for better performance
- CSS custom properties are efficient and cached
- Theme switching is instant with CSS variables
- No JavaScript required for basic theme functionality
