// User types (aligned with Better-Auth)
export interface User {
  id: string;
  name: string;
  email: string;
  emailVerified: boolean;
  image?: string | null;
  createdAt: Date;
  updatedAt: Date;
}

// Task types (aligned with FastAPI backend)
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

// Frontend Task type (camelCase for UI components)
export interface TaskUI {
  id: string;
  userId: string;
  text: string;
  completed: boolean;
  createdAt: Date;
  updatedAt: Date;
  completedAt: Date | null;
  order: number;
}

// Task API types
export interface TaskCreate {
  text: string;
}

export interface TaskUpdate {
  text?: string;
  completed?: boolean;
}

export interface TaskPatch {
  text?: string;
  completed?: boolean;
}

// Session types (aligned with Better-Auth)
export interface Session {
  id: string;
  userId: string;
  token: string;
  expiresAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

// Form types
export interface RegistrationFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface TaskFormData {
  text: string;
}

// Auth state
export interface AuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

// API Response types
export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}

// Toast types
export interface Toast {
  id: string;
  type: "success" | "error" | "info" | "warning";
  title: string;
  description?: string;
  duration?: number;
}

// Utility function to convert backend Task to UI Task
export function toTaskUI(task: Task): TaskUI {
  return {
    id: task.id,
    userId: task.user_id,
    text: task.text,
    completed: task.completed,
    order: task.order,
    createdAt: new Date(task.created_at),
    updatedAt: new Date(task.updated_at),
    completedAt: task.completed_at ? new Date(task.completed_at) : null,
  };
}
