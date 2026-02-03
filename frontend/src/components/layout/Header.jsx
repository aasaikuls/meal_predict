/**
 * Header Component
 * Modern application header with gradient and glass morphism
 */

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

const Header = ({ title, subtitle, children, className }) => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={cn(
        'sticky top-0 z-40 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60',
        className
      )}
    >
      <div className="container mx-auto px-4 py-6">
        <div className={cn(
          "flex items-center",
          children ? "justify-between" : "justify-center"
        )}>
          <div className={cn(children ? "flex-1" : "text-center")}>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              {title}
            </h1>
            {subtitle && (
              <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
            )}
          </div>
          {children && (
            <div className="flex items-center gap-4">
              {children}
            </div>
          )}
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
