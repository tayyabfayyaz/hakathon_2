"use client";

import { useCallback, useRef } from "react";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { TypingIndicator } from "./typing-indicator";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { AlertCircle, RefreshCw, MessageSquare, Mic } from "lucide-react";
import { isSpeechRecognitionSupported } from "@/hooks/use-speech-recognition";
import { InputMethod } from "@/lib/chat-api";

interface ChatContainerProps {
  className?: string;
}

export function ChatContainer({ className }: ChatContainerProps) {
  const isVoiceSupported = isSpeechRecognitionSupported();
  const lastInputMethodRef = useRef<InputMethod>("text");

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

  // Wrap sendMessage to track last input method
  const handleSendMessage = useCallback(
    (message: string, inputMethod: InputMethod = "text") => {
      lastInputMethodRef.current = inputMethod;
      sendMessage(message, inputMethod);
    },
    [sendMessage]
  );

  return (
    <div
      className={cn(
        "flex flex-col h-full bg-gradient-to-br from-background to-muted rounded-2xl border border-border/50 shadow-xl shadow-black/10 overflow-hidden",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-card border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 blur-md rounded-full"></div>
            <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r from-primary to-primary/80 border border-primary/20">
              <MessageSquare className="h-5 w-5 text-primary-foreground" />
            </div>
          </div>
          <div>
            <h2 className="font-semibold text-lg text-foreground">AI Assistant</h2>
            <p className="text-xs text-muted-foreground">
              {isVoiceSupported ? "Voice enabled" : "Text only"} • Online
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={refreshHistory}
          disabled={isLoading}
          title="Refresh conversation"
          className="hover:bg-accent/50 transition-colors"
        >
          <RefreshCw className={cn("h-4 w-4 text-muted-foreground", isLoading && "animate-spin")} />
        </Button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-3 px-4 py-3 bg-destructive/10 text-destructive text-sm border-b border-destructive/20">
          <AlertCircle className="h-4 w-4 shrink-0 flex-shrink-0" />
          <span className="flex-1">{error}</span>
        </div>
      )}

      {/* Messages */}
      <MessageList
        messages={messages}
        isLoading={isLoading}
        isTyping={isTyping}
        onRetry={retryMessage}
        className="flex-1 min-h-0 bg-gradient-to-b from-card/50 to-card"
      />

      {/* Input */}
      <MessageInput
        onSend={handleSendMessage}
        disabled={isLoading}
        isLoading={isSending}
        placeholder="Ask me to help with your tasks... (e.g., 'Add task to buy groceries' or 'What are my tasks?')"
        showVoiceInput={isVoiceSupported}
      />
    </div>
  );
}
