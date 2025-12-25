'use client';

import { useState, useCallback } from 'react';
import { authApi, LoginCredentials, RegisterCredentials } from '@/lib/auth';
import type { User } from '@/types';
import { ApiException } from '@/lib/api';

export interface UseAuthReturn {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (credentials: RegisterCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const checkAuth = useCallback(async () => {
    try {
      setIsLoading(true);
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await authApi.login(credentials);
      setUser(response.user);
      return true;
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.error.message);
      } else {
        setError('An unexpected error occurred');
      }
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (credentials: RegisterCredentials): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await authApi.register(credentials);
      setUser(response.user);
      return true;
    } catch (err) {
      if (err instanceof ApiException) {
        if (err.error.details?.fields) {
          const fieldErrors = err.error.details.fields
            .map(f => `${f.field}: ${f.error}`)
            .join(', ');
          setError(fieldErrors);
        } else {
          setError(err.error.message);
        }
      } else {
        setError('An unexpected error occurred');
      }
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      await authApi.logout();
      setUser(null);
    } catch (err) {
      // Even if logout fails, clear local state
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    user,
    isLoading,
    error,
    login,
    register,
    logout,
    checkAuth,
    clearError,
  };
}
