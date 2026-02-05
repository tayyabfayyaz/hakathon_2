---
name: frontend-form
description: Create forms with react-hook-form and Zod validation. Use when building login forms, registration, input fields, or any form with validation.
argument-hint: "[form-name]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Form Creation with react-hook-form + Zod

Build type-safe, validated forms following TodoList Pro patterns.

## Dependencies

```json
{
  "react-hook-form": "^7.69.0",
  "zod": "^4.2.1",
  "@hookform/resolvers": "^5.0.1"
}
```

## Form Template

```typescript
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

// 1. Define schema
const formSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormData = z.infer<typeof formSchema>;

// 2. Create component
export function MyForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = async (data: FormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          {...register("email")}
          className={errors.email ? "border-destructive" : ""}
        />
        {errors.email && (
          <p className="text-sm text-destructive">{errors.email.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          {...register("password")}
          className={errors.password ? "border-destructive" : ""}
        />
        {errors.password && (
          <p className="text-sm text-destructive">{errors.password.message}</p>
        )}
      </div>

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Submitting..." : "Submit"}
      </Button>
    </form>
  );
}
```

## Validation Schemas

### Login Schema

```typescript
// lib/validators.ts
export const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean().optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;
```

### Registration Schema

```typescript
export const registerSchema = z
  .object({
    name: z
      .string()
      .min(2, "Name must be at least 2 characters")
      .max(50, "Name cannot exceed 50 characters"),
    email: z.string().email("Please enter a valid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
      .regex(/[a-z]/, "Password must contain at least one lowercase letter")
      .regex(/[0-9]/, "Password must contain at least one number"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

export type RegisterFormData = z.infer<typeof registerSchema>;
```

### Task Schema

```typescript
export const taskSchema = z.object({
  text: z
    .string()
    .min(1, "Task cannot be empty")
    .max(500, "Task cannot exceed 500 characters"),
  deadline: z.string().datetime().optional(),
});

export type TaskFormData = z.infer<typeof taskSchema>;
```

## Form Examples

### Login Form

```typescript
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { loginSchema, type LoginFormData } from "@/lib/validators";
import { authClient } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";

export function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null);
    try {
      await authClient.signIn.email({
        email: data.email,
        password: data.password,
      });
      window.location.href = "/dashboard";
    } catch (error: any) {
      setServerError(error.message || "Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {serverError && (
        <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          {serverError}
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          {...register("email")}
        />
        {errors.email && (
          <p className="text-sm text-destructive">{errors.email.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            {...register("password")}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-0 top-0"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </Button>
        </div>
        {errors.password && (
          <p className="text-sm text-destructive">{errors.password.message}</p>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox id="rememberMe" {...register("rememberMe")} />
        <Label htmlFor="rememberMe" className="text-sm">
          Remember me
        </Label>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Signing in...
          </>
        ) : (
          "Sign in"
        )}
      </Button>
    </form>
  );
}
```

### Inline Task Input

```typescript
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { taskSchema, type TaskFormData } from "@/lib/validators";
import { useCreateTask } from "@/hooks/use-tasks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function TaskInput() {
  const createTask = useCreateTask();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  });

  const onSubmit = async (data: TaskFormData) => {
    await createTask.mutateAsync(data.text);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex gap-2">
      <div className="flex-1">
        <Input
          placeholder="Add a new task..."
          {...register("text")}
          className={errors.text ? "border-destructive" : ""}
        />
      </div>
      <Button type="submit" disabled={createTask.isPending}>
        <Plus className="h-4 w-4" />
      </Button>
    </form>
  );
}
```

## Form Styling

```typescript
// Error input styling
className={cn(
  "border-input",
  errors.fieldName && "border-destructive focus-visible:ring-destructive"
)}

// Error message
<p className="text-sm text-destructive mt-1">
  {errors.fieldName?.message}
</p>

// Loading button
<Button disabled={isSubmitting}>
  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  {isSubmitting ? "Submitting..." : "Submit"}
</Button>
```

## Best Practices

1. **Define schemas in `lib/validators.ts`** for reuse
2. **Export inferred types** with `z.infer<typeof schema>`
3. **Show loading states** during submission
4. **Display server errors** separately from validation errors
5. **Reset form** after successful submission
6. **Use controlled inputs** for complex interactions
7. **Add aria attributes** for accessibility
