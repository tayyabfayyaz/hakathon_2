"use client";

import { useEffect, useState, useCallback } from "react";
import { Bell, X, Clock, AlertTriangle, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Notification, NotificationType } from "@/lib/api";
import { NEW_NOTIFICATION_EVENT } from "@/hooks/use-notifications";
import { cn } from "@/lib/utils";

interface Toast {
  id: string;
  notification: Notification;
  visible: boolean;
}

function getNotificationIcon(type: NotificationType) {
  switch (type) {
    case "deadline_reminder":
      return <Clock className="h-5 w-5 text-blue-500" />;
    case "deadline_reached":
      return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    case "task_overdue":
      return <AlertTriangle className="h-5 w-5 text-red-500" />;
    case "system":
    default:
      return <Info className="h-5 w-5 text-gray-500" />;
  }
}

function getToastStyles(type: NotificationType) {
  switch (type) {
    case "deadline_reminder":
      return "border-l-blue-500";
    case "deadline_reached":
      return "border-l-yellow-500";
    case "task_overdue":
      return "border-l-red-500";
    case "system":
    default:
      return "border-l-gray-500";
  }
}

const TOAST_DURATION = 5000; // 5 seconds

export function NotificationToastProvider() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    // First hide it with animation
    setToasts((prev) =>
      prev.map((t) => (t.id === id ? { ...t, visible: false } : t))
    );
    // Then remove after animation
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 300);
  }, []);

  const addToast = useCallback(
    (notification: Notification) => {
      const id = `toast-${notification.id}-${Date.now()}`;
      setToasts((prev) => [...prev, { id, notification, visible: true }]);

      // Auto-remove after duration
      setTimeout(() => {
        removeToast(id);
      }, TOAST_DURATION);
    },
    [removeToast]
  );

  useEffect(() => {
    const handleNewNotification = (event: CustomEvent<Notification>) => {
      addToast(event.detail);
    };

    window.addEventListener(
      NEW_NOTIFICATION_EVENT,
      handleNewNotification as EventListener
    );

    return () => {
      window.removeEventListener(
        NEW_NOTIFICATION_EVENT,
        handleNewNotification as EventListener
      );
    };
  }, [addToast]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "pointer-events-auto w-80 bg-background border rounded-lg shadow-lg",
            "border-l-4 overflow-hidden",
            "transition-all duration-300 ease-out",
            toast.visible
              ? "translate-x-0 opacity-100"
              : "translate-x-full opacity-0",
            getToastStyles(toast.notification.type)
          )}
        >
          <div className="flex items-start gap-3 p-4">
            <div className="flex-shrink-0">
              {getNotificationIcon(toast.notification.type)}
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate">
                {toast.notification.title}
              </p>
              <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                {toast.notification.message}
              </p>
            </div>

            <Button
              variant="ghost"
              size="icon-sm"
              className="flex-shrink-0 h-6 w-6"
              onClick={() => removeToast(toast.id)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Progress bar */}
          <div className="h-1 bg-muted">
            <div
              className="h-full bg-primary transition-all ease-linear"
              style={{
                animation: `shrink ${TOAST_DURATION}ms linear forwards`,
              }}
            />
          </div>
        </div>
      ))}

      <style jsx>{`
        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
      `}</style>
    </div>
  );
}
