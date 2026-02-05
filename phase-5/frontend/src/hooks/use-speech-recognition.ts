"use client";

/**
 * useSpeechRecognition hook for voice input using Web Speech API.
 *
 * Features:
 * - Start/stop/cancel voice recording
 * - Interim and final results
 * - Browser compatibility detection
 * - End-of-speech auto-detection with silence timeout
 * - Error handling with user-friendly messages
 */

import { useState, useCallback, useRef, useEffect } from "react";
import {
  VoiceState,
  SpeechRecognitionResult,
  SpeechRecognitionError,
  SpeechRecognitionErrorType,
  ISpeechRecognition,
} from "@/types/voice";

/** Silence timeout in milliseconds (5 seconds per spec) */
const SILENCE_TIMEOUT_MS = 5000;

/** Default language for speech recognition */
const DEFAULT_LANGUAGE = "en-US";

/**
 * Map speech recognition errors to user-friendly messages.
 */
function getErrorMessage(errorType: SpeechRecognitionErrorType): SpeechRecognitionError {
  const errorMap: Record<SpeechRecognitionErrorType, SpeechRecognitionError> = {
    "no-speech": {
      type: "no-speech",
      message: "I didn't hear anything. Please try again.",
      recoverable: true,
    },
    "audio-capture": {
      type: "audio-capture",
      message: "Microphone is busy or unavailable. Please close other apps using the microphone.",
      recoverable: true,
    },
    "not-allowed": {
      type: "not-allowed",
      message: "Microphone access denied. Please allow microphone access in your browser settings.",
      recoverable: false,
    },
    "network": {
      type: "network",
      message: "Network error. Please check your connection and try again.",
      recoverable: true,
    },
    "aborted": {
      type: "aborted",
      message: "",
      recoverable: true,
    },
    "service-not-allowed": {
      type: "service-not-allowed",
      message: "Speech recognition service not available.",
      recoverable: false,
    },
    "bad-grammar": {
      type: "bad-grammar",
      message: "Could not understand. Please try speaking more clearly.",
      recoverable: true,
    },
    "language-not-supported": {
      type: "language-not-supported",
      message: "Language not supported. Please use English.",
      recoverable: false,
    },
  };

  return errorMap[errorType] || {
    type: errorType,
    message: "An error occurred. Please try again.",
    recoverable: true,
  };
}

/**
 * Check if Web Speech API is supported in the browser.
 */
export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === "undefined") return false;
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
}

/**
 * Get SpeechRecognition constructor.
 */
