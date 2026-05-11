import React, { createContext, useContext, useEffect } from 'react';
import purple from './purple';
import blue from './blue';

const themeMap = {
  purple,
  blue,
};

const ThemeContext = createContext('purple');

export function ThemeProvider({ children }) {
  const themeName = (process.env.REACT_APP_THEME || 'purple').toLowerCase();
  const tokens = themeMap[themeName] || themeMap.purple;

  useEffect(() => {
    const root = document.documentElement;
    Object.entries(tokens).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
  }, [tokens]);

  return (
    <ThemeContext.Provider value={themeName}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
