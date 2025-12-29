'use client';

import { createContext, useContext, useCallback, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signOut } from '@/lib/auth-client';

interface User {
  id: string;
  email: string;
  name?: string;
  image?: string;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  login: (credentials: { email: string; password: string }) => Promise<boolean>;
  register: (credentials: { email: string; password: string }) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { data: session, isPending, error: sessionError } = useSession();

  const user = session?.user ? {
    id: session.user.id,
    email: session.user.email,
    name: session.user.name || undefined,
    image: session.user.image || undefined,
  } : null;

  const logout = useCallback(async () => {
    await signOut();
    router.push('/login');
  }, [router]);

  // These are kept for backward compatibility but now auth is handled by Better Auth
  const login = useCallback(async (): Promise<boolean> => {
    // Login is now handled directly by LoginForm using Better Auth
    return true;
  }, []);

  const register = useCallback(async (): Promise<boolean> => {
    // Register is now handled directly by RegisterForm using Better Auth
    return true;
  }, []);

  const checkAuth = useCallback(async () => {
    // Session is automatically managed by Better Auth's useSession hook
  }, []);

  const clearError = useCallback(() => {
    // Error is managed by Better Auth
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      isLoading: isPending,
      isAuthenticated: !!session?.user,
      error: sessionError?.message || null,
      login,
      register,
      logout,
      checkAuth,
      clearError,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}
