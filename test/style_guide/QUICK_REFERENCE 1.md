# Style Guide - Quick Reference

## Color Palette

### Primary Blues
| Color | Hex | Usage |
|-------|-----|-------|
| Primary Dark | `#003580` | Headers, main elements, primary text |
| Primary Main | `#004B87` | Links, buttons, interactive elements |
| Primary Light | `#0066CC` | Hover states, focus indicators |

### Accent Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Gold | `#D4AF37` | Premium features, highlights |
| Warm Gold | `#F5A623` | Gold hover state |

### Neutral Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Dark Gray | `#1A1A1A` | Primary text |
| Gray | `#333333` | Secondary text |
| Light Gray | `#F5F5F5` | Backgrounds, sections |
| Border | `#E0E0E0` | Borders, dividers |
| White | `#FFFFFF` | Main background |

### Status Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Success | `#27AE60` | ✓ Success messages |
| Warning | `#E67E22` | ⚠ Warning alerts |
| Error | `#E74C3C` | ✗ Error messages |
| Info | `#3498DB` | ℹ Info messages |

---

## Component Styles

### Button Variants

#### Primary Button
```jsx
<button className="btn btn-primary">Send</button>
```
- Background: Blue gradient
- Hover: Lighter gradient, lift effect
- Best for: Main actions, CTAs

#### Secondary Button
```jsx
<button className="btn btn-secondary">Cancel</button>
```
- Background: White, Blue border
- Hover: Light gray background
- Best for: Alternative actions

#### Accent Button
```jsx
<button className="btn btn-accent">Upgrade</button>
```
- Background: Gold
- Hover: Warm gold
- Best for: Premium features

#### Danger Button
```jsx
<button className="btn btn-danger">Delete</button>
```
- Background: Red
- Hover: Dark red
- Best for: Destructive actions

### Size Variants
```jsx
<button className="btn btn-primary btn-sm">Small</button>
<button className="btn btn-primary">Default (Normal)</button>
<button className="btn btn-primary btn-lg">Large</button>
<button className="btn btn-primary btn-full">Full Width</button>
```

---

## Spacing Reference

| Variable | Size | Usage |
|----------|------|-------|
| `--spacing-xs` | 4px | Minimal spacing |
| `--spacing-sm` | 8px | Between elements |
| `--spacing-md` | 16px | Standard gaps |
| `--spacing-lg` | 24px | Section spacing |
| `--spacing-xl` | 32px | Large sections |
| `--spacing-2xl` | 48px | Extra breathing room |

---

## Typography Sizes

| Size | pixels | Usage |
|------|--------|-------|
| `--font-size-xs` | 12px | Metadata, badges |
| `--font-size-sm` | 14px | Small text, hints |
| `--font-size-base` | 16px | Body text |
| `--font-size-lg` | 18px | Slightly larger text |
| `--font-size-xl` | 20px | Subheadings |
| `--font-size-2xl` | 24px | Section headings |
| `--font-size-3xl` | 32px | Page headings |
| `--font-size-4xl` | 40px | Title headings |

---

## Border Radius

| Variable | Size | Usage |
|----------|------|-------|
| `--radius-sm` | 4px | Subtle curves |
| `--radius-md` | 8px | Standard inputs, small cards |
| `--radius-lg` | 12px | Cards, containers |
| `--radius-xl` | 16px | Large containers |

---

## Common Patterns

### Form Group
```jsx
<div className="form-group">
  <label htmlFor="email">Email Address</label>
  <input id="email" type="email" placeholder="your@email.com" />
  <p className="label-hint">We'll never share your email</p>
</div>
```

### Section with Header
```jsx
<div className="content-section">
  <h3>Section Title</h3>
  <p>Section content goes here...</p>
</div>
```

### Chat Message - User
```jsx
<div className="message user">
  <div className="message-content">
    This is the user's message
  </div>
</div>
```

### Chat Message - Bot
```jsx
<div className="message bot">
  <div className="message-content">
    This is the bot's response
  </div>
</div>
```

### Alert/Success Message
```jsx
<div className="message-box success">
  <div className="message-box-icon">✓</div>
  <div className="message-box-content">
    <div className="message-box-title">Success!</div>
    <div className="message-box-text">Your changes have been saved.</div>
  </div>
</div>
```

### Card with Footer
```jsx
<div className="card">
  <div className="card-header">
    <h3>Card Title</h3>
  </div>
  <div className="card-body">
    Card content here
  </div>
  <div className="card-footer">
    <button className="btn btn-secondary">Cancel</button>
    <button className="btn btn-primary">Confirm</button>
  </div>
</div>
```

