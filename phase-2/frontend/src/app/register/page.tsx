'use client';

import { useRouter } from 'next/navigation';
import Card from '@/components/ui/Card';
import RegisterForm from '@/components/auth/RegisterForm';
import { useAuthContext } from '@/contexts/AuthContext';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error } = useAuthContext();

  const handleSubmit = async (email: string, password: string) => {
    const success = await register({ email, password });
    if (success) {
      router.push('/todos');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">TodoList Pro</h1>
          <p className="mt-2 text-gray-600">Create your account</p>
        </div>

        <Card>
          <RegisterForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            error={error}
          />
        </Card>
      </div>
    </div>
  );
}
