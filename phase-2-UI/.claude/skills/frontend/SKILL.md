---
name: frontend
description: Frontend development for Next.js 16 + React 19 + TypeScript application. Use when working on UI, components, pages, styling, or any frontend code. Covers shadcn/ui, Tailwind CSS 4, React Query, and project conventions.
argument-hint: "[task]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Frontend Development Guide

This skill provides guidance for developing the TodoList Pro frontend application.

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.1.1 | React framework with App Router |
| React | 19.2.3 | UI library |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 4 | Utility-first styling |
| shadcn/ui | Latest | Component library (Radix UI) |
| React Query | 5.90.16 | Server state management |
| react-hook-form | 7.69.0 | Form handling |
| Zod | 4.2.1 | Schema validation |
| Framer Motion | 12.23.26 | Animations |
| Better-Auth | 1.4.10 | Authentication |

## Project Structure

```
frontend/src/
├── app/                    # Next.js App Router
│   ├── (marketing)/        # Public pages
│   ├── (auth)/             # Login/Register
│   ├── (dashboard)/        # Protected routes
│   └── api/                # API routes
├── components/             # React components
│   ├── ui/                 # shadcn/ui primitives
│   ├── tasks/              # Task-related components
│   ├── chat/               # AI chat components
│   ├── notifications/      # Notification components
│   └── landing/            # Marketing page components
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities & API clients
│   ├── api.ts              # Main API client
│   ├── chat-api.ts         # Chat API
│   ├── validators.ts       # Zod schemas
│   └── utils.ts            # Utility functions
├── types/                  # TypeScript definitions
└── middleware.ts           # Route protection
```

## Key Conventions

### Component Creation

```typescript
// Use "use client" for interactive components
"use client";

import { cn } from "@/lib/utils";

interface ComponentProps {
  className?: string;
  children: React.ReactNode;
}

export function Component({ className, children }: ComponentProps) {
  return (
    <div className={cn("base-styles", className)}>
      {children}
    </div>
  );
}
```

### Import Patterns

```typescript
// Path alias for clean imports
import { Button } from "@/components/ui/button";
import { useTasks } from "@/hooks/use-tasks";
import { cn } from "@/lib/utils";
import type { Task } from "@/types";
```

### Styling with Tailwind

```typescript
// Use cn() for conditional classes
className={cn(
  "base-class",
  variant === "primary" && "primary-styles",
  className
)}
```

### React Query Pattern

```typescript
// Query with proper keys
const { data, isLoading } = useQuery({
  queryKey: ["tasks"],
  queryFn: () => tasksApi.getAll(),
  staleTime: 30 * 1000,
});

// Mutation with optimistic update
const mutation = useMutation({
  mutationFn: tasksApi.create,
  onMutate: async (newTask) => {
    await queryClient.cancelQueries({ queryKey: ["tasks"] });
    const previous = queryClient.getQueryData(["tasks"]);
    queryClient.setQueryData(["tasks"], (old) => [...old, newTask]);
    return { previous };
  },
  onError: (err, vars, context) => {
    queryClient.setQueryData(["tasks"], context?.previous);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ["tasks"] });
  },
});
```

## Development Commands

```bash
cd frontend
npm run dev      # Start dev server (port 3000)
npm run build    # Production build
npm run lint     # ESLint check
npm run start    # Start production server
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
```

## Additional Skills

- **frontend-component**: Create new components
- **frontend-hook**: Create custom hooks
- **frontend-api**: API integration
- **frontend-form**: Forms with validation
- **frontend-auth**: Authentication patterns
- **frontend-style**: Styling guidelines
