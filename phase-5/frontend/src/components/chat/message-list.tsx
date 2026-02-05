"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, RotateCcw, User, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ChatMessage } from "@/hooks/use-chat";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  isTyping?: boolean;
  onRetry?: (messageId: string) => void;
  className?: string;
}

function MessageSkeleton() {
  return (
    <div className="space-y-4 p-4">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className={cn(
            "flex gap-3",
            i % 2 === 0 ? "justify-end" : "justify-start"
          )}
        >
          {i % 2 !== 0 && <Skeleton className="h-8 w-8 rounded-full shrink-0" />}
          <div className={cn("space-y-2", i % 2 === 0 ? "items-end" : "items-start")}>
            <Skeleton className="h-4 w-32" />
            <Skeleton className={cn("h-16", i % 2 === 0 ? "w-48" : "w-64")} />
          </div>
          {i % 2 === 0 && <Skeleton className="h-8 w-8 rounded-full shrink-0" />}
        </div>
      ))}
    </div>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
  onRetry?: () => void;
}

function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 max-w-[85%] group hover:bg-accent/20 rounded-2xl px-2 py-1 -mx-2 transition-colors duration-200",
        isUser ? "ml-auto flex-row-reverse" : "mr-auto"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-transparent",
          isUser ? "bg-primary text-primary-foreground" : "bg-gradient-to-br from-muted to-accent"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      {/* Message content */}
      <div className="flex flex-col gap-1 min-w-0">
        <div
          className={cn(
            "rounded-2xl px-4 py-3 shadow-sm",
            isUser
              ? "bg-gradient-to-r from-primary to-primary/90 text-primary-foreground rounded-tr-sm border border-primary/20"
              : "bg-card text-foreground rounded-tl-sm border border-border/50",
            message.isPending && "opacity-70 bg-muted/50 border-dashed"
          )}
        >
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">
            {message.content}
          </p>
        </div>

        {/* Error state */}
        {message.error && (
          <div className="flex items-center gap-2 text-sm text-destructive pt-1">
            <AlertCircle className="h-3.5 w-3.5" />
            <span>{message.error}</span>
            {onRetry && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRetry}
                className="h-6 px-2 text-xs hover:bg-destructive/20 hover:text-destructive"
              >
                <RotateCcw className="h-3 w-3 mr-1" />
                Retry
              </Button>
            )}
          </div>
        )}

        {/* Timestamp */}
        <span
          className={cn(
            "text-xs text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity duration-200",
            isUser ? "text-right" : "text-left"
          )}
        >
          {message.createdAt.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}

export function MessageList({
  messages,
  isLoading,
  isTyping,
  onRetry,
  className,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  if (isLoading) {
    return <MessageSkeleton />;
  }

  if (messages.length === 0) {
    return (
      <div className={cn("flex flex-col items-center justify-center h-full p-8 text-center", className)}>
        <div className="relative mb-6">
          <div className="absolute inset-0 bg-primary/10 blur-2xl rounded-full"></div>
          <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20">
            <Bot className="h-8 w-8 text-primary" />
          </div>
        </div>
        <h3 className="text-xl font-semibold mb-2 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
          How can I help you today?
        </h3>
        <p className="text-sm text-muted-foreground max-w-md mb-4">
          I can help you manage your tasks with voice or text. Try saying:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-md">
          <div className="text-xs bg-muted/50 rounded-lg px-3 py-2 text-left">
            <span className="text-primary font-medium">"Add task"</span> to create a new task
          </div>
          <div className="text-xs bg-muted/50 rounded-lg px-3 py-2 text-left">
            <span className="text-primary font-medium">"Show tasks"</span> to see your list
          </div>
          <div className="text-xs bg-muted/50 rounded-lg px-3 py-2 text-left">
            <span className="text-primary font-medium">"Complete task"</span> to finish a task
          </div>
          <div className="text-xs bg-muted/50 rounded-lg px-3 py-2 text-left">
            <span className="text-primary font-medium">"Set deadline"</span> for a task
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col gap-4 p-4 overflow-y-auto", className)}>
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          onRetry={onRetry ? () => onRetry(message.id) : undefined}
        />
      ))}

      {isTyping && (
        <div className="flex gap-3 max-w-[85%] mr-auto pl-2">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-muted to-accent border border-border/50">
            <Bot className="h-4 w-4" />
          </div>
          <div className="flex items-center rounded-2xl rounded-tl-sm bg-card border border-border/50 px-4 py-2.5 shadow-sm">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
