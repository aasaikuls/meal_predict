# Enterprise AI Chatbot - Style Guide Documentation

## Overview

This style guide is inspired by Malaysia Airlines' design system and modern enterprise application best practices. It emphasizes professionalism, clarity, accessibility, and a premium user experience.

---

## 1. Color Palette

### Primary Colors (Trust & Authority)
- **Primary Dark** (`#003580`): Deep blue used for primary actions, headers, and key elements
- **Primary Main** (`#004B87`): Malaysia Airlines signature blue - used for interactive elements and hover states
- **Primary Light** (`#0066CC`): Lighter blue for hover and focus states

### Accent Colors (Premium Feel)
- **Gold** (`#D4AF37`): Premium accent for special features, upgrades, and highlights
- **Warm Gold** (`#F5A623`): Secondary accent for hover states and emphasis

### Neutral Colors (Clean Backgrounds)
- **Dark Gray** (`#1A1A1A`): Primary text color for maximum readability
- **Gray** (`#333333`): Secondary text for descriptions and metadata
- **Light Gray** (`#F5F5F5`): Background for sections and elevated content
- **Border** (`#E0E0E0`): Subtle borders for structure
- **White** (`#FFFFFF`): Main background

### Status Colors
- **Success Green** (`#27AE60`): Positive actions and confirmations
- **Warning Orange** (`#E67E22`): Caution states and warnings
- **Error Red** (`#E74C3C`): Errors and destructive actions
- **Info Blue** (`#3498DB`): Informational messages

---

## 2. Typography

### Font Family
- **Primary Font**: Segoe UI, Roboto, system fonts
  - Professional, clean, and widely supported
  - Excellent readability on all screen sizes
  - Used for all body text and UI elements
- **Secondary Font**: Georgia (serif)
  - Used for special content like quotes or published materials
- **Monospace Font**: Monaco, Courier New
  - Used for code, technical content, and chat messages

### Font Sizes
- **Heading 1** (40px, Bold): Page titles
- **Heading 2** (32px, Semibold): Major sections
- **Heading 3** (24px, Semibold): Card titles and subsections
- **Heading 4** (20px, Semibold): Form labels and minor headings
- **Body Text** (16px, Regular): Default text
- **Small Text** (14px, Regular): Descriptions and hints
- **Tiny Text** (12px, Regular): Metadata and footer information

### Font Weights
- **Light** (300): Minimal use, large display text
- **Regular** (400): Body text and descriptions
- **Semibold** (600): Labels, headings, and emphasis
- **Bold** (700): Main headings and strong emphasis

### Line Heights
- **Tight** (1.2): Headings
- **Normal** (1.5): Body text
- **Relaxed** (1.75): Large text blocks and accessibility

---

## 3. Spacing System

Based on 8px increments for consistent alignment:
- **XS** (4px): Minimal spacing between inline elements
- **SM** (8px): Default spacing between components
- **MD** (16px): Standard spacing within sections
- **LG** (24px): Spacing between major sections
- **XL** (32px): Large gaps between sections
- **2XL** (48px): Extra-large spacing for visual breathing room

---

## 4. Component Library

### Buttons

#### Primary Button (CTA)
```
Background: Gradient blue (Primary Main → Primary Dark)
Color: White
Padding: 16px 24px
Border-radius: 8px
Hover: Lighter gradient, shadow increase, slight lift effect
States: Normal, Hover, Active, Disabled
```
**Usage**: Main call-to-action buttons, form submissions, confirmations

#### Secondary Button
```
Background: White
Color: Primary Blue
Border: 2px Primary Blue
Hover: Light gray background
```
**Usage**: Alternative actions, cancel buttons, non-destructive options

#### Accent Button
```
Background: Gold
Color: Dark Gray
Hover: Warm Gold
```
**Usage**: Premium features, upsells, special offers

#### Danger Button
```
Background: Red
Color: White
Hover: Darker Red
```
**Usage**: Destructive actions, deletions, confirmations

### Form Elements

#### Text Inputs & Selects
```
Border: 1px solid Light Gray
Padding: 16px
Border-radius: 8px
Focus: Blue border + blue shadow
Font: Segoe UI, 16px
```
**Best Practices**:
- Always include labels above inputs
- Use placeholder text sparingly
- Provide clear focus states
- Maintain adequate padding for touch targets (48px minimum)

#### Textareas
```
Min-height: 100px
Resizable: Vertical only
Font: Monospace for chat/code
```

### Cards
```
Background: White
Border: 1px Light Gray
Padding: 24px
Border-radius: 12px
Shadow: 0 2px 4px rgba(0,0,0,0.1)
Hover: Increased shadow, blue border
```

### Chat Messages
```
User Messages:
  - Alignment: Right
  - Background: Blue gradient
  - Color: White
  - Border-radius: 12px 8px 8px 12px
  
Bot Messages:
  - Alignment: Left
  - Background: Light Gray
  - Color: Dark Gray
  - Border-radius: 8px 12px 12px 8px
```

### Alert/Message Boxes
```
Border-left: 4px colored
Padding: 16px
Border-radius: 8px
Background: Subtle tint of status color

Types: Success (green), Error (red), Warning (orange), Info (blue)
```

---

## 5. Layout & Structure

### Header
- **Background**: Blue gradient
- **Text Color**: White
- **Sticky**: Remains visible on scroll
- **Padding**: 24px horizontal, 16px vertical
- **Contains**: Logo/Title + Subtitle/Description

