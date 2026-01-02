"use client";

import { Button } from "@/components/ui/button";
import { ClipboardList, Plus } from "lucide-react";
import { motion } from "framer-motion";

interface EmptyStateProps {
  onAddTask: () => void;
}

export function EmptyState({ onAddTask }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center py-16 px-4 text-center"
    >
      <div className="mb-6 p-4 rounded-full bg-muted">
        <ClipboardList className="h-12 w-12 text-muted-foreground" />
      </div>
      <h3 className="text-xl font-semibold mb-2">No tasks yet</h3>
      <p className="text-muted-foreground mb-6 max-w-sm">
        Start organizing your day by adding your first task. It's easy – just type
        what you need to do and press enter!
      </p>
      <Button onClick={onAddTask}>
        <Plus className="h-4 w-4 mr-2" />
        Add Your First Task
      </Button>
    </motion.div>
  );
}
