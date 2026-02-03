# Developer Guide - UI Component Library

## Table of Contents
1. [Getting Started](#getting-started)
2. [Theme System](#theme-system)
3. [Component Library](#component-library)
4. [Styling Guidelines](#styling-guidelines)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

---

## Getting Started

### Installation
The UI system uses Tailwind CSS with custom design tokens. All dependencies are already installed.

### Import Components
```javascript
// Import individual components
import { Button, Card, Input } from './components/ui';

// Import layout components
import { Header, Container, PageTransition } from './components/layout';

// Import utilities
import { cn } from './lib/utils';
```

---

## Theme System

### Design Tokens
Located in `src/theme/tokens.js`, design tokens define the core design values:

```javascript
import { designTokens } from './theme/tokens';

// Access colors
designTokens.colors.purple[600]  // #9333ea
designTokens.colors.neutral[500] // #737373
designTokens.colors.gold[400]    // #facc15

// Access spacing
designTokens.spacing[4]  // 1rem (16px)
designTokens.spacing[8]  // 2rem (32px)

// Access typography
designTokens.typography.fontSize.lg  // 1.125rem
designTokens.typography.fontWeight.bold  // 700
```

### Purple Theme
Located in `src/theme/purple.js`, provides theme-specific styles:

```javascript
import { purpleTheme } from './theme/purple';

// Use gradients
purpleTheme.gradients.primary  // Primary gradient
purpleTheme.gradients.hero     // Hero section gradient

// Access component styles
purpleTheme.components.button.primary
purpleTheme.components.card.shadow
```

### CSS Custom Properties
Theme variables are defined in `src/index.css`:

```css
/* Light theme */
:root {
  --primary: 271 91% 65%;
  --background: 0 0% 100%;
  --foreground: 262 80% 12%;
  /* ... more variables */
}

/* Dark theme */
.dark {
  --primary: 271 91% 65%;
  --background: 262 80% 5%;
  --foreground: 0 0% 98%;
  /* ... more variables */
}
```

---

## Component Library

### Button Component

#### Basic Usage
```jsx
import { Button } from './components/ui';

<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>
```

#### Variants
- `primary`: Purple gradient (default)
- `secondary`: Outlined with border
- `ghost`: Text only with hover
- `outline`: Primary color outline
- `destructive`: Red for dangerous actions
- `link`: Underlined text link

#### Sizes
- `sm`: Small (h-9)
- `md`: Medium (h-10) - default
- `lg`: Large (h-12)
- `icon`: Square icon button (h-10 w-10)

#### Examples
```jsx
// Primary action button
<Button variant="primary" size="lg">
  Submit Form
</Button>

// Secondary action
<Button variant="secondary">
  Cancel
</Button>

// Icon button
<Button variant="ghost" size="icon" aria-label="Close">
  <X className="h-4 w-4" />
</Button>

// Disabled state
<Button disabled>
  Processing...
</Button>
```

### Card Component

#### Structure
```jsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './components/ui';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Optional description</CardDescription>
  </CardHeader>
  <CardContent>
    Main content goes here
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

#### Examples
```jsx
// Simple card
<Card>
  <CardContent className="p-6">
    <p>Simple card content</p>
  </CardContent>
</Card>

// Card with hover effect
<Card className="hover:shadow-xl transition-shadow cursor-pointer">
  <CardContent>
    Interactive card
  </CardContent>
</Card>

// Glass morphism card
<Card className="glass">
  <CardContent>
    Transparent blurred card
  </CardContent>
</Card>
```

### Input & Label

#### Basic Form
```jsx
import { Label, Input } from './components/ui';

<div className="space-y-2">
  <Label htmlFor="email">Email Address</Label>
  <Input 
    id="email" 
    type="email" 
    placeholder="you@example.com"
    required
  />
</div>
```

#### With Validation
```jsx
const [error, setError] = useState('');

<div className="space-y-2">
  <Label htmlFor="password">Password</Label>
  <Input 
    id="password" 
    type="password"
    className={error ? 'border-red-500' : ''}
  />
  {error && (
    <p className="text-sm text-red-600">{error}</p>
  )}
</div>
```

### Select Component

```jsx
import { Label, Select } from './components/ui';

<div className="space-y-2">
  <Label htmlFor="country">Country</Label>
  <Select id="country" value={value} onChange={handleChange}>
    <option value="">Select a country</option>
    <option value="us">United States</option>
    <option value="uk">United Kingdom</option>
    <option value="ca">Canada</option>
  </Select>
</div>
```

### Table Component

```jsx
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from './components/ui';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Email</TableHead>
      <TableHead>Role</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>John Doe</TableCell>
      <TableCell>john@example.com</TableCell>
      <TableCell>Admin</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Modal Component

```jsx
import { Modal } from './components/ui';

const [isOpen, setIsOpen] = useState(false);

<Modal 
  isOpen={isOpen} 
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
  size="md"
>
  <p>Are you sure you want to proceed?</p>
  <div className="flex gap-2 mt-4">
    <Button onClick={() => setIsOpen(false)}>Cancel</Button>
    <Button variant="primary">Confirm</Button>
  </div>
</Modal>
```

### Badge Component

```jsx
import { Badge } from './components/ui';

<Badge variant="primary">New</Badge>
<Badge variant="success">Active</Badge>
<Badge variant="error">Failed</Badge>
<Badge variant="outline">Draft</Badge>
```

### Toast Notifications

```jsx
import { useToast } from './components/ui';

function MyComponent() {
  const { toast } = useToast();
  
  const handleSuccess = () => {
    toast('Operation completed successfully!', 'success');
  };
  
  const handleError = () => {
    toast('An error occurred', 'error', 5000);
  };
  
  return (
    <Button onClick={handleSuccess}>Show Toast</Button>
  );
}
```

### Loading States

#### Skeleton Loader
```jsx
import { Skeleton } from './components/ui';

<div className="space-y-3">
  <Skeleton className="h-12 w-full" />
  <Skeleton className="h-4 w-3/4" />
  <Skeleton className="h-4 w-1/2" />
</div>
```

#### Empty State
```jsx
import { EmptyState } from './components/ui';
import { FileX } from 'lucide-react';

<EmptyState
  icon={FileX}
  title="No results found"
  description="Try adjusting your search criteria"
  action={() => handleReset()}
  actionLabel="Reset Filters"
/>
```

---

## Styling Guidelines

### Using Tailwind Classes

```jsx
// ✅ Good: Use Tailwind utilities
<div className="flex items-center gap-4 p-6 rounded-lg bg-white shadow-md">

// ❌ Avoid: Inline styles
<div style={{ display: 'flex', padding: '24px', ... }}>
```

### Combining Classes with cn()

```jsx
import { cn } from './lib/utils';

// Merge classes with proper precedence
<div className={cn(
  'base-classes',
  condition && 'conditional-classes',
  props.className  // Allow external overrides
)} />
```

### Responsive Design

```jsx
// Mobile-first approach
<div className="
  flex flex-col         /* Mobile: stack */
  md:flex-row          /* Tablet: horizontal */
  lg:gap-8             /* Desktop: larger gap */
">
```

### Theme Colors

```jsx
// ✅ Use theme variables
<div className="bg-primary text-primary-foreground">

// ✅ Use token colors
<div className="bg-purple-600 text-white">

// ❌ Avoid arbitrary colors
<div className="bg-[#9333ea]">  // Use only when necessary
```

---

## Best Practices

### 1. Component Composition
```jsx
// ✅ Build complex UIs from simple components
<Card>
  <CardHeader>
    <CardTitle>User Profile</CardTitle>
  </CardHeader>
  <CardContent>
    <div className="space-y-4">
      <div>
        <Label>Name</Label>
        <Input value={name} onChange={setName} />
      </div>
    </div>
  </CardContent>
  <CardFooter>
    <Button>Save Changes</Button>
  </CardFooter>
</Card>
```

### 2. Accessibility First
```jsx
// Always include labels
<Label htmlFor="email">Email</Label>
<Input id="email" type="email" />

// Icon buttons need aria-label
<Button aria-label="Close dialog">
  <X className="h-4 w-4" />
</Button>

// Use semantic HTML
<main>
  <article>
    <h1>Page Title</h1>
  </article>
</main>
```

### 3. Consistent Spacing
```jsx
// Use design tokens for spacing
<div className="space-y-6">     // 24px vertical spacing
  <div className="p-4">          // 16px padding
    <div className="mb-2">       // 8px margin bottom
```

### 4. Animation Guidelines
```jsx
// Use Framer Motion for complex animations
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>

// Use CSS transitions for simple effects
<button className="transition-all duration-300 hover:scale-105">
```

---

## Examples

### Login Form
```jsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter, Label, Input, Button } from './components/ui';

function LoginForm() {
  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Sign In</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" placeholder="you@example.com" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" />
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full">Sign In</Button>
      </CardFooter>
    </Card>
  );
}
```

### Data Table with Actions
```jsx
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell, Button, Badge } from './components/ui';
import { Edit, Trash } from 'lucide-react';

function UsersTable({ users }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Role</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map(user => (
          <TableRow key={user.id}>
            <TableCell className="font-medium">{user.name}</TableCell>
            <TableCell>
              <Badge variant={user.active ? 'success' : 'secondary'}>
                {user.active ? 'Active' : 'Inactive'}
              </Badge>
            </TableCell>
            <TableCell>{user.role}</TableCell>
            <TableCell className="text-right space-x-2">
              <Button variant="ghost" size="icon">
                <Edit className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Trash className="h-4 w-4" />
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

### Dashboard Layout
```jsx
import { Header, Container, PageTransition } from './components/layout';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui';

function Dashboard() {
  return (
    <PageTransition>
      <Header 
        title="Dashboard" 
        subtitle="Welcome back, user!"
      />
      
      <Container className="mt-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Total Users</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">1,234</p>
            </CardContent>
          </Card>
          
          {/* More cards... */}
        </div>
      </Container>
    </PageTransition>
  );
}
```

---

## Additional Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Lucide Icons](https://lucide.dev/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated**: November 26, 2025
