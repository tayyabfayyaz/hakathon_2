"use client";

import { useState, useRef, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TaskInput } from "@/components/tasks/task-input";
import { TaskList } from "@/components/tasks/task-list";
import { DeleteDialog } from "@/components/tasks/delete-dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTasks, useToggleTask, useUpdateTask, useDeleteTask } from "@/hooks/use-tasks";
import { Task } from "@/lib/api";

export default function DashboardPage() {
  const { data: tasks = [], isLoading, error, refetch } = useTasks();
  const toggleTask = useToggleTask();
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleToggleTask = useCallback((id: string) => {
    const task = tasks.find((t) => t.id === id);
    if (task) {
      toggleTask.mutate({ id, completed: !task.completed });
    }
  }, [tasks, toggleTask]);

  const handleUpdateTask = useCallback((id: string, text: string) => {
    updateTask.mutate({ id, data: { text } });
  }, [updateTask]);

  const handleDeleteClick = useCallback((id: string) => {
    const task = tasks.find((t) => t.id === id);
    if (task) {
      setTaskToDelete(task);
      setDeleteDialogOpen(true);
    }
  }, [tasks]);

  const handleConfirmDelete = useCallback(() => {
    if (taskToDelete) {
      deleteTask.mutate(taskToDelete.id);
      setTaskToDelete(null);
    }
  }, [taskToDelete, deleteTask]);

  const handleFocusInput = useCallback(() => {
    inputRef.current?.focus();
  }, []);

  const completedCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length;

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <Skeleton className="h-9 w-48 mb-2" />
          <Skeleton className="h-5 w-64" />
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-20 mb-2" />
                <Skeleton className="h-8 w-12" />
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // Error state - show simple message without retry to avoid potential loops
  if (error) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center text-center">
              <div className="p-4 rounded-full bg-destructive/10 mb-4">
                <AlertCircle className="h-8 w-8 text-destructive" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Failed to load tasks</h3>
              <p className="text-muted-foreground mb-6">
                There was an error loading your tasks. Please refresh the page.
              </p>
              <Button onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Tasks</h1>
        <p className="text-muted-foreground mt-1">
          Manage your tasks and stay organized
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Tasks</CardDescription>
            <CardTitle className="text-3xl">{totalCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Completed</CardDescription>
            <CardTitle className="text-3xl text-green-600">{completedCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Remaining</CardDescription>
            <CardTitle className="text-3xl text-orange-600">
              {totalCount - completedCount}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Task Input */}
      <Card>
        <CardHeader>
          <CardTitle>Add New Task</CardTitle>
          <CardDescription>
            Type your task and press Enter or click Add
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TaskInput />
        </CardContent>
      </Card>

      {/* Task List */}
      <Card>
        <CardHeader>
          <CardTitle>Task List</CardTitle>
          <CardDescription>
            Click the checkbox to complete a task, or hover to edit/delete
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TaskList
            tasks={tasks}
            onToggle={handleToggleTask}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteClick}
            onAddTask={handleFocusInput}
          />
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <DeleteDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        taskText={taskToDelete?.text}
      />
    </div>
  );
}
