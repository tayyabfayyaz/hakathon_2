'use client';

import { useState, useCallback, useEffect } from 'react';
import { api, ApiException } from '@/lib/api';
import type { Todo, TodoCreate, TodoUpdate, TodoListResponse, StatusFilter } from '@/types';

export interface UseTodosReturn {
  todos: Todo[];
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  searchQuery: string;
  statusFilter: StatusFilter;
  fetchTodos: () => Promise<void>;
  createTodo: (data: TodoCreate) => Promise<boolean>;
  updateTodo: (id: string, data: TodoUpdate) => Promise<boolean>;
  deleteTodo: (id: string) => Promise<boolean>;
  toggleTodo: (id: string) => Promise<boolean>;
  setSearchQuery: (query: string) => void;
  setStatusFilter: (filter: StatusFilter) => void;
  clearError: () => void;
}

export function useTodos(): UseTodosReturn {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const fetchTodos = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      if (statusFilter !== 'all') {
        params.append('status', statusFilter);
      }

      const queryString = params.toString();
      const endpoint = `/todos${queryString ? `?${queryString}` : ''}`;

      const response = await api.get<TodoListResponse>(endpoint);
      setTodos(response.items);
      setTotalCount(response.total_count);
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.error.message);
      } else {
        setError('Failed to fetch todos');
      }
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, statusFilter]);

  const createTodo = useCallback(async (data: TodoCreate): Promise<boolean> => {
    try {
      setError(null);
      const newTodo = await api.post<Todo>('/todos', data);
      // Optimistic update - add to beginning of list
      setTodos((prev) => [newTodo, ...prev]);
      setTotalCount((prev) => prev + 1);
      return true;
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.error.message);
      } else {
        setError('Failed to create todo');
      }
      return false;
    }
  }, []);

  const updateTodo = useCallback(async (id: string, data: TodoUpdate): Promise<boolean> => {
    // Store previous state for rollback
    const previousTodos = [...todos];

    try {
      setError(null);
      // Optimistic update
      setTodos((prev) =>
        prev.map((todo) =>
          todo.id === id ? { ...todo, ...data, updated_at: new Date().toISOString() } : todo
        )
      );

      await api.patch<Todo>(`/todos/${id}`, data);
      return true;
    } catch (err) {
      // Rollback on error
      setTodos(previousTodos);
      if (err instanceof ApiException) {
        setError(err.error.message);
      } else {
        setError('Failed to update todo');
      }
      return false;
    }
  }, [todos]);

  const deleteTodo = useCallback(async (id: string): Promise<boolean> => {
    // Store previous state for rollback
    const previousTodos = [...todos];
    const previousCount = totalCount;

    try {
      setError(null);
      // Optimistic update
      setTodos((prev) => prev.filter((todo) => todo.id !== id));
      setTotalCount((prev) => prev - 1);

      await api.delete(`/todos/${id}`);
      return true;
    } catch (err) {
      // Rollback on error
      setTodos(previousTodos);
      setTotalCount(previousCount);
      if (err instanceof ApiException) {
        setError(err.error.message);
      } else {
        setError('Failed to delete todo');
      }
      return false;
    }
  }, [todos, totalCount]);

  const toggleTodo = useCallback(async (id: string): Promise<boolean> => {
    // Store previous state for rollback
    const previousTodos = [...todos];

    try {
      setError(null);
      // Optimistic update
      setTodos((prev) =>
        prev.map((todo) =>
          todo.id === id
            ? { ...todo, is_completed: !todo.is_completed, updated_at: new Date().toISOString() }
            : todo
        )
      );

      await api.post<Todo>(`/todos/${id}/toggle`);
      return true;
    } catch (err) {
      // Rollback on error
      setTodos(previousTodos);
      if (err instanceof ApiException) {
        setError(err.error.message);
      } else {
        setError('Failed to toggle todo status');
      }
      return false;
    }
  }, [todos]);

  // Fetch todos when search or filter changes
  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  return {
    todos,
    isLoading,
    error,
    totalCount,
    searchQuery,
    statusFilter,
    fetchTodos,
    createTodo,
    updateTodo,
    deleteTodo,
    toggleTodo,
    setSearchQuery,
    setStatusFilter,
    clearError,
  };
}
