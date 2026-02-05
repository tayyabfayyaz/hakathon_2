/**
 * Voice Assistant TypeScript types and interfaces.
 *
 * Defines types for Web Speech API integration including
 * speech recognition and speech synthesis.
 */

/**
 * Voice system state enum for tracking UI and processing states.
 */
export enum VoiceState {
  /** No voice activity, ready for input */
  IDLE = "idle",
  /** Actively listening for speech input */
  LISTENING = "listening",
  /** Processing speech to text */
  PROCESSING = "processing",
  /** Speaking response via TTS */
  SPEAKING = "speaking",
  /** Error occurred during voice operation */
  ERROR = "error",
}

/**
 * Speech recognition result from Web Speech API.
 */
export interface SpeechRecognitionResult {
  /** Transcribed text */
  transcript: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Whether this is the final result or interim */
  isFinal: boolean;
}

/**
 * Speech recognition error types from Web Speech API.
 */
export type SpeechRecognitionErrorType =
  | "no-speech"
  | "audio-capture"
  | "not-allowed"
  | "network"
  | "aborted"
  | "service-not-allowed"
  | "bad-grammar"
  | "language-not-supported";

/**
 * Speech recognition error with user-friendly message.
 */
export interface SpeechRecognitionError {
  /** Error type from Web Speech API */
  type: SpeechRecognitionErrorType;
  /** User-friendly error message */
  message: string;
  /** Whether the error is recoverable */
  recoverable: boolean;
}

/**
 * Browser voice information from SpeechSynthesis API.
 */
export interface VoiceInfo {
  /** Voice URI identifier */
  voiceURI: string;
  /** Human-readable voice name */
  name: string;
  /** Language code (e.g., 'en-US') */
  lang: string;
  /** Whether this is the default voice */
  default: boolean;
  /** Whether this is a local voice */
  localService: boolean;
}

/**
 * User voice preferences synced with backend.
 */
export interface VoicePreferences {
  /** User ID */
  userId: string;
  /** Whether AI responses should be spoken aloud */
  voiceOutputEnabled: boolean;
  /** Whether continuous listening mode is active */
  continuousModeEnabled: boolean;
  /** Selected browser voice URI for TTS */
  preferredVoice: string | null;
  /** Last update timestamp */
  updatedAt: string;
}

/**
 * Voice preferences update request.
 */
export interface VoicePreferencesUpdate {
  voiceOutputEnabled?: boolean;
  continuousModeEnabled?: boolean;
  preferredVoice?: string | null;
}

/**
 * Input method for chat messages.
 */
export type InputMethod = "text" | "voice";

/**
 * Extended Web Speech API types for TypeScript.
 * These extend the built-in types to provide better type safety.
 */

/**
 * SpeechRecognition interface extension.
 */
export interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: ISpeechRecognitionEvent) => void) | null;
  onerror: ((event: ISpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
  onspeechstart: (() => void) | null;
  onspeechend: (() => void) | null;
  onaudiostart: (() => void) | null;
  onaudioend: (() => void) | null;
}

/**
 * SpeechRecognition event interface.
 */
export interface ISpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: ISpeechRecognitionResultList;
}

/**
 * SpeechRecognition result list interface.
 */
export interface ISpeechRecognitionResultList {
  length: number;
  item(index: number): ISpeechRecognitionResult;
  [index: number]: ISpeechRecognitionResult;
}

/**
 * SpeechRecognition result interface.
 */
export interface ISpeechRecognitionResult {
  length: number;
  isFinal: boolean;
  item(index: number): ISpeechRecognitionAlternative;
  [index: number]: ISpeechRecognitionAlternative;
}

/**
 * SpeechRecognition alternative interface.
 */
export interface ISpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

/**
 * SpeechRecognition error event interface.
 */
export interface ISpeechRecognitionErrorEvent extends Event {
  error: SpeechRecognitionErrorType;
  message: string;
}

/**
 * Global window type extension for Web Speech API.
 */
declare global {
  interface Window {
    SpeechRecognition?: new () => ISpeechRecognition;
    webkitSpeechRecognition?: new () => ISpeechRecognition;
  }
}
