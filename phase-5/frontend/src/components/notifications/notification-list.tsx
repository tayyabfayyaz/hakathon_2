"use client";

import { formatDistanceToNow } from "date-fns";
import { Bell, Clock, AlertTriangle, Info, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Notification, NotificationType } from "@/lib/api";
import { useMarkAsRead, useDismissNotification } from "@/hooks/use-notifications";
import { cn } from "@/lib/utils";

interface NotificationListProps {
  notifications: Notification[];
  onNotificationClick?: (notification: Notification) => void;
}

function getNotificationIcon(type: NotificationType) {
  switch (type) {
    case "deadline_reminder":
      return <Clock className="h-4 w-4 text-blue-500" />;
    case "deadline_reached":
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    case "task_overdue":
      return <AlertTriangle className="h-4 w-4 text-red-500" />;
    case "system":
    default:
      return <Info className="h-4 w-4 text-gray-500" />;
  }
}

function getNotificationStyles(type: NotificationType) {
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

export function NotificationList({
  notifications,
  onNotificationClick,
}: NotificationListProps) {
  const markAsRead = useMarkAsRead();
  const dismissNotification = useDismissNotification();

  const handleMarkAsRead = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    markAsRead.mutate([id]);
  };

  const handleDismiss = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    dismissNotification.mutate(id);
  };

  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <Bell className="h-10 w-10 text-muted-foreground/50 mb-2" />
        <p className="text-sm text-muted-foreground">No notifications</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col max-h-[400px] overflow-y-auto">
      {notifications.map((notification) => {
        const isUnread = notification.status !== "read";

        return (
          <div
            key={notification.id}
            className={cn(
              "flex items-start gap-3 p-3 border-l-4 cursor-pointer transition-colors",
              "hover:bg-accent/50",
              isUnread ? "bg-accent/20" : "bg-background",
              getNotificationStyles(notification.type)
            )}
            onClick={() => {
              if (isUnread) {
                markAsRead.mutate([notification.id]);
              }
              onNotificationClick?.(notification);
            }}
          >
            <div className="flex-shrink-0 mt-0.5">
              {getNotificationIcon(notification.type)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <p
                  className={cn(
                    "text-sm font-medium truncate",
                    isUnread && "font-semibold"
                  )}
                >
                  {notification.title}
                </p>
                {isUnread && (
                  <span className="flex-shrink-0 h-2 w-2 rounded-full bg-primary" />
                )}
              </div>

              <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                {notification.message}
              </p>

              <p className="text-xs text-muted-foreground mt-1">
                {formatDistanceToNow(new Date(notification.created_at), {
                  addSuffix: true,
                })}
              </p>
            </div>

            <div className="flex-shrink-0 flex items-center gap-1">
              {isUnread && (
                <Button
                  variant="ghost"
                  size="icon-sm"
                  className="h-6 w-6"
                  onClick={(e) => handleMarkAsRead(e, notification.id)}
                  title="Mark as read"
                >
                  <Check className="h-3 w-3" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon-sm"
                className="h-6 w-6 text-muted-foreground hover:text-destructive"
                onClick={(e) => handleDismiss(e, notification.id)}
                title="Dismiss"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
