"use client";

import { useEffect, useRef, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  notificationsApi,
  Notification,
  NotificationListResponse,
} from "@/lib/api";

// Query key factory
export const notificationKeys = {
  all: ["notifications"] as const,
  unreadCount: ["notifications", "unread-count"] as const,
};

// Custom event for new notifications (for toast provider)
export const NEW_NOTIFICATION_EVENT = "new-notification";

export function dispatchNewNotification(notification: Notification) {
  if (typeof window !== "undefined") {
    window.dispatchEvent(
      new CustomEvent(NEW_NOTIFICATION_EVENT, { detail: notification })
    );
  }
}

// WebSocket connection state
type WebSocketState = "connecting" | "connected" | "disconnected" | "error";

// Hook to manage WebSocket connection for real-time notifications
export function useNotificationWebSocket() {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    const token = localStorage.getItem("bearer_token");
    if (!token) {
      console.log("No auth token, skipping WebSocket connection");
      return;
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const url = `${wsUrl}/ws/notifications?token=${encodeURIComponent(token)}`;

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log("WebSocket connected");
        reconnectAttemptsRef.current = 0;
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === "new_notification") {
            const notification = message.payload as Notification;

            // Update notifications list cache
            queryClient.setQueryData<NotificationListResponse>(
              notificationKeys.all,
              (old) => {
                if (!old) return old;
                return {
                  ...old,
                  notifications: [notification, ...old.notifications],
                  count: old.count + 1,
                  unread_count: old.unread_count + 1,
                };
              }
            );

            // Invalidate unread count
            queryClient.invalidateQueries({
              queryKey: notificationKeys.unreadCount,
            });

            // Dispatch custom event for toast
            dispatchNewNotification(notification);
          } else if (message.type === "notification_read") {
            // Invalidate to refetch
            queryClient.invalidateQueries({
              queryKey: notificationKeys.all,
            });
            queryClient.invalidateQueries({
              queryKey: notificationKeys.unreadCount,
            });
          } else if (message.type === "all_read") {
            queryClient.invalidateQueries({
              queryKey: notificationKeys.all,
            });
            queryClient.invalidateQueries({
              queryKey: notificationKeys.unreadCount,
            });
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log("WebSocket closed:", event.code, event.reason);
        wsRef.current = null;

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttemptsRef.current),
            30000
          );
          console.log(`Reconnecting in ${delay}ms...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
    }
  }, [queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { connect, disconnect };
}

// Hook to fetch notifications
export function useNotifications(unreadOnly = false) {
  return useQuery({
    queryKey: notificationKeys.all,
    queryFn: () => notificationsApi.getAll(unreadOnly),
    staleTime: 30 * 1000,
  });
}

// Hook to fetch unread count
export function useUnreadCount() {
  return useQuery({
    queryKey: notificationKeys.unreadCount,
    queryFn: notificationsApi.getUnreadCount,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000, // Refetch every minute as fallback
  });
}

// Hook to mark notifications as read
export function useMarkAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationIds: string[]) =>
      notificationsApi.markAsRead(notificationIds),
    onMutate: async (notificationIds) => {
      await queryClient.cancelQueries({ queryKey: notificationKeys.all });

      const previousData = queryClient.getQueryData<NotificationListResponse>(
        notificationKeys.all
      );

      if (previousData) {
        const now = new Date().toISOString();
        queryClient.setQueryData<NotificationListResponse>(
          notificationKeys.all,
          {
            ...previousData,
            notifications: previousData.notifications.map((n) =>
              notificationIds.includes(n.id)
                ? { ...n, status: "read" as const, read_at: now }
                : n
            ),
            unread_count: Math.max(
              0,
              previousData.unread_count - notificationIds.length
            ),
          }
        );
      }

      return { previousData };
    },
    onError: (err, variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData<NotificationListResponse>(
          notificationKeys.all,
          context.previousData
        );
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all });
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount });
    },
  });
}

// Hook to mark all notifications as read
export function useMarkAllAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notificationsApi.markAllAsRead,
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: notificationKeys.all });

      const previousData = queryClient.getQueryData<NotificationListResponse>(
        notificationKeys.all
      );

      if (previousData) {
        const now = new Date().toISOString();
        queryClient.setQueryData<NotificationListResponse>(
          notificationKeys.all,
          {
            ...previousData,
            notifications: previousData.notifications.map((n) => ({
              ...n,
              status: "read" as const,
              read_at: now,
            })),
            unread_count: 0,
          }
        );
      }

      return { previousData };
    },
    onError: (err, variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData<NotificationListResponse>(
          notificationKeys.all,
          context.previousData
        );
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all });
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount });
    },
  });
}

// Hook to dismiss a notification
export function useDismissNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => notificationsApi.dismiss(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: notificationKeys.all });

      const previousData = queryClient.getQueryData<NotificationListResponse>(
        notificationKeys.all
      );

      if (previousData) {
        const notification = previousData.notifications.find((n) => n.id === id);
        const wasUnread = notification?.status !== "read";

        queryClient.setQueryData<NotificationListResponse>(
          notificationKeys.all,
          {
            ...previousData,
            notifications: previousData.notifications.filter((n) => n.id !== id),
            count: previousData.count - 1,
            unread_count: wasUnread
              ? previousData.unread_count - 1
              : previousData.unread_count,
          }
        );
      }

      return { previousData };
    },
    onError: (err, id, context) => {
      if (context?.previousData) {
        queryClient.setQueryData<NotificationListResponse>(
          notificationKeys.all,
          context.previousData
        );
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all });
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount });
    },
  });
}
