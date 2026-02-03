// Thai Airways theme configuration
export const thaiAirwaysTheme = {
  colors: {
    primary: {
      main: '#5D1F8A',      // Royal Purple
      light: '#9B59B6',     // Light Purple
      dark: '#3D0066',      // Deep Purple
      vibrant: '#8B3FBF',   // Vibrant Purple
      gradient: 'linear-gradient(135deg, #5D1F8A 0%, #9B59B6 50%, #C77DFF 100%)',
      gradientReverse: 'linear-gradient(135deg, #C77DFF 0%, #9B59B6 50%, #5D1F8A 100%)',
    },
    secondary: {
      main: '#D4AF37',      // Gold
      light: '#FFD700',     // Light Gold
      dark: '#B8860B',      // Dark Gold
      vibrant: '#FFA500',   // Orange Gold
      gradient: 'linear-gradient(135deg, #D4AF37 0%, #FFD700 50%, #FFA500 100%)',
      gradientReverse: 'linear-gradient(135deg, #FFA500 0%, #FFD700 50%, #D4AF37 100%)',
    },
    accent: {
      blue: '#4A90E2',      // Sky Blue
      cyan: '#00D4FF',      // Cyan
      pink: '#FF6B9D',      // Pink
      coral: '#FF7E67',     // Coral
      teal: '#00B8A9',      // Teal
      lavender: '#C7CEEA',  // Lavender
    },
    glass: {
      white: 'rgba(255, 255, 255, 0.15)',
      purple: 'rgba(93, 31, 138, 0.2)',
      gold: 'rgba(212, 175, 55, 0.35)',
      blue: 'rgba(74, 144, 226, 0.2)',
      pink: 'rgba(255, 107, 157, 0.2)',
      background: 'rgba(255, 255, 255, 0.08)',
      border: 'rgba(255, 255, 255, 0.25)',
    },
    gradient: {
      purpleGold: 'linear-gradient(135deg, #5D1F8A 0%, #9B59B6 30%, #D4AF37 70%, #FFD700 100%)',
      goldPurple: 'linear-gradient(135deg, #FFD700 0%, #D4AF37 30%, #9B59B6 70%, #5D1F8A 100%)',
      darkPurple: 'linear-gradient(180deg, #3D0066 0%, #5D1F8A 50%, #8B3FBF 100%)',
      rainbow: 'linear-gradient(135deg, #5D1F8A 0%, #9B59B6 20%, #4A90E2 40%, #00D4FF 60%, #FFD700 80%, #FFA500 100%)',
      sunset: 'linear-gradient(135deg, #FF6B9D 0%, #FFA500 50%, #FFD700 100%)',
      ocean: 'linear-gradient(135deg, #00D4FF 0%, #4A90E2 50%, #5D1F8A 100%)',
      royal: 'linear-gradient(135deg, #3D0066 0%, #5D1F8A 25%, #9B59B6 50%, #D4AF37 75%, #FFD700 100%)',
    },
    background: {
      main: 'linear-gradient(135deg, #F5F0FF 0%, #FFF8E7 50%, #F0F8FF 100%)',
      paper: 'rgba(255, 255, 255, 0.98)',
      overlay: 'radial-gradient(circle at 20% 50%, rgba(93, 31, 138, 0.1), transparent 50%), radial-gradient(circle at 80% 80%, rgba(212, 175, 55, 0.08), transparent 50%)',
    },
    text: {
      primary: '#2C1A3D',
      secondary: 'rgba(44, 26, 61, 0.75)',
      gold: '#B8860B',
      white: '#FFFFFF',
    },
  },
  glass: {
    background: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(20px) saturate(180%)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    boxShadow: '0 8px 32px rgba(93, 31, 138, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.1) inset',
    borderRadius: '20px',
  },
  glassDark: {
    background: 'linear-gradient(135deg, rgba(93, 31, 138, 0.25) 0%, rgba(61, 0, 102, 0.3) 100%)',
    backdropFilter: 'blur(20px) saturate(180%)',
    border: '1px solid rgba(155, 89, 182, 0.4)',
    boxShadow: '0 8px 32px rgba(93, 31, 138, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.1) inset',
    borderRadius: '24px',
  },
  glassGold: {
    background: 'linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(255, 215, 0, 0.25) 100%)',
    backdropFilter: 'blur(15px) saturate(180%)',
    border: '1px solid rgba(212, 175, 55, 0.5)',
    boxShadow: '0 8px 32px rgba(212, 175, 55, 0.3), 0 0 20px rgba(255, 215, 0, 0.2)',
    borderRadius: '20px',
  },
  glassBlue: {
    background: 'linear-gradient(135deg, rgba(74, 144, 226, 0.2) 0%, rgba(0, 212, 255, 0.25) 100%)',
    backdropFilter: 'blur(15px) saturate(180%)',
    border: '1px solid rgba(74, 144, 226, 0.4)',
    boxShadow: '0 8px 32px rgba(74, 144, 226, 0.25), 0 0 20px rgba(0, 212, 255, 0.15)',
    borderRadius: '20px',
  },
  glassPink: {
    background: 'linear-gradient(135deg, rgba(255, 107, 157, 0.2) 0%, rgba(255, 126, 103, 0.25) 100%)',
    backdropFilter: 'blur(15px) saturate(180%)',
    border: '1px solid rgba(255, 107, 157, 0.4)',
    boxShadow: '0 8px 32px rgba(255, 107, 157, 0.25), 0 0 20px rgba(255, 126, 103, 0.15)',
    borderRadius: '20px',
  },
  animations: {
    shimmer: `
      @keyframes shimmer {
        0% { 
          background-position: -1000px 0;
          opacity: 0.5;
        }
        50% {
          opacity: 1;
        }
        100% { 
          background-position: 1000px 0;
          opacity: 0.5;
        }
      }
    `,
    glow: `
      @keyframes glow {
        0%, 100% { 
          box-shadow: 0 0 20px rgba(212, 175, 55, 0.5),
                      0 0 40px rgba(212, 175, 55, 0.3);
        }
        50% { 
          box-shadow: 0 0 30px rgba(212, 175, 55, 0.8),
                      0 0 60px rgba(212, 175, 55, 0.5),
                      0 0 80px rgba(255, 215, 0, 0.3);
        }
      }
    `,
    float: `
      @keyframes float {
        0%, 100% { 
          transform: translateY(0px);
        }
        50% { 
          transform: translateY(-15px);
        }
      }
    `,
    pulse: `
      @keyframes pulse {
        0%, 100% { 
          opacity: 1;
          transform: scale(1);
        }
        50% { 
          opacity: 0.8;
          transform: scale(1.05);
        }
      }
    `,
    gradientShift: `
      @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
    `,
    rainbowBorder: `
      @keyframes rainbowBorder {
        0% { border-color: #5D1F8A; }
        25% { border-color: #4A90E2; }
        50% { border-color: #FFD700; }
        75% { border-color: #FF6B9D; }
        100% { border-color: #5D1F8A; }
      }
    `,
    slideIn: `
      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateX(-30px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
    `,
  },
};

