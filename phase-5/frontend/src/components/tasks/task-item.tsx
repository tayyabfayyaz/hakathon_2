"use client";

import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Pencil, Trash2, Check, X, Calendar } from "lucide-react";
import { motion } from "framer-motion";
import { Task } from "@/lib/api";
import { DeadlineBadge, DeadlinePicker } from "./deadline-picker";

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onUpdate: (id: string, text: string) => void;
  onDelete: (id: string) => void;
  onSetDeadline?: (id: string, deadline: string) => void;
  onRemoveDeadline?: (id: string) => void;
  isToggling?: boolean;
  isUpdating?: boolean;
}

export function TaskItem({
  task,
  onToggle,
  onUpdate,
  onDelete,
  onSetDeadline,
  onRemoveDeadline,
}: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(task.text);
  const [showDeadlinePicker, setShowDeadlinePicker] = useState(false);

  const handleDeadlineChange = (deadline: Date | null) => {
    if (deadline && onSetDeadline) {
      onSetDeadline(task.id, deadline.toISOString());
    } else if (!deadline && onRemoveDeadline) {
      onRemoveDeadline(task.id);
    }
    setShowDeadlinePicker(false);
  };

  const handleSave = () => {
    if (editText.trim() && editText !== task.text) {
      onUpdate(task.id, editText.trim());
    } else {
      setEditText(task.text);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditText(task.text);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      handleCancel();
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.2 }}
      className={`flex items-center gap-3 p-4 rounded-lg border bg-card transition-all group ${
        task.completed ? "opacity-60" : ""
      }`}
    >
      <Checkbox
        id={`task-${task.id}`}
        checked={task.completed}
        onCheckedChange={() => onToggle(task.id)}
        className="h-5 w-5"
      />

      {isEditing ? (
        <div className="flex-1 flex items-center gap-2">
          <Input
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1"
            autoFocus
            maxLength={500}
          />
          <Button size="icon" variant="ghost" onClick={handleSave}>
            <Check className="h-4 w-4 text-green-600" />
          </Button>
          <Button size="icon" variant="ghost" onClick={handleCancel}>
            <X className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ) : (
        <>
          <div className="flex-1 min-w-0">
            <div
              className={`cursor-pointer transition-all ${
                task.completed ? "line-through text-muted-foreground" : ""
              }`}
            >
              <span className="inline-flex items-center mr-2 px-1.5 py-0.5 rounded text-xs font-mono bg-muted text-muted-foreground">
                #{task.task_number || "----"}
              </span>
              <span onClick={() => onToggle(task.id)}>{task.text}</span>
            </div>
            {task.deadline && !task.completed && (
              <div className="mt-1.5">
                <DeadlineBadge
                  deadline={task.deadline}
                  onClick={() => setShowDeadlinePicker(true)}
                />
              </div>
            )}
          </div>

          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {!task.completed && onSetDeadline && (
              <DeadlinePicker
                deadline={task.deadline ? new Date(task.deadline) : null}
                onDeadlineChange={handleDeadlineChange}
                className="h-8"
              />
            )}
            <Button
              size="icon"
              variant="ghost"
              onClick={() => setIsEditing(true)}
              className="h-8 w-8"
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => onDelete(task.id)}
              className="h-8 w-8"
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </div>
        </>
      )}
    </motion.div>
  );
}
