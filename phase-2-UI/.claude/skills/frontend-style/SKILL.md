---
name: frontend-style
description: Styling with Tailwind CSS 4, shadcn/ui components, themes, and dark mode. Use when styling components, implementing dark mode, or following the design system.
argument-hint: "[element]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Styling Guide - Tailwind CSS + shadcn/ui

Style components following the TodoList Pro design system.

## Tech Stack

- **Tailwind CSS 4** with PostCSS
- **shadcn/ui** components (New York style)
- **OKLch color space** for modern colors
- **CSS variables** for theming
- **Dark mode** with class strategy

## Color System

Colors are defined as CSS variables in `globals.css`:

```css
:root {
  --background: oklch(100% 0 0);
  --foreground: oklch(14.9% 0.028 264.8);
  --primary: oklch(60.2% 0.09 286.6);
  --primary-foreground: oklch(100% 0 0);
  --secondary: oklch(96.4% 0.006 264.8);
  --muted: oklch(96.4% 0.006 264.8);
  --accent: oklch(96.4% 0.006 264.8);
  --destructive: oklch(57.7% 0.245 27.3);
  --border: oklch(90.6% 0.013 264.8);
  --input: oklch(90.6% 0.013 264.8);
  --ring: oklch(60.2% 0.09 286.6);
  --radius: 0.625rem;
}

.dark {
  --background: oklch(14.9% 0.028 264.8);
  --foreground: oklch(98.4% 0.003 264.8);
  /* ... dark mode colors */
}
```

## Using Colors

```typescript
// Use semantic color classes
className="bg-background text-foreground"
className="bg-primary text-primary-foreground"
className="bg-muted text-muted-foreground"
className="bg-destructive text-destructive-foreground"
className="border-border"
className="ring-ring"
```

## Utility Function: cn()

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage
className={cn(
  "base-classes",
  condition && "conditional-classes",
  className // Allow override
)}
```

## Component Styling Patterns

### Card

```typescript
<div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6">
  <h3 className="text-lg font-semibold">Title</h3>
  <p className="text-muted-foreground">Description</p>
</div>
```

### Button Variants

```typescript
// Primary (default)
<Button>Click me</Button>

// Secondary
<Button variant="secondary">Secondary</Button>

// Ghost (transparent)
<Button variant="ghost">Ghost</Button>

// Outline
<Button variant="outline">Outline</Button>

// Destructive
<Button variant="destructive">Delete</Button>

// Icon button
<Button variant="ghost" size="icon">
  <X className="h-4 w-4" />
</Button>
```

### Form Inputs

```typescript
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    type="email"
    placeholder="you@example.com"
    className={cn(
      hasError && "border-destructive focus-visible:ring-destructive"
    )}
  />
  {hasError && (
    <p className="text-sm text-destructive">Error message</p>
  )}
</div>
```

### Spacing

```typescript
// Vertical spacing
<div className="space-y-4">...</div>

// Horizontal spacing
<div className="space-x-2">...</div>

// Flex gap
<div className="flex gap-4">...</div>

// Grid gap
<div className="grid gap-6">...</div>
```

### Typography

```typescript
// Headings
<h1 className="text-3xl font-bold tracking-tight">Page Title</h1>
<h2 className="text-2xl font-semibold">Section Title</h2>
<h3 className="text-lg font-medium">Subsection</h3>

// Body text
<p className="text-muted-foreground">Secondary text</p>
<p className="text-sm text-muted-foreground">Small text</p>

// Links
<a className="text-primary hover:underline">Link text</a>
```

## Dark Mode

### Theme Provider

```typescript
// components/theme-provider.tsx
"use client";

import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (theme: Theme) => void;
}>({
  theme: "system",
  setTheme: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme;
    if (stored) setTheme(stored);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }

    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
```

### Theme Toggle

```typescript
"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/components/theme-provider";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
```

## Animations

### Framer Motion

```typescript
import { motion, AnimatePresence } from "framer-motion";

// Fade in
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
>
  Content
</motion.div>

// Slide up
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Content
</motion.div>

// List animations
<AnimatePresence>
  {items.map((item) => (
    <motion.div
      key={item.id}
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
    >
      {item.content}
    </motion.div>
  ))}
</AnimatePresence>
```

### Tailwind Animations

```typescript
// Spin
<Loader2 className="h-4 w-4 animate-spin" />

// Pulse
<div className="animate-pulse bg-muted h-4 w-32 rounded" />

// Custom keyframes (in globals.css)
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// Usage
className="animate-[fadeIn_0.3s_ease-out]"
```

## Responsive Design

```typescript
// Mobile first approach
<div className="
  grid
  grid-cols-1
  md:grid-cols-2
  lg:grid-cols-3
  gap-4
">

// Hide/show on breakpoints
<div className="hidden md:block">Desktop only</div>
<div className="block md:hidden">Mobile only</div>

// Responsive text
<h1 className="text-2xl md:text-3xl lg:text-4xl">Title</h1>

// Responsive padding
<div className="p-4 md:p-6 lg:p-8">Content</div>
```

## Loading States

### Skeleton

```typescript
import { Skeleton } from "@/components/ui/skeleton";

// Text skeleton
<Skeleton className="h-4 w-[250px]" />

// Avatar skeleton
<Skeleton className="h-12 w-12 rounded-full" />

// Card skeleton
<div className="space-y-3">
  <Skeleton className="h-4 w-[250px]" />
  <Skeleton className="h-4 w-[200px]" />
  <Skeleton className="h-4 w-[150px]" />
</div>
```

### Loading Spinner

```typescript
import { Loader2 } from "lucide-react";

<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Loading...
</Button>
```

## Best Practices

1. **Use cn()** for conditional classes
2. **Prefer semantic colors** (primary, muted, destructive)
3. **Mobile-first** responsive design
4. **Use CSS variables** for customization
5. **Consistent spacing** with Tailwind scale
6. **Focus states** for accessibility
7. **Loading states** for async operations
