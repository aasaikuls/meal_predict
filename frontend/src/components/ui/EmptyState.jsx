/**
 * EmptyState Component
 * Displays empty state with optional action
 */

import React from 'react';
import { cn } from '../../lib/utils';
import { FileX } from 'lucide-react';
import Button from './Button';

const EmptyState = ({ 
  icon: Icon = FileX,
  title = 'No data available',
  description,
  action,
  actionLabel,
  className 
}) => {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12 px-4 text-center', className)}>
      <div className="rounded-full bg-muted p-6 mb-4">
        <Icon className="h-12 w-12 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-muted-foreground mb-6 max-w-md">
          {description}
        </p>
      )}
      {action && actionLabel && (
        <Button onClick={action} variant="primary">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