function getSpeechRecognitionConstructor(): (new () => ISpeechRecognition) | null {
  if (typeof window === "undefined") return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

export interface UseSpeechRecognitionOptions {
  /** Language for recognition (default: en-US) */
  language?: string;
  /** Enable continuous listening (default: false) */
  continuous?: boolean;
  /** Silence timeout in ms (default: 5000) */
  silenceTimeout?: number;
  /** Callback when final result is received */
  onResult?: (result: SpeechRecognitionResult) => void;
  /** Callback when error occurs */
  onError?: (error: SpeechRecognitionError) => void;
  /** Callback when speech ends (silence detected or manual stop) */
  onEnd?: () => void;
}

export interface UseSpeechRecognitionReturn {
  /** Current voice state */
  state: VoiceState;
  /** Current interim transcript (updates in real-time) */
  interimTranscript: string;
  /** Final transcript (after speech ends) */
  finalTranscript: string;
  /** Current error if any */
  error: SpeechRecognitionError | null;
  /** Whether speech recognition is supported */
  isSupported: boolean;
  /** Start listening for speech */
  startListening: () => void;
  /** Stop listening and process final result */
  stopListening: () => void;
  /** Cancel listening without processing */
  cancelListening: () => void;
  /** Clear transcripts and error */
  reset: () => void;
}

/**
 * Hook for speech recognition using Web Speech API.
 */
export function useSpeechRecognition(
  options: UseSpeechRecognitionOptions = {}
): UseSpeechRecognitionReturn {
  const {
    language = DEFAULT_LANGUAGE,
    continuous = false,
    silenceTimeout = SILENCE_TIMEOUT_MS,
    onResult,
    onError,
    onEnd,
  } = options;

  const [state, setState] = useState<VoiceState>(VoiceState.IDLE);
  const [interimTranscript, setInterimTranscript] = useState("");
  const [finalTranscript, setFinalTranscript] = useState("");
  const [error, setError] = useState<SpeechRecognitionError | null>(null);
  const [isSupported] = useState(() => isSpeechRecognitionSupported());

  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isListeningRef = useRef(false);

  /**
   * Clear silence timeout.
   */
  const clearSilenceTimer = useCallback(() => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  }, []);

  /**
   * Reset silence timeout (called on speech activity).
   */
  const resetSilenceTimer = useCallback(() => {
    clearSilenceTimer();
    if (continuous && isListeningRef.current) {
      silenceTimerRef.current = setTimeout(() => {
        // Silence timeout - stop listening
        if (recognitionRef.current && isListeningRef.current) {
          recognitionRef.current.stop();
        }
      }, silenceTimeout);
    }
  }, [continuous, silenceTimeout, clearSilenceTimer]);

  /**
   * Initialize speech recognition instance.
   */
  const initRecognition = useCallback(() => {
    const SpeechRecognitionClass = getSpeechRecognitionConstructor();
    if (!SpeechRecognitionClass) return null;

    const recognition = new SpeechRecognitionClass();
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.lang = language;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setState(VoiceState.LISTENING);
      setError(null);
      isListeningRef.current = true;
      if (continuous) {
        resetSilenceTimer();
      }
    };

    recognition.onspeechstart = () => {
      // User started speaking - reset silence timer
      resetSilenceTimer();
    };

    recognition.onspeechend = () => {
      // Speech ended - if not continuous, will auto-stop
      if (!continuous) {
        setState(VoiceState.PROCESSING);
      }
    };

    recognition.onresult = (event) => {
      let interim = "";
      let final = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;

        if (result.isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if (interim) {
        setInterimTranscript(interim);
        // Reset silence timer on any speech activity
        resetSilenceTimer();
      }

      if (final) {
        setFinalTranscript((prev) => prev + final);
        setInterimTranscript("");

        const resultObj: SpeechRecognitionResult = {
          transcript: final,
          confidence: event.results[event.results.length - 1][0].confidence,
          isFinal: true,
        };
        onResult?.(resultObj);
      }
    };

    recognition.onerror = (event) => {
      const errorInfo = getErrorMessage(event.error);

      // Don't treat 'aborted' as an error (user cancelled)
      if (event.error === "aborted") {
        return;
      }

      setError(errorInfo);
      setState(VoiceState.ERROR);
      onError?.(errorInfo);
    };

    recognition.onend = () => {
      isListeningRef.current = false;
      clearSilenceTimer();

      // Only set to IDLE if not in error state
      if (state !== VoiceState.ERROR) {
        setState(VoiceState.IDLE);
      }
      onEnd?.();
    };

    return recognition;
  }, [language, continuous, onResult, onError, onEnd, resetSilenceTimer, clearSilenceTimer, state]);

  /**
   * Start listening for speech.
   */
  const startListening = useCallback(() => {
    if (!isSupported) {
      setError({
        type: "service-not-allowed",
        message: "Speech recognition is not supported in this browser.",
        recoverable: false,
      });
      setState(VoiceState.ERROR);
      return;
    }

    // Stop any existing recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // Ignore abort errors
      }
    }

    // Reset state
    setInterimTranscript("");
    setFinalTranscript("");
    setError(null);

    // Create new recognition instance
    const recognition = initRecognition();
    if (!recognition) {
      setError({
        type: "service-not-allowed",
        message: "Could not initialize speech recognition.",
        recoverable: false,
      });
      setState(VoiceState.ERROR);
      return;
    }

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (err) {
      setError({
        type: "audio-capture",
        message: "Could not start speech recognition. Please try again.",
        recoverable: true,
      });
      setState(VoiceState.ERROR);
    }
  }, [isSupported, initRecognition]);

  /**
   * Stop listening and process final result.
   */
  const stopListening = useCallback(() => {
    clearSilenceTimer();
    if (recognitionRef.current && isListeningRef.current) {
      setState(VoiceState.PROCESSING);
      try {
        recognitionRef.current.stop();
      } catch {
        // Ignore stop errors
        setState(VoiceState.IDLE);
      }
    }
  }, [clearSilenceTimer]);

  /**
   * Cancel listening without processing.
   */
  const cancelListening = useCallback(() => {
    clearSilenceTimer();
    setInterimTranscript("");
    setFinalTranscript("");

    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // Ignore abort errors
      }
    }
    setState(VoiceState.IDLE);
    isListeningRef.current = false;
  }, [clearSilenceTimer]);

  /**
   * Reset all state.
   */
  const reset = useCallback(() => {
    cancelListening();
    setError(null);
  }, [cancelListening]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearSilenceTimer();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // Ignore
        }
      }
    };
  }, [clearSilenceTimer]);

  return {
    state,
    interimTranscript,
    finalTranscript,
    error,
    isSupported,
    startListening,
    stopListening,
    cancelListening,
    reset,
  };
}
