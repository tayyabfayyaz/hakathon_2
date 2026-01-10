"use client";

import { useThemeContext } from "@/components/providers/theme-provider";

/**
 * Hook for accessing and controlling the application theme.
 * Must be used within a ThemeProvider.
 *
 * @returns {Object} Theme state and control functions
 * @returns {string} theme - Current theme ("light" | "dark")
 * @returns {Function} setTheme - Set theme to specific value
 * @returns {Function} toggleTheme - Toggle between light and dark
 * @returns {boolean} isDark - Convenience boolean for dark theme check
 * @returns {boolean} isLight - Convenience boolean for light theme check
 */
export function useTheme() {
  const { theme, setTheme, toggleTheme } = useThemeContext();

  return {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === "dark",
    isLight: theme === "light",
  };
}
