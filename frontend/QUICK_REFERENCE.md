# Quick Reference Card - New UI System

## 🚀 Quick Start

### Import Components
```jsx
import { Button, Card, Input, Label } from './components/ui';
import { Header, Container } from './components/layout';
import { cn } from './lib/utils';
```

---

## 🎨 Color Classes

### Primary (Purple)
```
bg-primary         text-primary         border-primary
bg-primary-50      text-purple-600      border-purple-600
bg-primary-foreground
```

### Neutral
```
bg-muted           text-muted-foreground    border-border
bg-background      text-foreground          border-input
bg-card            text-card-foreground
```

### Semantic
```
bg-destructive     text-success             border-error
```

---

## 📏 Spacing Scale

```
p-1  → 4px      gap-1  → 4px      m-1  → 4px
p-2  → 8px      gap-2  → 8px      m-2  → 8px
p-4  → 16px     gap-4  → 16px     m-4  → 16px
p-6  → 24px     gap-6  → 24px     m-6  → 24px
p-8  → 32px     gap-8  → 32px     m-8  → 32px
```

---

## 🔤 Typography

### Font Sizes
```
text-xs    → 12px
text-sm    → 14px
text-base  → 16px
text-lg    → 18px
text-xl    → 20px
text-2xl   → 24px
text-3xl   → 30px
text-4xl   → 36px
```

### Font Weights
```
font-light     → 300
font-normal    → 400
font-medium    → 500
font-semibold  → 600
font-bold      → 700
```

---

## 🧩 Common Patterns

### Card with Form
```jsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent className="space-y-4">
    <div>
      <Label htmlFor="field">Label</Label>
      <Input id="field" />
    </div>
  </CardContent>
  <CardFooter>
    <Button>Submit</Button>
  </CardFooter>
</Card>
```

### Flex Layout
```jsx
// Horizontal
<div className="flex items-center gap-4">

// Vertical
<div className="flex flex-col space-y-4">

// Between
<div className="flex items-center justify-between">
```

### Grid Layout
```jsx
// 2 columns on tablet+
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">

// 3 columns on desktop+
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

### Responsive Text
```jsx
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
```

---

## 🎭 Button Variants

```jsx
<Button variant="primary">    // Gradient purple
<Button variant="secondary">  // Outlined
<Button variant="ghost">      // Transparent
<Button variant="outline">    // Purple outline
<Button variant="destructive">// Red
<Button variant="link">       // Text link
```

### Button Sizes
```jsx
<Button size="sm">    // Small
<Button size="md">    // Medium (default)
<Button size="lg">    // Large
<Button size="icon">  // Square icon
```

---

## 🏷️ Badge Variants

```jsx
<Badge variant="primary">New</Badge>
<Badge variant="success">Active</Badge>
<Badge variant="error">Failed</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="outline">Draft</Badge>
```

---

## 🔔 Toast Notifications

```jsx
const { toast } = useToast();

toast('Success!', 'success');
toast('Error occurred', 'error');
toast('Warning message', 'warning');
toast('Info message', 'info', 5000); // 5 second duration
```

---

## 📱 Breakpoints

```jsx
sm:   640px   // Mobile landscape
md:   768px   // Tablet
lg:   1024px  // Desktop
xl:   1280px  // Large desktop
2xl:  1536px  // Extra large
```

### Usage
```jsx
<div className="hidden md:block">  // Hide on mobile
<div className="md:w-1/2">        // Half width on tablet+
<div className="space-y-4 md:space-y-6">  // More space on tablet+
```

---

## 🎨 Shadows

```
shadow-sm   // Subtle
shadow-md   // Medium (default)
shadow-lg   // Large
shadow-xl   // Extra large
shadow-none // No shadow
```

---

## 🔲 Border Radius

```
rounded-sm   → 6px
rounded-md   → 8px
rounded-lg   → 12px
rounded-xl   → 16px
rounded-full → 9999px
```

---

## ♿ Accessibility Quick Checks

### Every Interactive Element
```jsx
// Focus ring
className="focus-visible:ring-2 focus-visible:ring-ring"

// Label association
<Label htmlFor="input-id">Label</Label>
<Input id="input-id" />

// Icon button label
<Button aria-label="Close">
  <X className="h-4 w-4" />
</Button>
```

---

## 🎬 Animations

### Framer Motion
```jsx
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
```

### CSS Transitions
```jsx
className="transition-all duration-300 hover:scale-105"
```

---

## 🛠️ Utility Functions

### className Merger
```jsx
import { cn } from './lib/utils';

<div className={cn(
  'base-classes',
  condition && 'conditional-classes',
  props.className
)} />
```

---

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| **DEVELOPER_GUIDE.md** | Complete API reference |
| **ACCESSIBILITY.md** | WCAG compliance |
| **MIGRATION_GUIDE.md** | MUI → New system |
| **IMPLEMENTATION_STATUS.md** | Project status |

---

## 🐛 Common Fixes

### Styles not applying?
1. Check `index.css` is imported in `index.js`
2. Verify Tailwind config `content` paths
3. Restart dev server

### Component not found?
```jsx
// ❌ Wrong
import Button from './components/Button';

// ✅ Correct
import { Button } from './components/ui';
```

### Colors not working?
```jsx
// ❌ Avoid
className="bg-[#9333ea]"

// ✅ Use tokens
className="bg-primary"
className="bg-purple-600"
```

---

## 🔗 External Resources

- [Tailwind Docs](https://tailwindcss.com/docs)
- [Lucide Icons](https://lucide.dev/)
- [Framer Motion](https://www.framer.com/motion/)

---

**Print this card for quick reference!**
