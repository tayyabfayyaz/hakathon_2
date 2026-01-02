const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public data: { detail?: string; [key: string]: unknown }
  ) {
    super(data.detail || "An error occurred");
    this.name = "ApiError";
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("bearer_token") : null;

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Unknown error" }));

    // Handle session expiry - don't auto-redirect, let components handle it
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("bearer_token");
      }
    }

    throw new ApiError(response.status, error);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Task API functions
export interface TaskCreate {
  text: string;
}

export interface TaskUpdate {
  text?: string;
  completed?: boolean;
}

export interface Task {
  id: string;
  user_id: string;
  text: string;
  completed: boolean;
  order: number;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

export const tasksApi = {
  getAll: async (): Promise<Task[]> => {
    const response = await apiClient<TaskListResponse>("/tasks");
    return response.tasks;
  },

  getById: (id: string) => apiClient<Task>(`/tasks/${id}`),

  create: (data: TaskCreate) =>
    apiClient<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: TaskUpdate) =>
    apiClient<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiClient<void>(`/tasks/${id}`, {
      method: "DELETE",
    }),

  toggle: (id: string, completed: boolean) =>
    apiClient<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    }),
};
