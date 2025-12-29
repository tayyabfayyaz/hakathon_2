'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { validateEmail, validatePassword } from '@/lib/validation';
import { signUp } from '@/lib/auth-client';

interface RegisterFormProps {
  onSubmit?: (email: string, password: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  redirectTo?: string;
}

export default function RegisterForm({ onSubmit, isLoading: externalLoading, error: externalError, redirectTo = '/tasks' }: RegisterFormProps) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string; confirmPassword?: string; form?: string }>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validate fields
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    const newErrors: typeof errors = {};

    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.error;
    }

    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.error;
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    setIsLoading(true);

    try {
      // Use Better Auth signUp with explicit callback to prevent default redirect
      const result = await signUp.email({
        email: email.trim(),
        password,
        name: email.split('@')[0], // Use email prefix as display name
        callbackURL: redirectTo, // Explicit redirect to /tasks
      });

      if (result.error) {
        if (result.error.code === 'USER_ALREADY_EXISTS') {
          setErrors({ email: 'An account with this email already exists' });
        } else {
          setErrors({ form: result.error.message || 'Registration failed' });
        }
      } else {
        // Registration successful - redirect to tasks page
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
        placeholder="At least 8 characters"
        autoComplete="new-password"
        disabled={loading}
      />

      <Input
        label="Confirm Password"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        error={errors.confirmPassword}
        placeholder="Confirm your password"
        autoComplete="new-password"
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
        Create Account
      </Button>

      <p className="text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link href="/login" className="text-primary-600 hover:text-primary-700 font-medium">
          Sign in
        </Link>
      </p>
    </form>
  );
}