### Main Content
```
Max-width: 1200px
Centered on page
Padding: 32px (desktop), 16px (mobile)
Margin: 0 auto
```

### Sections
```
Background: White
Border: 1px Light Gray
Padding: 24px
Margin-bottom: 32px
Border-radius: 12px
Shadow: Subtle on normal, medium on hover
```

---

## 6. Shadows & Depth

- **sm**: `0 2px 4px rgba(0,0,0,0.1)` - Subtle elevation
- **md**: `0 4px 12px rgba(0,0,0,0.15)` - Medium elevation
- **lg**: `0 8px 24px rgba(0,0,0,0.2)` - Strong elevation

**Usage**: Build visual hierarchy and draw attention to interactive elements

---

## 7. Animations & Transitions

### Standard Transitions
- **Fast** (150ms): UI state changes (hover, focus)
- **Normal** (300ms): Component animations, interactions
- **Slow** (500ms): Page transitions, featured content

### Animations
- **Fade In**: New messages, content load
- **Typing Indicator**: Chat thinking state (animated dots)
- **Hover Effects**: Buttons lift, shadows increase
- **Focus States**: Smooth outline and shadow

---

## 8. Responsive Design

### Breakpoints

#### Desktop (>768px)
- Full width layouts
- Multi-column forms
- Hover states active
- Full typography sizes

#### Tablet (768px - 481px)
- Adjusted padding (24px)
- Single column forms
- Optimized touch targets
- Reduced max-widths

#### Mobile (<480px)
- Full width content
- Single column everything
- Larger touch targets (min 44x44px)
- Simplified navigation
- Reduced padding (16px)

### Mobile-First Principles
- Start with mobile design
- Layer enhancements for larger screens
- Touch-friendly minimum: 44x44px buttons
- Adequate spacing between interactive elements
- Readable font sizes (minimum 16px for inputs)

---

## 9. Accessibility Features

### Color Contrast
- Minimum 4.5:1 ratio for text
- 3:1 ratio for large text and UI components
- Never rely on color alone for meaning

### Interactive Elements
- **Focus States**: Always visible, minimum 3px outline
- **Labels**: All inputs have visible labels
- **Error Messages**: Clear, descriptive text
- **ARIA Labels**: Provided where necessary

### Typography
- Sufficient line-height (1.5 minimum)
- Appropriate font sizes
- Clear hierarchy using size and weight

### Keyboard Navigation
- All buttons and links keyboard accessible
- Tab order logical and intuitive
- Skip navigation links if necessary

---

## 10. Enterprise Design Principles

### 1. **Professionalism**
- Clean, minimal aesthetic
- Generous whitespace
- Professional color palette
- Clear hierarchy

### 2. **Trust & Authority**
- Consistent branding
- Premium feel (gold accents)
- Reliable visual patterns
- Clear communication

### 3. **Clarity**
- Clear labels and instructions
- Obvious call-to-action buttons
- Meaningful error messages
- Logical content organization

### 4. **Accessibility**
- WCAG AA compliance target
- Clear focus states
- Sufficient contrast
- Semantic HTML

### 5. **Performance**
- Optimized assets
- Smooth animations
- Fast interactions
- Efficient rendering

---

## 11. Usage Guidelines

### For Headers
```jsx
<div className="header">
  <h1>Page Title</h1>
  <p>Subtitle or description</p>
</div>
```

### For Sections
```jsx
<div className="content-section">
  <h3>Section Title</h3>
  {/* Content */}
</div>
```

### For Buttons
```jsx
<button className="btn btn-primary">Action</button>
<button className="btn btn-secondary">Alternative</button>
<button className="btn btn-accent btn-sm">Small Accent</button>
```

### For Forms
```jsx
<div className="form-group">
  <label htmlFor="input">Label</label>
  <input id="input" type="text" placeholder="Hint text" />
  <p className="label-hint">Helper text</p>
</div>
```

### For Chat
```jsx
<div className="chat-container">
  <div className="chat-messages">
    <div className="message user">
      <div className="message-content">User message</div>
    </div>
    <div className="message bot">
      <div className="message-content">Bot response</div>
    </div>
  </div>
  <div className="chat-input-area">
    <textarea placeholder="Type here..." />
    <button className="btn btn-primary">Send</button>
  </div>
</div>
```

---

## 12. Design System Updates

To maintain consistency:
1. **CSS Variables**: All colors, spacing, typography defined as variables
2. **Single Source of Truth**: Update `:root` for global changes
3. **Class Names**: BEM-like structure for clarity
4. **Documentation**: Keep this guide updated with changes

---

## 13. Implementation Checklist

- [x] Color variables defined
- [x] Typography hierarchy established
- [x] Spacing system consistent
- [x] Button styles standardized
- [x] Form elements styled
- [x] Chat interface designed
- [x] Responsive breakpoints implemented
- [x] Accessibility features included
- [x] Hover/Focus states defined
- [x] Animation/Transition consistent

---

## 14. File References

- **Styles**: `frontend/src/styles.css` - All design tokens and components
- **Components**: `frontend/src/App.jsx` - React implementation
- **HTML**: `frontend/index.html` - Entry point

---

## Questions or Customization?

This style guide provides a solid foundation. You can:
- Adjust colors to match your brand
- Modify spacing for your layout preferences
- Add new component variants as needed
- Extend animations for specific interactions
- Customize responsive breakpoints

Remember: **Consistency is key**. Use CSS variables and maintain the documented patterns for a cohesive user experience.
