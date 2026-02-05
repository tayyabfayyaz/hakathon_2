"use client";

import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";

interface ThemeToggleProps {
  variant?: "ghost" | "outline" | "default";
  size?: "default" | "sm" | "lg" | "icon";
  showLabel?: boolean;
  className?: string;
}

export function ThemeToggle({
  variant = "ghost",
  size = "icon",
  showLabel = false,
  className,
}: ThemeToggleProps) {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <Button
      variant={variant}
      size={size}
      onClick={toggleTheme}
      className={className}
      aria-label={`Switch to ${isDark ? "light" : "dark"} theme`}
      title={`Switch to ${isDark ? "light" : "dark"} theme`}
    >
      {isDark ? (
        <>
          <Sun className="h-5 w-5" />
          {showLabel && <span className="ml-2">Light Mode</span>}
        </>
      ) : (
        <>
          <Moon className="h-5 w-5" />
          {showLabel && <span className="ml-2">Dark Mode</span>}
        </>
      )}
      <span className="sr-only">
        {isDark ? "Switch to light theme" : "Switch to dark theme"}
      </span>
    </Button>
  );
}
