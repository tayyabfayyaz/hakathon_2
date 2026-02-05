"use client";

/**
 * VoiceButton component for voice input control.
 *
 * Features:
 * - Microphone icon button with visual states
 * - States: idle, listening (pulsing), processing, error
 * - Click to start/stop recording
 * - Accessibility support with aria-labels
 */

import { forwardRef } from "react";
import { Mic, MicOff, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { VoiceState } from "@/types/voice";

// Extract the props type from the Button component
type ButtonProps = React.ComponentProps<typeof Button>;

export interface VoiceButtonProps extends Omit<ButtonProps, "onClick"> {
  /** Current voice state */
  state: VoiceState;
  /** Whether speech recognition is supported */
  isSupported: boolean;
  /** Click handler - toggles listening */
  onClick: () => void;
  /** Optional class name */
  className?: string;
}

/**
 * Get aria-label based on current state.
 */
function getAriaLabel(state: VoiceState, isSupported: boolean): string {
  if (!isSupported) return "Voice input not supported";

  switch (state) {
    case VoiceState.IDLE:
      return "Start voice input";
    case VoiceState.LISTENING:
      return "Stop voice input";
    case VoiceState.PROCESSING:
      return "Processing voice input";
    case VoiceState.ERROR:
      return "Voice input error. Click to retry";
    default:
      return "Voice input";
  }
}

/**
 * Get button variant based on current state.
 */
function getButtonVariant(state: VoiceState): ButtonProps["variant"] {
  switch (state) {
    case VoiceState.LISTENING:
      return "default";
    case VoiceState.ERROR:
      return "destructive";
    default:
      return "ghost";
  }
}

export const VoiceButton = forwardRef<HTMLButtonElement, VoiceButtonProps>(
  ({ state, isSupported, onClick, className, disabled, ...props }, ref) => {
    const isDisabled = disabled || !isSupported || state === VoiceState.PROCESSING;
    const isListening = state === VoiceState.LISTENING;
    const isProcessing = state === VoiceState.PROCESSING;
    const isError = state === VoiceState.ERROR;

    return (
      <Button
        ref={ref}
        type="button"
        variant={getButtonVariant(state)}
        size="icon"
        onClick={onClick}
        disabled={isDisabled}
        aria-label={getAriaLabel(state, isSupported)}
        aria-pressed={isListening}
        className={cn(
          "relative transition-all duration-200 rounded-full shadow-sm h-10 w-10",
          // Pulsing animation when listening
          isListening && "animate-pulse bg-red-500 text-white hover:bg-red-600",
          // Error state
          isError && "text-destructive-foreground bg-destructive hover:bg-destructive/90",
          // Default state
          !isListening && !isError && "bg-accent hover:bg-accent/80 text-foreground",
          // Not supported state
          !isSupported && "opacity-50 cursor-not-allowed",
          className
        )}
        title={!isSupported ? "Voice input not supported in this browser" : undefined}
        {...props}
      >
        {/* Processing spinner */}
        {isProcessing && (
          <Loader2 className="h-4 w-4 animate-spin" />
        )}

        {/* Error icon */}
        {isError && !isProcessing && (
          <AlertCircle className="h-4 w-4" />
        )}

        {/* Mic icon (default and listening states) */}
        {!isProcessing && !isError && (
          isSupported ? (
            <Mic className={cn(
              "h-4 w-4 transition-transform",
              isListening && "scale-110"
            )} />
          ) : (
            <MicOff className="h-4 w-4" />
          )
        )}

        {/* Listening indicator ring */}
        {isListening && (
          <span
            className="absolute inset-0 rounded-md animate-ping bg-primary/30"
            aria-hidden="true"
          />
        )}
      </Button>
    );
  }
);

VoiceButton.displayName = "VoiceButton";
