'use client';

import { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAuth, UseAuthReturn } from '@/hooks/useAuth';

const AuthContext = createContext<UseAuthReturn | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuth();

  useEffect(() => {
    // Check authentication status on mount
    auth.checkAuth();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext(): UseAuthReturn {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}
