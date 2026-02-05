"use client";

import { useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tasksApi, Task, TaskCreate, TaskUpdate, DeadlineResponse } from "@/lib/api";

// Query key factory
export const taskKeys = {
  all: ["tasks"] as const,
  detail: (id: string) => ["tasks", id] as const,
};

// Hook to fetch all tasks
export function useTasks() {
  return useQuery({
    queryKey: taskKeys.all,
    queryFn: tasksApi.getAll,
    staleTime: 30 * 1000, // 30 seconds
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchInterval: false,
  });
}

// Hook to create a new task with optimistic update
export function useCreateTask() {
  const queryClient = useQueryClient();
  const tempIdRef = useRef<string>("");

  return useMutation({
    mutationFn: (data: TaskCreate) => tasksApi.create(data),
    onMutate: async (newTask) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskKeys.all });

      // Snapshot the previous value
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.all);

      // Generate temp ID for this optimistic update
      tempIdRef.current = `temp-${Date.now()}`;

      // Optimistically update to the new value
      if (previousTasks) {
        const optimisticTask: Task = {
          id: tempIdRef.current,
          task_number: Math.floor(Math.random() * 9000) + 1000, // Temporary random number
          user_id: "",
          text: newTask.text,
          description: null,
          completed: false,
          deadline: null,
          order: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          completed_at: null,
        };
        queryClient.setQueryData<Task[]>(taskKeys.all, [
          optimisticTask,
          ...previousTasks,
        ]);
      }

      // Return context with the snapshotted value and temp ID
      return { previousTasks, tempId: tempIdRef.current };
    },
    onSuccess: (createdTask, _, context) => {
      // Replace the optimistic task with the real one from the server
      const currentTasks = queryClient.getQueryData<Task[]>(taskKeys.all);
      if (currentTasks && context?.tempId) {
        queryClient.setQueryData<Task[]>(
          taskKeys.all,
          currentTasks.map((task) =>
            task.id === context.tempId ? createdTask : task
          )
        );
      }
    },
    onError: (err, newTask, context) => {
      // Rollback to the previous value on error
      if (context?.previousTasks) {
        queryClient.setQueryData<Task[]>(taskKeys.all, context.previousTasks);
      }
    },
    onSettled: () => {
      // Always refetch after error or success to ensure consistency
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}

// Hook to toggle task completion with optimistic update
export function useToggleTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, completed }: { id: string; completed: boolean }) =>
      tasksApi.toggle(id, completed),
    onMutate: async ({ id, completed }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskKeys.all });

      // Snapshot the previous value
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.all);

      // Optimistically update to the new value
      if (previousTasks) {
        queryClient.setQueryData<Task[]>(
          taskKeys.all,
          previousTasks.map((task) =>
            task.id === id
              ? {
                  ...task,
                  completed,
                  completed_at: completed ? new Date().toISOString() : null,
                  updated_at: new Date().toISOString(),
                }
              : task
          )
        );
      }

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData<Task[]>(taskKeys.all, context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}

// Hook to update task text with optimistic update
export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TaskUpdate }) =>
      tasksApi.update(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.all });

      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.all);

      if (previousTasks) {
        queryClient.setQueryData<Task[]>(
          taskKeys.all,
          previousTasks.map((task) =>
            task.id === id
              ? {
                  ...task,
                  ...data,
                  updated_at: new Date().toISOString(),
                }
              : task
          )
        );
      }

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData<Task[]>(taskKeys.all, context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}

// Hook to delete task with optimistic update
export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => tasksApi.delete(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.all });

      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.all);

      if (previousTasks) {
        queryClient.setQueryData<Task[]>(
          taskKeys.all,
          previousTasks.filter((task) => task.id !== id)
        );
      }

      return { previousTasks };
    },
    onError: (err, id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData<Task[]>(taskKeys.all, context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}

// Hook to set task deadline with optimistic update
export function useSetDeadline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, deadline }: { id: string; deadline: string }) =>
      tasksApi.setDeadline(id, deadline),
    onMutate: async ({ id, deadline }) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.all });

      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.all);

      if (previousTasks) {
        queryClient.setQueryData<Task[]>(
          taskKeys.all,
          previousTasks.map((task) =>
            task.id === id
              ? {
                  ...task,
                  deadline,
                  updated_at: new Date().toISOString(),
                }
              : task
          )
        );
      }

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData<Task[]>(taskKeys.all, context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}

// Hook to remove task deadline with optimistic update
export function useRemoveDeadline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => tasksApi.removeDeadline(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.all });

      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.all);

      if (previousTasks) {
        queryClient.setQueryData<Task[]>(
          taskKeys.all,
          previousTasks.map((task) =>
            task.id === id
              ? {
                  ...task,
                  deadline: null,
                  updated_at: new Date().toISOString(),
                }
              : task
          )
        );
      }

      return { previousTasks };
    },
    onError: (err, id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData<Task[]>(taskKeys.all, context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
    },
  });
}
