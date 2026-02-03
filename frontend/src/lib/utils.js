/**
 * Utility functions for className management
 */

import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges Tailwind CSS classes with proper precedence
 * @param {...(string | undefined | null | false)[]} inputs - Class names to merge
 * @returns {string} Merged class names
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Creates a variant-based className generator
 * @param {Object} config - Variant configuration
 * @returns {Function} Variant className generator
 */
export function cva(base, config) {
  return (props = {}) => {
    const { variants = {}, defaultVariants = {} } = config;
    const mergedProps = { ...defaultVariants, ...props };
    
    const variantClasses = Object.entries(mergedProps)
      .map(([key, value]) => variants[key]?.[value])
      .filter(Boolean);
    
    return cn(base, ...variantClasses, props.className);
  };
}

export default cn;
