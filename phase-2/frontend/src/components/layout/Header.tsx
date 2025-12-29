'use client';

import Button from '@/components/ui/Button';
import { useAuthContext } from '@/contexts/AuthContext';

export default function Header() {
  const { user, logout, isLoading } = useAuthContext();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-gray-900">TodoList Pro</h1>
        </div>

        {user && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user.email}</span>
            <Button
              variant="secondary"
              size="sm"
              onClick={logout}
              isLoading={isLoading}
            >
              Logout
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
