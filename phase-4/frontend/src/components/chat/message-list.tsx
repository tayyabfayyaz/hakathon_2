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
        "flex gap-3 max-w-[85%]",
        isUser ? "ml-auto flex-row-reverse" : "mr-auto"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      {/* Message content */}
      <div className="flex flex-col gap-1">
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5",
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "bg-muted rounded-tl-sm",
            message.isPending && "opacity-70"
          )}
        >
          <p className="text-sm whitespace-pre-wrap break-words">
            {message.content}
          </p>
        </div>

        {/* Error state */}
        {message.error && (
          <div className="flex items-center gap-2 text-sm text-destructive">
            <AlertCircle className="h-3.5 w-3.5" />
            <span>{message.error}</span>
            {onRetry && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRetry}
                className="h-6 px-2 text-xs"
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
            "text-xs text-muted-foreground",
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
        <Bot className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium mb-2">Start a Conversation</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          I can help you manage your tasks. Try saying &quot;Add a task to buy groceries&quot;
          or &quot;What are my tasks?&quot;
        </p>
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
        <div className="flex gap-3 max-w-[85%] mr-auto">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
            <Bot className="h-4 w-4" />
          </div>
          <div className="flex items-center rounded-2xl rounded-tl-sm bg-muted px-4 py-2.5">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
