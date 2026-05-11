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
        'sticky top-0 z-40 w-full shadow-md',
        'bg-gradient-to-r from-[hsl(var(--primary-dark,215_100%_25%))] to-[hsl(var(--primary,207_100%_26%))]',
        className
      )}
    >
      <div className="container mx-auto px-6 py-4">
        <div className={cn(
          "flex items-center",
          children ? "justify-between" : "justify-center"
        )}>
          <div className={cn(children ? "flex-1" : "text-center")}>
            <h1 className="text-3xl font-bold text-white">
              {title}
            </h1>
            {subtitle && (
              <p className="mt-1 text-sm text-white/80">{subtitle}</p>
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
