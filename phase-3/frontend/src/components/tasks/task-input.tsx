"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Loader2, AlertCircle } from "lucide-react";
import { useCreateTask } from "@/hooks/use-tasks";

interface TaskInputProps {
  onAddTask?: (text: string) => void;
}

export function TaskInput({ onAddTask }: TaskInputProps) {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createTask = useCreateTask();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!text.trim()) return;

    try {
      await createTask.mutateAsync({ text: text.trim() });
      setText("");
      // Call optional callback for parent component
      onAddTask?.(text.trim());
    } catch (err) {
      console.error("Failed to create task:", err);
      setError("Failed to add task. Please try again.");
    }
  };

  return (
    <div className="space-y-2">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          type="text"
          placeholder="What needs to be done?"
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            setError(null);
          }}
          className="flex-1"
          maxLength={500}
          disabled={createTask.isPending}
        />
        <Button
          type="submit"
          disabled={!text.trim() || createTask.isPending}
        >
          {createTask.isPending ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Adding...
            </>
          ) : (
            <>
              <Plus className="h-4 w-4 mr-2" />
              Add Task
            </>
          )}
        </Button>
      </form>
      {error && (
        <div className="flex items-center gap-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
