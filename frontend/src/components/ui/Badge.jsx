/**
 * Badge Component
 * Small status indicators and labels
 */

import React from 'react';
import { cn } from '../../lib/utils';

const badgeVariants = {
  variant: {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/80',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    outline: 'border border-border text-foreground',
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-white',
  },
};

const Badge = React.forwardRef(({ className, variant = 'primary', ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
        'transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        badgeVariants.variant[variant],
        className
      )}
      {...props}
    />
  );
});

Badge.displayName = 'Badge';

export default Badge;
