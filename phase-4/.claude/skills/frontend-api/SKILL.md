---
name: frontend-api
description: API integration patterns for the frontend using fetch, React Query, and proper error handling. Use when connecting to backend APIs, handling authentication, or managing server state.
argument-hint: "[endpoint]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# API Integration Patterns

Connect to the backend API using the established patterns in TodoList Pro.

## API Client Structure

```
frontend/src/lib/
├── api.ts           # Main API client (tasks, notifications, etc.)
├── chat-api.ts      # Chat/AI API client
└── auth-client.ts   # Better-Auth client
```

## Base API Client

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getAuthToken(): Promise<string | null> {
  return localStorage.getItem("bearer_token");
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("bearer_token");
      window.location.href = "/login";
    }
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      error.detail || "API Error",
      response.status,
      error
    );
  }

  return response.json();
}
```

## API Modules

### Tasks API

```typescript
// lib/api.ts
export const tasksApi = {
  getAll: () => fetchApi<Task[]>("/api/tasks"),

  create: (text: string) =>
    fetchApi<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  update: (id: string, data: Partial<Task>) =>
    fetchApi<Task>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    fetchApi<void>(`/api/tasks/${id}`, {
      method: "DELETE",
    }),

  toggle: (id: string) =>
    fetchApi<Task>(`/api/tasks/${id}/toggle`, {
      method: "POST",
    }),

  setDeadline: (id: string, deadline: string) =>
    fetchApi<Task>(`/api/tasks/${id}/deadline`, {
      method: "PUT",
      body: JSON.stringify({ deadline }),
    }),

  removeDeadline: (id: string) =>
    fetchApi<Task>(`/api/tasks/${id}/deadline`, {
      method: "DELETE",
    }),
};
```

### Chat API

```typescript
// lib/chat-api.ts
export const chatApi = {
  sendMessage: (content: string, inputMethod: "text" | "voice" = "text") =>
    fetchApi<ChatResponse>("/api/chat/message", {
      method: "POST",
      body: JSON.stringify({ content, input_method: inputMethod }),
    }),

  getHistory: () => fetchApi<ChatMessage[]>("/api/chat/history"),

  submitToolResult: (toolCallId: string, result: any) =>
    fetchApi<ChatResponse>("/api/chat/tool-result", {
      method: "POST",
      body: JSON.stringify({ tool_call_id: toolCallId, result }),
    }),
};
```

### Notifications API

```typescript
export const notificationsApi = {
  getAll: () => fetchApi<Notification[]>("/api/notifications"),

  getUnreadCount: () =>
    fetchApi<{ count: number }>("/api/notifications/unread-count"),

  markAsRead: (id: string) =>
    fetchApi<void>(`/api/notifications/${id}/read`, {
      method: "POST",
    }),

  markAllAsRead: () =>
    fetchApi<void>("/api/notifications/read-all", {
      method: "POST",
    }),

  dismiss: (id: string) =>
    fetchApi<void>(`/api/notifications/${id}`, {
      method: "DELETE",
    }),
};
```

## React Query Integration

```typescript
// hooks/use-tasks.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "@/lib/api";

// Query keys factory (prevents typos, enables type safety)
export const taskKeys = {
  all: ["tasks"] as const,
  detail: (id: string) => ["tasks", id] as const,
};

// Fetch query
export function useTasks() {
  return useQuery({
    queryKey: taskKeys.all,
    queryFn: tasksApi.getAll,
    staleTime: 30 * 1000,
    refetchOnWindowFocus: false,
  });
}

// Mutation with optimistic update
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: tasksApi.create,
    onMutate: async (text) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.all });
      const previous = queryClient.getQueryData<Task[]>(taskKeys.all);

      queryClient.setQueryData<Task[]>(taskKeys.all, (old = []) => [
        ...old,
        { id: `temp-${Date.now()}`, text, completed: false },
      ]);

      return { previous };
    },
    onError: (err, text, context) => {
      queryClient.setQueryData(taskKeys.all, context?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}
```

## Query Client Configuration

```typescript
// lib/query-client.ts
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: (failureCount, error: any) => {
        if (error?.status === 401 || error?.status === 403) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      retry: false,
    },
  },
});
```

## Authentication Flow

```typescript
// Get bearer token after login
async function fetchBearerToken(): Promise<string | null> {
  try {
    const response = await fetch("/api/auth/token", {
      method: "POST",
      credentials: "include",
    });
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem("bearer_token", data.token);
      return data.token;
    }
  } catch (error) {
    console.error("Failed to get token:", error);
  }
  return null;
}
```

## Error Handling

```typescript
// In components
const { data, isLoading, error } = useTasks();

if (isLoading) return <Skeleton />;
if (error) return <ErrorMessage message={error.message} />;

// In mutations
const mutation = useCreateTask();

const handleSubmit = async (text: string) => {
  try {
    await mutation.mutateAsync(text);
    toast.success("Task created!");
  } catch (error) {
    if (error instanceof ApiError) {
      toast.error(error.message);
    }
  }
};
```

## Type Definitions

```typescript
// types/index.ts
export interface Task {
  id: string;
  text: string;
  completed: boolean;
  deadline?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  inputMethod?: "text" | "voice";
  createdAt: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
}
```

## Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```
