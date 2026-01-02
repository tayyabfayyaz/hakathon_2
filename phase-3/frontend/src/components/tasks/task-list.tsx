"use client";

import { AnimatePresence } from "framer-motion";
import { TaskItem } from "./task-item";
import { EmptyState } from "./empty-state";
import { Task } from "@/lib/api";

interface TaskListProps {
  tasks: Task[];
  onToggle: (id: string) => void;
  onUpdate: (id: string, text: string) => void;
  onDelete: (id: string) => void;
  onAddTask: () => void;
}

export function TaskList({ tasks, onToggle, onUpdate, onDelete, onAddTask }: TaskListProps) {
  if (tasks.length === 0) {
    return <EmptyState onAddTask={onAddTask} />;
  }

  const completedTasks = tasks.filter((t) => t.completed);
  const pendingTasks = tasks.filter((t) => !t.completed);

  return (
    <div className="space-y-6">
      {/* Pending Tasks */}
      {pendingTasks.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">
            To Do ({pendingTasks.length})
          </h3>
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {pendingTasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onToggle={onToggle}
                  onUpdate={onUpdate}
                  onDelete={onDelete}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">
            Completed ({completedTasks.length})
          </h3>
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {completedTasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onToggle={onToggle}
                  onUpdate={onUpdate}
                  onDelete={onDelete}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
}
