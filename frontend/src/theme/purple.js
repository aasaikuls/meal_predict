/**
 * Purple Theme - Modern Professional Design
 * Based on the chatbot_reference purple theme with Tailwind CSS integration
 */

import { designTokens } from './tokens';

export const purpleTheme = {
  name: 'purple',
  displayName: 'Purple Professional',
  
  // CSS Custom Properties for Tailwind
  cssVariables: {
    light: {
      // Base colors
      '--background': '0 0% 100%',           // White
      '--foreground': '262 80% 12%',         // Deep purple text
      
      // Card colors
      '--card': '0 0% 100%',
      '--card-foreground': '262 80% 12%',
      
      // Popover colors
      '--popover': '0 0% 100%',
      '--popover-foreground': '262 80% 12%',
      
      // Primary (Purple)
      '--primary': '271 91% 65%',            // Purple 600
      '--primary-foreground': '0 0% 100%',
      
      // Secondary (Gold accent)
      '--secondary': '48 96% 53%',           // Gold 400
      '--secondary-foreground': '262 80% 12%',
      
      // Muted (Neutral)
      '--muted': '0 0% 96%',
      '--muted-foreground': '0 0% 45%',
      
      // Accent
      '--accent': '271 81% 96%',             // Purple 50
      '--accent-foreground': '271 91% 65%',
      
      // Destructive (Error)
      '--destructive': '0 84% 60%',
      '--destructive-foreground': '0 0% 100%',
      
      // Border
      '--border': '0 0% 90%',
      '--input': '0 0% 90%',
      '--ring': '271 91% 65%',
      
      // Border radius
      '--radius': '0.5rem',
    },
    
    dark: {
      // Base colors
      '--background': '262 80% 5%',          // Deep purple black
      '--foreground': '0 0% 98%',
      
      // Card colors
      '--card': '262 50% 10%',
      '--card-foreground': '0 0% 98%',
      
      // Popover colors
      '--popover': '262 50% 10%',
      '--popover-foreground': '0 0% 98%',
      
      // Primary (Purple)
      '--primary': '271 91% 65%',
      '--primary-foreground': '0 0% 100%',
      
      // Secondary (Gold accent)
      '--secondary': '48 96% 53%',
      '--secondary-foreground': '262 80% 5%',
      
      // Muted (Neutral)
      '--muted': '262 30% 15%',
      '--muted-foreground': '0 0% 65%',
      
      // Accent
      '--accent': '271 50% 20%',
      '--accent-foreground': '0 0% 98%',
      
      // Destructive (Error)
      '--destructive': '0 84% 60%',
      '--destructive-foreground': '0 0% 100%',
      
      // Border
      '--border': '262 30% 20%',
      '--input': '262 30% 20%',
      '--ring': '271 91% 65%',
      
      // Border radius
      '--radius': '0.5rem',
    },
  },
  
  // Gradients
  gradients: {
    primary: 'linear-gradient(135deg, #9333ea 0%, #7e22ce 100%)',
    secondary: 'linear-gradient(135deg, #7e22ce 0%, #c026d3 100%)',
    accent: 'linear-gradient(90deg, #facc15 0%, #eab308 100%)',
    hero: 'linear-gradient(135deg, #c084fc 0%, #f472b6 50%, #fbbf24 100%)',
    surface: 'linear-gradient(180deg, #7e22ce 0%, #c026d3 50%, #facc15 100%)',
    subtle: 'linear-gradient(135deg, #faf5ff 0%, #f9fafb 100%)',
    glass: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
  },
  
  // Component-specific styles
  components: {
    button: {
      primary: {
        background: 'linear-gradient(135deg, #9333ea 0%, #7e22ce 100%)',
        hover: 'linear-gradient(135deg, #7e22ce 0%, #6b21a8 100%)',
        shadow: '0 4px 12px rgba(147, 51, 234, 0.3)',
        hoverShadow: '0 6px 20px rgba(147, 51, 234, 0.4)',
      },
      secondary: {
        border: designTokens.colors.neutral[300],
        hoverBackground: designTokens.colors.purple[50],
      },
    },
    
    card: {
      background: 'rgba(255, 255, 255, 0.98)',
      backdropFilter: 'blur(10px)',
      border: designTokens.colors.neutral[200],
      shadow: designTokens.shadows.md,
      hoverShadow: designTokens.shadows.lg,
    },
    
    input: {
      border: designTokens.colors.neutral[300],
      focusBorder: designTokens.colors.purple[600],
      focusRing: 'rgba(147, 51, 234, 0.2)',
    },
    
    table: {
      headerBackground: designTokens.colors.purple[50],
      hoverBackground: designTokens.colors.purple[25],
      border: designTokens.colors.neutral[200],
    },
  },
  
  // Glass morphism effects
  glass: {
    light: {
      background: 'rgba(255, 255, 255, 0.8)',
      border: 'rgba(255, 255, 255, 0.3)',
      backdropFilter: 'blur(12px) saturate(180%)',
    },
    dark: {
      background: 'rgba(26, 26, 36, 0.8)',
      border: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(12px) saturate(180%)',
    },
  },
};

export default purpleTheme;
