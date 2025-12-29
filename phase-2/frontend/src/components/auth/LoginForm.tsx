'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { validateEmail, validatePassword } from '@/lib/validation';
import { signIn } from '@/lib/auth-client';

interface LoginFormProps {
  onSubmit?: (email: string, password: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  redirectTo?: string;
}

export default function LoginForm({ onSubmit, isLoading: externalLoading, error: externalError, redirectTo = '/tasks' }: LoginFormProps) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string; form?: string }>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validate fields
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    if (!emailValidation.isValid || !passwordValidation.isValid) {
      setErrors({
        email: emailValidation.error,
        password: passwordValidation.error,
      });
      return;
    }

    setErrors({});
    setIsLoading(true);

    try {
      // Use Better Auth signIn with explicit callback
      const result = await signIn.email({
        email: email.trim(),
        password,
        callbackURL: redirectTo, // Explicit redirect to /tasks
      });

      if (result.error) {
        // Better error messages for common issues
        const errorMessage = result.error.message || 'Invalid credentials';
        if (result.error.code === 'INVALID_EMAIL_OR_PASSWORD' || errorMessage.includes('not found')) {
          setErrors({ form: 'Invalid email or password. Please check your credentials or register a new account.' });
        } else {
          setErrors({ form: errorMessage });
        }
      } else {
        // Login successful - redirect to tasks page
        router.push(redirectTo);
        router.refresh(); // Force refresh to update session state
      }
    } catch (err) {
      setErrors({ form: 'An unexpected error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const loading = isLoading || externalLoading;
  const formError = errors.form || externalError;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={errors.email}
        placeholder="you@example.com"
        autoComplete="email"
        disabled={loading}
      />

      <Input
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        error={errors.password}
        placeholder="Enter your password"
        autoComplete="current-password"
        disabled={loading}
      />

      {formError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{formError}</p>
        </div>
      )}

      <Button
        type="submit"
        variant="primary"
        className="w-full"
        isLoading={loading}
      >
        Sign In
      </Button>

      <p className="text-center text-sm text-gray-600">
        Don&apos;t have an account?{' '}
        <Link href="/register" className="text-primary-600 hover:text-primary-700 font-medium">
          Sign up
        </Link>
      </p>
    </form>
  );
}
