"use client";

import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { TypingIndicator } from "./typing-indicator";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { AlertCircle, RefreshCw, MessageSquare } from "lucide-react";

interface ChatContainerProps {
  className?: string;
}

export function ChatContainer({ className }: ChatContainerProps) {
  const {
    messages,
    isTyping,
    isLoading,
    isSending,
    error,
    sendMessage,
    retryMessage,
    refreshHistory,
  } = useChat({
    onError: (error) => {
      console.error("Chat error:", error);
    },
  });

  return (
    <div
      className={cn(
        "flex flex-col h-full bg-background rounded-lg border shadow-sm",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary" />
          <h2 className="font-semibold">AI Assistant</h2>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={refreshHistory}
          disabled={isLoading}
          title="Refresh conversation"
        >
          <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
        </Button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-2 bg-destructive/10 text-destructive text-sm">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span className="flex-1">{error}</span>
        </div>
      )}

      {/* Messages */}
      <MessageList
        messages={messages}
        isLoading={isLoading}
        isTyping={isTyping}
        onRetry={retryMessage}
        className="flex-1 min-h-0"
      />

      {/* Typing indicator (alternative position) */}
      {/* {isTyping && <TypingIndicator className="border-t" />} */}

      {/* Input */}
      <MessageInput
        onSend={sendMessage}
        disabled={isLoading}
        isLoading={isSending}
        placeholder="Ask me to help with your tasks..."
      />
    </div>
  );
}
