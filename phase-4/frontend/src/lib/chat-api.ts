/**
 * Chat API client for Phase-3 AI Chatbot
 */

import { apiClient, ApiError } from "./api";

export interface ToolCallResult {
  tool_name: string;
  result: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  tool_calls: ToolCallResult[] | null;
}

export interface HistoryMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatHistoryResponse {
  messages: HistoryMessage[];
  count: number;
}

export interface ChatError {
  error: string;
  code?: string;
}

/**
 * Send a message to the AI chatbot and receive a response.
 *
 * @param userId - User ID (must match JWT token)
 * @param message - User's natural language message
 * @returns Promise with AI response and any tool calls made
 */
export async function sendMessage(
  userId: string,
  message: string
): Promise<ChatResponse> {
  return apiClient<ChatResponse>(`/${userId}/chat`, {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

/**
 * Get conversation history for the user.
 *
 * @param userId - User ID (must match JWT token)
 * @param limit - Maximum number of messages to return (default: 50)
 * @returns Promise with conversation history
 */
export async function getHistory(
  userId: string,
  limit: number = 50
): Promise<HistoryMessage[]> {
  const response = await apiClient<ChatHistoryResponse>(
    `/${userId}/chat/history?limit=${limit}`
  );
  return response.messages;
}

/**
 * Chat API object with all chat-related functions
 */
export const chatApi = {
  sendMessage,
  getHistory,
};

export { ApiError };
