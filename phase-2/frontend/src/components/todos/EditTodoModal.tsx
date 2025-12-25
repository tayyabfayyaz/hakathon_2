'use client';

import { useState, FormEvent, useEffect, useCallback } from 'react';
import type { Todo } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { validateTodoTitle, validateTodoDescription } from '@/lib/validation';

interface EditTodoModalProps {
  todo: Todo;
  onSave: (title: string, description?: string) => Promise<boolean>;
  onClose: () => void;
}

export default function EditTodoModal({ todo, onSave, onClose }: EditTodoModalProps) {
  const [title, setTitle] = useState(todo.title);
  const [description, setDescription] = useState(todo.description || '');
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isSubmitting) {
        onClose();
      }
    },
    [onClose, isSubmitting]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const titleValidation = validateTodoTitle(title);
    const descValidation = validateTodoDescription(description);

    if (!titleValidation.isValid || !descValidation.isValid) {
      setErrors({
        title: titleValidation.error,
        description: descValidation.error,
      });
      return;
    }

    setErrors({});
    setIsSubmitting(true);

    const success = await onSave(title.trim(), description.trim() || undefined);
    setIsSubmitting(false);

    if (success) {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={!isSubmitting ? onClose : undefined}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Edit Todo</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            error={errors.title}
            disabled={isSubmitting}
            autoFocus
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isSubmitting}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent resize-none ${
                errors.description
                  ? 'border-red-500 focus:ring-red-500'
                  : 'border-gray-300 focus:ring-primary-500'
              }`}
              rows={3}
              placeholder="Add a description (optional)"
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description}</p>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Save Changes
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
