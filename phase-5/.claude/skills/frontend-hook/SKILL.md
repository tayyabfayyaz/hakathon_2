---
name: frontend-hook
description: Create custom React hooks for data fetching, state management, and reusable logic. Use when building hooks with React Query, managing side effects, or extracting reusable logic.
argument-hint: "[hook-name]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Custom React Hooks

Create hooks following the TodoList Pro patterns with React Query and TypeScript.

## Hook Template

```typescript
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useCallback } from "react";

export function use$ARGUMENTS[0]() {
  // Implementation
}
```

## Hook Patterns

### 1. Data Fetching Hook (React Query)

```typescript
// hooks/use-tasks.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "@/lib/api";
import type { Task } from "@/types";

// Query key factory
const taskKeys = {
  all: ["tasks"] as const,
  detail: (id: string) => ["tasks", id] as const,
};

export function useTasks() {
  return useQuery({
    queryKey: taskKeys.all,
    queryFn: () => tasksApi.getAll(),
    staleTime: 30 * 1000,
    refetchOnWindowFocus: false,
    retry: (failureCount, error: any) => {
      if (error?.status === 401 || error?.status === 403) return false;
      return failureCount < 3;
    },
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (text: string) => tasksApi.create(text),
    onMutate: async (newText) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskKeys.all });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.all);

      // Optimistically update
      queryClient.setQueryData<Task[]>(taskKeys.all, (old = []) => [
        ...old,
        {
          id: `temp-${Date.now()}`,
          text: newText,
          completed: false,
          createdAt: new Date().toISOString(),
        },
      ]);

      return { previousTasks };
    },
    onError: (err, newText, context) => {
      // Rollback on error
      queryClient.setQueryData(taskKeys.all, context?.previousTasks);
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}
```

### 2. State Management Hook

```typescript
// hooks/use-toggle.ts
import { useState, useCallback } from "react";

export function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => setValue((v) => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return { value, toggle, setTrue, setFalse };
}
```

### 3. Local Storage Hook

```typescript
// hooks/use-local-storage.ts
import { useState, useEffect } from "react";

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(key, JSON.stringify(storedValue));
    }
  }, [key, storedValue]);

  return [storedValue, setStoredValue] as const;
}
```

### 4. WebSocket Hook

```typescript
// hooks/use-notification-websocket.ts
import { useEffect, useCallback, useRef } from "react";

export function useNotificationWebSocket(onMessage: (data: any) => void) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    const token = localStorage.getItem("bearer_token");
    if (!token) return;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL;
    wsRef.current = new WebSocket(`${wsUrl}?token=${token}`);

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    wsRef.current.onclose = () => {
      if (reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.pow(2, reconnectAttempts.current) * 1000;
        setTimeout(() => {
          reconnectAttempts.current++;
          connect();
        }, delay);
      }
    };

    wsRef.current.onopen = () => {
      reconnectAttempts.current = 0;
    };
  }, [onMessage]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);
}
```

### 5. Form Hook

```typescript
// hooks/use-form-with-validation.ts
import { useForm, UseFormProps } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

export function useFormWithValidation<T extends z.ZodType>(
  schema: T,
  options?: Omit<UseFormProps<z.infer<T>>, "resolver">
) {
  return useForm<z.infer<T>>({
    resolver: zodResolver(schema),
    ...options,
  });
}
```

### 6. Speech Recognition Hook

```typescript
// hooks/use-speech-recognition.ts
import { useState, useCallback, useRef, useEffect } from "react";

interface SpeechRecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
}

export function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const startListening = useCallback(() => {
    if (!("webkitSpeechRecognition" in window)) {
      setError("Speech recognition not supported");
      return;
    }

    const SpeechRecognition = window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = true;

    recognitionRef.current.onresult = (event) => {
      const result = event.results[event.results.length - 1];
      setTranscript(result[0].transcript);
    };

    recognitionRef.current.onend = () => setIsListening(false);
    recognitionRef.current.onerror = (e) => setError(e.error);

    recognitionRef.current.start();
    setIsListening(true);
  }, []);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  return { isListening, transcript, error, startListening, stopListening };
}
```

## Existing Hooks

Located in `frontend/src/hooks/`:

| Hook | Purpose |
|------|---------|
| `useTasks` | Task CRUD operations |
| `useCreateTask` | Create task with optimistic update |
| `useToggleTask` | Toggle task completion |
| `useUpdateTask` | Update task text |
| `useDeleteTask` | Delete task |
| `useSetDeadline` | Set task deadline |
| `useRemoveDeadline` | Clear task deadline |
| `useChat` | Chat conversation management |
| `useSpeechRecognition` | Voice input handling |
| `useNotifications` | Fetch notifications |
| `useUnreadCount` | Get unread count |
| `useMarkAsRead` | Mark notification read |
| `useAuth` | Authentication state |

## Best Practices

1. **Prefix with `use`**: All hooks must start with `use`
2. **Single responsibility**: One hook, one purpose
3. **Return objects for multiple values**: Easier to destructure
4. **Memoize callbacks**: Use `useCallback` for functions
5. **Handle loading/error states**: Always expose these states
6. **TypeScript generics**: Make hooks reusable with generics
