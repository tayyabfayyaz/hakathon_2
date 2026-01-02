"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface DemoTask {
  id: number;
  text: string;
  completed: boolean;
}

const initialTasks: DemoTask[] = [
  { id: 1, text: "Design the landing page", completed: true },
  { id: 2, text: "Implement user authentication", completed: true },
  { id: 3, text: "Build task management features", completed: false },
  { id: 4, text: "Add responsive design", completed: false },
];

export function DemoSection() {
  const [tasks, setTasks] = useState<DemoTask[]>(initialTasks);

  const toggleTask = (id: number) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const addTask = () => {
    const newTask: DemoTask = {
      id: Date.now(),
      text: `New task ${tasks.length + 1}`,
      completed: false,
    };
    setTasks((prev) => [...prev, newTask]);
  };

  const removeTask = (id: number) => {
    setTasks((prev) => prev.filter((task) => task.id !== id));
  };

  return (
    <section id="features" className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          {/* Left side - Text */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
              See It in Action
            </h2>
            <p className="text-lg text-muted-foreground">
              Experience the simplicity of TodoList Pro. Click the checkboxes to complete
              tasks, add new ones, or remove them. It's that easy!
            </p>
            <ul className="space-y-3 text-muted-foreground">
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Click checkboxes to toggle completion
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Add new tasks with one click
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Remove tasks you no longer need
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Smooth animations for a delightful experience
              </li>
            </ul>
          </motion.div>

          {/* Right side - Interactive Demo */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card className="shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-semibold text-lg">My Tasks</h3>
                  <Button size="sm" onClick={addTask}>
                    <Plus className="h-4 w-4 mr-1" />
                    Add Task
                  </Button>
                </div>

                <div className="space-y-2">
                  <AnimatePresence mode="popLayout">
                    {tasks.map((task) => (
                      <motion.div
                        key={task.id}
                        layout
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8, x: -100 }}
                        transition={{ duration: 0.2 }}
                        className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors group"
                      >
                        <Checkbox
                          id={`demo-task-${task.id}`}
                          checked={task.completed}
                          onCheckedChange={() => toggleTask(task.id)}
                          className="h-5 w-5"
                        />
                        <label
                          htmlFor={`demo-task-${task.id}`}
                          className={`flex-1 cursor-pointer transition-all ${
                            task.completed
                              ? "line-through text-muted-foreground"
                              : ""
                          }`}
                        >
                          {task.text}
                        </label>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => removeTask(task.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  {tasks.length === 0 && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-center py-8 text-muted-foreground"
                    >
                      <p>No tasks yet. Click "Add Task" to create one!</p>
                    </motion.div>
                  )}
                </div>

                {/* Stats */}
                <div className="mt-6 pt-4 border-t flex justify-between text-sm text-muted-foreground">
                  <span>{tasks.filter((t) => t.completed).length} completed</span>
                  <span>{tasks.filter((t) => !t.completed).length} remaining</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
