'use client';

import { useState, FormEvent, KeyboardEvent } from 'react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { validateTodoTitle } from '@/lib/validation';

interface TodoFormProps {
  onSubmit: (title: string, description?: string) => Promise<boolean>;
  isLoading?: boolean;
}

export default function TodoForm({ onSubmit, isLoading }: TodoFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | undefined>();
  const [showDescription, setShowDescription] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const validation = validateTodoTitle(title);
    if (!validation.isValid) {
      setError(validation.error);
      return;
    }

    setError(undefined);
    const success = await onSubmit(title.trim(), description.trim() || undefined);
    if (success) {
      setTitle('');
      setDescription('');
      setShowDescription(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            placeholder="What needs to be done?"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              if (error) setError(undefined);
            }}
            onKeyDown={handleKeyDown}
            error={error}
            disabled={isLoading}
            aria-label="New todo title"
          />
        </div>
        <Button type="submit" isLoading={isLoading} disabled={!title.trim()}>
          Add
        </Button>
      </div>

      {!showDescription && (
        <button
          type="button"
          onClick={() => setShowDescription(true)}
          className="mt-2 text-sm text-gray-500 hover:text-gray-700"
        >
          + Add description
        </button>
      )}

      {showDescription && (
        <div className="mt-3">
          <textarea
            placeholder="Add a description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            rows={2}
            aria-label="Todo description"
          />
          <button
            type="button"
            onClick={() => {
              setShowDescription(false);
              setDescription('');
            }}
            className="mt-1 text-sm text-gray-500 hover:text-gray-700"
          >
            Cancel
          </button>
        </div>
      )}
    </form>
  );
}
