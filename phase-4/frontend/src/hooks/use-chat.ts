"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { chatApi, HistoryMessage, ChatResponse, ApiError } from "@/lib/chat-api";
import { useAuth } from "./use-auth";

// Query key factory for chat
export const chatKeys = {
  history: (userId: string) => ["chat", "history", userId] as const,
};

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: Date;
  isPending?: boolean;
  error?: string;
}

export interface UseChatOptions {
  onError?: (error: Error) => void;
}

export function useChat(options: UseChatOptions = {}) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messageIdCounter = useRef(0);

  const userId = user?.id;

  // Fetch conversation history
  const historyQuery = useQuery({
    queryKey: chatKeys.history(userId ?? ""),
    queryFn: () => chatApi.getHistory(userId!),
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Initialize messages from history
  useEffect(() => {
    if (historyQuery.data && !historyQuery.isLoading) {
      const historyMessages: ChatMessage[] = historyQuery.data.map((msg) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        createdAt: new Date(msg.created_at),
      }));
      setMessages(historyMessages);
    }
  }, [historyQuery.data, historyQuery.isLoading]);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!userId) {
        throw new Error("User not authenticated");
      }
      return chatApi.sendMessage(userId, message);
    },
    onMutate: async (message) => {
      // Clear any previous error
      setError(null);

      // Generate temporary ID for optimistic update
      const tempId = `temp-${++messageIdCounter.current}`;

      // Add user message optimistically
      const userMessage: ChatMessage = {
        id: tempId,
        role: "user",
        content: message,
        createdAt: new Date(),
        isPending: true,
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsTyping(true);

      return { tempId, message };
    },
    onSuccess: (response, message, context) => {
      setIsTyping(false);

      // Remove pending flag from user message
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === context?.tempId ? { ...msg, isPending: false } : msg
        )
      );

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: `assistant-${++messageIdCounter.current}`,
        role: "assistant",
        content: response.message,
        createdAt: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Invalidate tasks query if any task operations were performed
      if (response.tool_calls && response.tool_calls.length > 0) {
        const taskTools = ["add_task", "complete_task_toggle", "update_task", "delete_task"];
        const hasTaskChange = response.tool_calls.some(tc =>
          taskTools.includes(tc.tool_name)
        );
        if (hasTaskChange) {
          queryClient.invalidateQueries({ queryKey: ["tasks"] });
        }
      }
    },
    onError: (error, message, context) => {
      setIsTyping(false);

      // Determine appropriate error message
      let errorMessage = "Failed to send message. Please try again.";
      let messageError = "Failed to send";

      if (error instanceof ApiError) {
        if (error.status === 503) {
          errorMessage = "The AI service is temporarily unavailable. Please try again in a moment.";
          messageError = "Service unavailable";
        } else if (error.status === 401) {
          errorMessage = "Your session has expired. Please log in again.";
          messageError = "Session expired";
        } else {
          errorMessage = error.message;
        }
      }

      // Mark user message as failed
      if (context?.tempId) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === context.tempId
              ? { ...msg, isPending: false, error: messageError }
              : msg
          )
        );
      }

      setError(errorMessage);
      options.onError?.(error instanceof Error ? error : new Error(errorMessage));
    },
  });

  // Send message function
  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim()) return;
      if (!userId) {
        setError("Please log in to use the chat");
        return;
      }

      await sendMessageMutation.mutateAsync(message);
    },
    [userId, sendMessageMutation]
  );

  // Retry failed message
  const retryMessage = useCallback(
    async (messageId: string) => {
      const failedMessage = messages.find(
        (msg) => msg.id === messageId && msg.error
      );
      if (!failedMessage) return;

      // Remove the failed message
      setMessages((prev) => prev.filter((msg) => msg.id !== messageId));

      // Retry sending
      await sendMessage(failedMessage.content);
    },
    [messages, sendMessage]
  );

  // Clear chat (local only - doesn't delete from DB)
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  // Refresh history from server
  const refreshHistory = useCallback(() => {
    if (userId) {
      queryClient.invalidateQueries({ queryKey: chatKeys.history(userId) });
    }
  }, [userId, queryClient]);

  return {
    messages,
    isTyping,
    isLoading: historyQuery.isLoading,
    isSending: sendMessageMutation.isPending,
    error,
    sendMessage,
    retryMessage,
    clearChat,
    refreshHistory,
  };
}
