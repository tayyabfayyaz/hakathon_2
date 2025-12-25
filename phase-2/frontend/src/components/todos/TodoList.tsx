'use client';

import type { Todo } from '@/types';
import TodoItem from './TodoItem';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface TodoListProps {
  todos: Todo[];
  isLoading?: boolean;
  searchQuery?: string;
  onToggle: (id: string) => Promise<boolean>;
  onUpdate: (id: string, title: string, description?: string) => Promise<boolean>;
  onDelete: (id: string) => Promise<boolean>;
}

export default function TodoList({
  todos,
  isLoading,
  searchQuery,
  onToggle,
  onUpdate,
  onDelete,
}: TodoListProps) {
  if (isLoading) {
    return (
      <div className="py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (todos.length === 0) {
    return (
      <div className="py-12 text-center">
        <div className="text-gray-400 mb-2">
          <svg
            className="w-16 h-16 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
            />
          </svg>
        </div>
        {searchQuery ? (
          <p className="text-gray-500">No todos found matching your search</p>
        ) : (
          <>
            <p className="text-gray-600 font-medium">No todos yet</p>
            <p className="text-gray-400 text-sm mt-1">Add your first task above!</p>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
