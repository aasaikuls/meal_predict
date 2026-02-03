/**
 * Button Component
 * Modern, accessible button with variants and sizes
 */

import React from 'react';
import { cn } from '../../lib/utils';

const buttonVariants = {
  variant: {
    primary: 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg hover:shadow-xl hover:from-purple-700 hover:to-purple-800 active:scale-95',
    secondary: 'border-2 border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground',
    ghost: 'text-foreground hover:bg-accent hover:text-accent-foreground',
    outline: 'border-2 border-primary text-primary hover:bg-primary hover:text-white',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    link: 'text-primary underline-offset-4 hover:underline',
  },
  size: {
    sm: 'h-9 px-3 text-sm rounded-md',
    md: 'h-10 px-4 text-base rounded-lg',
    lg: 'h-12 px-6 text-lg rounded-lg',
    icon: 'h-10 w-10 rounded-lg',
  },
};

const Button = React.forwardRef(({
  className,
  variant = 'primary',
  size = 'md',
  disabled = false,
  children,
  ...props
}, ref) => {
  return (
    <button
      ref={ref}
      className={cn(
        // Base styles
        'inline-flex items-center justify-center font-medium transition-all duration-300',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        // Variant styles
        buttonVariants.variant[variant],
        buttonVariants.size[size],
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
