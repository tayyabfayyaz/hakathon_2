"use client";

import { cn } from "@/lib/utils";

interface TypingIndicatorProps {
  className?: string;
}

export function TypingIndicator({ className }: TypingIndicatorProps) {
  return (
    <div className={cn("flex items-center gap-3 p-3", className)}>
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-muted to-accent border border-border/50">
        <span className="text-xs">AI</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground font-medium">Thinking...</span>
        <span className="flex gap-1">
          <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:300ms]" />
        </span>
      </div>
    </div>
  );
}
