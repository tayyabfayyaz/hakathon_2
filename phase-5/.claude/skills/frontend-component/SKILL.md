---
name: frontend-component
description: Create React components following shadcn/ui patterns and project conventions. Use when building new UI components, creating reusable elements, or adding interactive features.
argument-hint: "[component-name]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# React Component Creation

Create components following the TodoList Pro conventions using shadcn/ui patterns.

## Component Template

```typescript
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface $ARGUMENTS[0]Props extends React.HTMLAttributes<HTMLDivElement> {
  // Add custom props
}

const $ARGUMENTS[0] = React.forwardRef<HTMLDivElement, $ARGUMENTS[0]Props>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("", className)}
        {...props}
      />
    );
  }
);
$ARGUMENTS[0].displayName = "$ARGUMENTS[0]";

export { $ARGUMENTS[0] };
```

## Component Types

### 1. UI Primitives (`/components/ui/`)

shadcn/ui style components built on Radix UI:

```typescript
// Example: Badge component
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        secondary: "bg-secondary text-secondary-foreground",
        destructive: "bg-destructive text-destructive-foreground",
        outline: "border border-input",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
```

### 2. Feature Components (`/components/[feature]/`)

Domain-specific components:

```typescript
// Example: TaskItem component
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Trash2, Edit2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Task } from "@/types";

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string, text: string) => void;
}

export function TaskItem({ task, onToggle, onDelete, onEdit }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg border",
        task.completed && "opacity-60"
      )}
    >
      <Checkbox
        checked={task.completed}
        onCheckedChange={() => onToggle(task.id)}
      />
      <span className={cn(task.completed && "line-through")}>
        {task.text}
      </span>
      <div className="ml-auto flex gap-2">
        <Button variant="ghost" size="icon" onClick={() => setIsEditing(true)}>
          <Edit2 className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" onClick={() => onDelete(task.id)}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </motion.div>
  );
}
```

### 3. Layout Components

Page layouts and containers:

```typescript
// Example: PageHeader
interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between pb-4 border-b">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {description && (
          <p className="text-muted-foreground">{description}</p>
        )}
      </div>
      {actions && <div className="flex gap-2">{actions}</div>}
    </div>
  );
}
```

## Existing UI Components

Available in `/components/ui/`:
- `Avatar` - User avatars with fallback
- `Button` - Buttons with variants
- `Card` - Content containers
- `Checkbox` - Checkboxes
- `Dialog` - Modal dialogs
- `Input` - Text inputs
- `Label` - Form labels
- `Popover` - Dropdown popovers
- `Calendar` - Date picker
- `Sheet` - Mobile sidebars
- `Separator` - Dividers
- `Skeleton` - Loading placeholders

## Animation Patterns

```typescript
import { motion, AnimatePresence } from "framer-motion";

// List animations
<AnimatePresence>
  {items.map((item) => (
    <motion.div
      key={item.id}
      layout
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.2 }}
    >
      {/* content */}
    </motion.div>
  ))}
</AnimatePresence>
```

## Icon Usage

```typescript
import { Check, X, Plus, Trash2, Edit2, Calendar } from "lucide-react";

// Standard icon sizing
<Check className="h-4 w-4" />
<Plus className="h-5 w-5" />
```

## File Locations

- UI primitives: `frontend/src/components/ui/`
- Task components: `frontend/src/components/tasks/`
- Chat components: `frontend/src/components/chat/`
- Notification components: `frontend/src/components/notifications/`
- Landing components: `frontend/src/components/landing/`
