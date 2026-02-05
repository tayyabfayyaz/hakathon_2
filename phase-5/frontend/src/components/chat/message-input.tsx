"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Send, Loader2 } from "lucide-react";
import { VoiceButton, VoiceIndicator } from "./voice";
import { useSpeechRecognition, isSpeechRecognitionSupported } from "@/hooks/use-speech-recognition";
import { VoiceState, InputMethod } from "@/types/voice";

interface MessageInputProps {
  /** Send message callback - receives message and input method */
  onSend: (message: string, inputMethod?: InputMethod) => void;
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
  /** Whether to show voice input button */
  showVoiceInput?: boolean;
}

export function MessageInput({
  onSend,
  disabled = false,
  isLoading = false,
  placeholder = "Type a message...",
  className,
  showVoiceInput = true,
}: MessageInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isVoiceSupported = isSpeechRecognitionSupported();

  // Voice input hook
  const {
    state: voiceState,
    interimTranscript,
    error: voiceError,
    startListening,
    stopListening,
    cancelListening,
    reset: resetVoice,
  } = useSpeechRecognition({
    onResult: (result) => {
      // When we get a final result, send it as a voice message
      if (result.transcript.trim()) {
        onSend(result.transcript.trim(), "voice");
      }
    },
    onEnd: () => {
      // Voice input ended
    },
  });

  // Handle voice button click
  const handleVoiceClick = useCallback(() => {
    if (voiceState === VoiceState.LISTENING) {
      stopListening();
    } else if (voiceState === VoiceState.ERROR) {
      resetVoice();
      startListening();
    } else {
      startListening();
    }
  }, [voiceState, startListening, stopListening, resetVoice]);

  // Handle voice retry
  const handleVoiceRetry = useCallback(() => {
    resetVoice();
    startListening();
  }, [resetVoice, startListening]);

  // Handle voice error dismiss
  const handleVoiceDismiss = useCallback(() => {
    resetVoice();
  }, [resetVoice]);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || disabled || isLoading) return;

    onSend(message.trim(), "text");
    setMessage("");

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter, but allow Shift+Enter for new line
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isVoiceActive = voiceState === VoiceState.LISTENING ||
                        voiceState === VoiceState.PROCESSING;

  return (
    <div className={cn("border-t bg-card/50 backdrop-blur-sm", className)}>
      {/* Voice indicator - shows when listening/processing/error */}
      {showVoiceInput && (
        <VoiceIndicator
          state={voiceState}
          interimTranscript={interimTranscript}
          error={voiceError}
          onRetry={handleVoiceRetry}
          onDismiss={handleVoiceDismiss}
          className="mx-4 mt-2"
        />
      )}

      <form
        onSubmit={handleSubmit}
        className="flex items-end gap-3 p-4 bg-card border border-border/50 rounded-2xl m-4 shadow-sm"
      >
        {/* Voice input button */}
        {showVoiceInput && (
          <VoiceButton
            state={voiceState}
            isSupported={isVoiceSupported}
            onClick={handleVoiceClick}
            disabled={disabled || isLoading}
            className="shrink-0 self-end mb-1"
          />
        )}

        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isVoiceActive ? "Listening... Speak now (press mic to stop)" : placeholder}
            disabled={disabled || isLoading || isVoiceActive}
            maxLength={2000}
            rows={1}
            className={cn(
              "w-full resize-none rounded-xl border border-input bg-background px-4 py-3 pr-12 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50 min-h-[48px] max-h-[150px]",
              isVoiceActive ? "bg-primary/5 border-primary/30" : ""
            )}
          />
          <div className="absolute right-2 bottom-2">
            <Button
              type="submit"
              size="icon"
              disabled={!message.trim() || disabled || isLoading || isVoiceActive}
              className="h-8 w-8 rounded-full bg-primary hover:bg-primary/90 transition-colors shadow-sm"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span className="sr-only">Send message</span>
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