export const glassStyle = {
  background: thaiAirwaysTheme.glass.background,
  backdropFilter: thaiAirwaysTheme.glass.backdropFilter,
  border: thaiAirwaysTheme.glass.border,
  boxShadow: thaiAirwaysTheme.glass.boxShadow,
  borderRadius: thaiAirwaysTheme.glass.borderRadius,
};

export const glassDarkStyle = {
  background: thaiAirwaysTheme.glassDark.background,
  backdropFilter: thaiAirwaysTheme.glassDark.backdropFilter,
  border: thaiAirwaysTheme.glassDark.border,
  boxShadow: thaiAirwaysTheme.glassDark.boxShadow,
  borderRadius: thaiAirwaysTheme.glassDark.borderRadius,
};

export const glassGoldStyle = {
  background: thaiAirwaysTheme.glassGold.background,
  backdropFilter: thaiAirwaysTheme.glassGold.backdropFilter,
  border: thaiAirwaysTheme.glassGold.border,
  boxShadow: thaiAirwaysTheme.glassGold.boxShadow,
  borderRadius: thaiAirwaysTheme.glassGold.borderRadius,
};

export const glassBlueStyle = {
  background: thaiAirwaysTheme.glassBlue.background,
  backdropFilter: thaiAirwaysTheme.glassBlue.backdropFilter,
  border: thaiAirwaysTheme.glassBlue.border,
  boxShadow: thaiAirwaysTheme.glassBlue.boxShadow,
  borderRadius: thaiAirwaysTheme.glassBlue.borderRadius,
};

export const glassPinkStyle = {
  background: thaiAirwaysTheme.glassPink.background,
  backdropFilter: thaiAirwaysTheme.glassPink.backdropFilter,
  border: thaiAirwaysTheme.glassPink.border,
  boxShadow: thaiAirwaysTheme.glassPink.boxShadow,
  borderRadius: thaiAirwaysTheme.glassPink.borderRadius,
};