---

## Utility Classes

### Flex Layout
```jsx
<div className="flex">Two items side by side</div>
<div className="flex-col">Column layout</div>
<div className="flex-center">Centered content</div>
<div className="flex-between">Space-between layout</div>
```

### Spacing
```jsx
<div className="gap-sm">Small gap between children</div>
<div className="gap-md">Medium gap</div>
<div className="gap-lg">Large gap</div>

<div className="mb-lg">Large margin bottom</div>
<div className="mt-md">Medium margin top</div>
<div className="p-lg">Large padding</div>
```

### Text Styles
```jsx
<p className="text-center">Centered text</p>
<p className="text-sm">Small text</p>
<p className="text-muted">Muted gray text</p>
<p className="text-primary">Blue text</p>
<p className="font-bold">Bold text</p>
```

### Backgrounds & Borders
```jsx
<div className="bg-light">Light background</div>
<div className="bg-primary">Blue background</div>
<div className="rounded-md">Rounded corners</div>
```

---

## Responsive Design

### Mobile-First Approach

```css
/* Mobile first (default) */
.container { padding: 16px; }

/* Tablet and up */
@media (min-width: 768px) {
  .container { padding: 24px; }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container { max-width: 1200px; }
}
```

### Breakpoints
- **Mobile**: < 480px
- **Tablet**: 480px - 768px
- **Desktop**: > 768px

---

## CSS Variables Usage

### In Your CSS
```css
background-color: var(--primary-main);
padding: var(--spacing-lg);
border-radius: var(--radius-md);
box-shadow: var(--shadow-md);
transition: all var(--transition-normal);
```

### All Available Variables
```css
/* Colors */
--primary-dark, --primary-main, --primary-light
--accent-gold, --accent-warm
--neutral-dark, --neutral-gray, --neutral-light, --neutral-border, --neutral-white
--success-green, --warning-orange, --error-red, --info-blue

/* Spacing */
--spacing-xs through --spacing-2xl

/* Typography */
--font-primary, --font-secondary, --font-mono
--font-size-xs through --font-size-4xl
--font-weight-light through --font-weight-bold
--line-height-tight, --line-height-normal, --line-height-relaxed

/* Borders & Radius */
--radius-sm through --radius-xl

/* Shadows */
--shadow-sm, --shadow-md, --shadow-lg

/* Transitions */
--transition-fast, --transition-normal, --transition-slow

/* Z-index */
--z-index-dropdown, --z-index-sticky, --z-index-modal, --z-index-tooltip
```

---

## Common Tasks

### Change Primary Color
Edit `frontend/src/styles.css`, update `:root`:
```css
--primary-main: #NEW_COLOR;
--primary-dark: #DARKER_SHADE;
--primary-light: #LIGHTER_SHADE;
```

### Adjust Spacing
Edit `:root` spacing variables:
```css
--spacing-md: 16px;  /* Change from 16px to preferred size */
```

### Add Custom Button Style
```css
.btn-custom {
  background: linear-gradient(135deg, #color1 0%, #color2 100%);
  color: white;
  /* other styles */
}
```

### Create New Message Type
```jsx
<div className="message-box custom-type">
  <div className="message-box-content">
    {/* content */}
  </div>
</div>
```

---

## Accessibility Checklist

- [ ] All interactive elements keyboard accessible
- [ ] Color contrast ≥ 4.5:1 for text
- [ ] All inputs have associated labels
- [ ] Focus states visible
- [ ] Error messages clear and descriptive
- [ ] Images have alt text
- [ ] Semantic HTML used
- [ ] Font sizes readable (≥ 16px for inputs)
- [ ] Touch targets ≥ 44x44px
- [ ] Sufficient line-height (≥ 1.5)

---

## Files to Reference

- **Main Styles**: `frontend/src/styles.css`
- **Component Implementation**: `frontend/src/App.jsx`
- **Full Documentation**: `frontend/STYLE_GUIDE.md`

---

## Support

For questions or customization requests:
1. Review `frontend/STYLE_GUIDE.md` for detailed information
2. Check `frontend/src/styles.css` for available variables
3. Refer to component examples in this file
4. Maintain consistency across implementations

---

**Version**: 1.0  
**Last Updated**: 2024  
**Inspiration**: Malaysia Airlines Enterprise Design System
