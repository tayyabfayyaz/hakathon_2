'use client';

import { useState } from 'react';
import type { Todo } from '@/types';
import Button from '@/components/ui/Button';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import EditTodoModal from './EditTodoModal';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => Promise<boolean>;
  onUpdate: (id: string, title: string, description?: string) => Promise<boolean>;
  onDelete: (id: string) => Promise<boolean>;
}

export default function TodoItem({ todo, onToggle, onUpdate, onDelete }: TodoItemProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    await onToggle(todo.id);
    setIsToggling(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    await onDelete(todo.id);
    setIsDeleting(false);
    setShowDeleteConfirm(false);
  };

  const handleUpdate = async (title: string, description?: string) => {
    const success = await onUpdate(todo.id, title, description);
    if (success) {
      setShowEditModal(false);
    }
    return success;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start gap-3">
          {/* Checkbox */}
          <button
            onClick={handleToggle}
            disabled={isToggling}
            className={`mt-1 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
              todo.is_completed
                ? 'bg-primary-600 border-primary-600 text-white'
                : 'border-gray-300 hover:border-primary-500'
            } ${isToggling ? 'opacity-50' : ''}`}
            aria-label={todo.is_completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {todo.is_completed && (
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`font-medium ${
                todo.is_completed ? 'line-through text-gray-400' : 'text-gray-900'
              }`}
            >
              {todo.title}
            </h3>
            {todo.description && (
              <p
                className={`mt-1 text-sm ${
                  todo.is_completed ? 'line-through text-gray-300' : 'text-gray-600'
                }`}
              >
                {todo.description}
              </p>
            )}
            <p className="mt-2 text-xs text-gray-400">
              Created {formatDate(todo.created_at)}
              {todo.updated_at !== todo.created_at && (
                <> · Updated {formatDate(todo.updated_at)}</>
              )}
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowEditModal(true)}
              aria-label="Edit todo"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => setShowDeleteConfirm(true)}
              aria-label="Delete todo"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </Button>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <EditTodoModal
          todo={todo}
          onSave={handleUpdate}
          onClose={() => setShowEditModal(false)}
        />
      )}

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <ConfirmDialog
          title="Delete Todo"
          message="Are you sure you want to delete this item?"
          confirmLabel="Delete"
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(false)}
          isLoading={isDeleting}
        />
      )}
    </>
  );
}
