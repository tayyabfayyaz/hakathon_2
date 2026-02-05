"use client";

/**
 * VoiceIndicator component for real-time transcription display.
 *
 * Features:
 * - Real-time transcription display (interim results)
 * - Processing spinner
 * - Error messages with retry option
 */

import { Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { VoiceState, SpeechRecognitionError } from "@/types/voice";

export interface VoiceIndicatorProps {
  /** Current voice state */
  state: VoiceState;
  /** Current interim transcript */
  interimTranscript: string;
  /** Current error if any */
  error: SpeechRecognitionError | null;
  /** Retry callback for recoverable errors */
  onRetry?: () => void;
  /** Dismiss error callback */
  onDismiss?: () => void;
  /** Optional class name */
  className?: string;
}

export function VoiceIndicator({
  state,
  interimTranscript,
  error,
  onRetry,
  onDismiss,
  className,
}: VoiceIndicatorProps) {
  const showIndicator =
    state === VoiceState.LISTENING ||
    state === VoiceState.PROCESSING ||
    (state === VoiceState.ERROR && error);

  if (!showIndicator) return null;

  return (
    <div
      className={cn(
        "flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-all",
        state === VoiceState.LISTENING && "bg-primary/10 text-primary",
        state === VoiceState.PROCESSING && "bg-muted text-muted-foreground",
        state === VoiceState.ERROR && "bg-destructive/10 text-destructive",
        className
      )}
      role="status"
      aria-live="polite"
    >
      {/* Listening state - show interim transcript */}
      {state === VoiceState.LISTENING && (
        <>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
          </span>
          <span className="flex-1 min-w-0">
            {interimTranscript ? (
              <span className="italic">{interimTranscript}</span>
            ) : (
              <span className="text-muted-foreground">Listening...</span>
            )}
          </span>
        </>
      )}

      {/* Processing state - show spinner */}
      {state === VoiceState.PROCESSING && (
        <>
          <Loader2 className="h-4 w-4 animate-spin shrink-0" />
          <span>Processing...</span>
        </>
      )}

      {/* Error state - show error message with retry option */}
      {state === VoiceState.ERROR && error && (
        <>
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span className="flex-1 min-w-0">{error.message}</span>
          <div className="flex items-center gap-1 shrink-0">
            {error.recoverable && onRetry && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRetry}
                className="h-6 px-2 text-xs"
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                Retry
              </Button>
            )}
            {onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onDismiss}
                className="h-6 px-2 text-xs"
              >
                Dismiss
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
