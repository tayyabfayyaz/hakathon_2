export interface User {
  id: string;
  email: string;
  name?: string;
  image?: string;
  created_at?: string;
  emailVerified?: boolean;
}

export interface Todo {
  id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  title: string;
  description?: string;
}

export interface TodoUpdate {
  title?: string;
  description?: string;
}

export interface TodoListResponse {
  items: Todo[];
  next_cursor: string | null;
  total_count: number;
}

export interface AuthResponse {
  user: User;
  message: string;
}

export interface ApiError {
  error_code: string;
  message: string;
  details?: {
    fields?: Array<{
      field: string;
      error: string;
    }>;
  };
}

export type StatusFilter = 'all' | 'completed' | 'remaining';
