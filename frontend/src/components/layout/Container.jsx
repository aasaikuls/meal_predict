/**
 * Container Component
 * Responsive container with max-width constraints
 */

import React from 'react';
import { cn } from '../../lib/utils';

const Container = ({ 
  children, 
  className, 
  size = 'default',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'max-w-3xl',
    default: 'max-w-7xl',
    lg: 'max-w-[1440px]',
    full: 'max-w-full',
  };
  
  return (
    <div
      className={cn(
        'mx-auto w-full px-4 sm:px-6 lg:px-8',
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Container;
