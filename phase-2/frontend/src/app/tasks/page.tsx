'use client';

import { useCallback, useState } from 'react';
import Header from '@/components/layout/Header';
import TodoForm from '@/components/todos/TodoForm';
import TodoList from '@/components/todos/TodoList';
import SearchBar from '@/components/todos/SearchBar';
import FilterTabs from '@/components/todos/FilterTabs';
import Toast from '@/components/ui/Toast';
import { useTodos } from '@/hooks/useTodos';

export default function TodosPage() {
  const {
    todos,
    isLoading,
    error,
    totalCount,
    searchQuery,
    statusFilter,
    createTodo,
    updateTodo,
    deleteTodo,
    toggleTodo,
    setSearchQuery,
    setStatusFilter,
    clearError,
  } = useTodos();

  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const handleCreateTodo = async (title: string, description?: string) => {
    const success = await createTodo({ title, description });
    if (success) {
      setToast({ message: 'Todo created successfully', type: 'success' });
    }
    return success;
  };

  const handleUpdateTodo = async (id: string, title: string, description?: string) => {
    const success = await updateTodo(id, { title, description });
    if (success) {
      setToast({ message: 'Todo updated successfully', type: 'success' });
    }
    return success;
  };

  const handleDeleteTodo = async (id: string) => {
    const success = await deleteTodo(id);
    if (success) {
      setToast({ message: 'Todo deleted successfully', type: 'success' });
    }
    return success;
  };

  const handleToggleTodo = useCallback(async (id: string) => {
    return toggleTodo(id);
  }, [toggleTodo]);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, [setSearchQuery]);

  // Calculate counts for filter tabs
  const counts = {
    all: totalCount,
    remaining: todos.filter(t => !t.is_completed).length,
    completed: todos.filter(t => t.is_completed).length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">My Todos</h1>

        {/* Add Todo Form */}
        <div className="mb-6">
          <TodoForm onSubmit={handleCreateTodo} isLoading={isLoading} />
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <SearchBar onSearch={handleSearch} />
          </div>
          <FilterTabs
            activeFilter={statusFilter}
            onFilterChange={setStatusFilter}
            counts={counts}
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
            <button
              onClick={clearError}
              className="mt-2 text-sm text-red-500 hover:text-red-700"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Todo List */}
        <TodoList
          todos={todos}
          isLoading={isLoading}
          searchQuery={searchQuery}
          onToggle={handleToggleTodo}
          onUpdate={handleUpdateTodo}
          onDelete={handleDeleteTodo}
        />

        {/* Stats */}
        {!isLoading && todos.length > 0 && (
          <div className="mt-6 text-center text-sm text-gray-500">
            {counts.remaining} remaining · {counts.completed} completed
          </div>
        )}
      </div>

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
