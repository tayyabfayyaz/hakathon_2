"use client";

import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { NotificationList } from "./notification-list";
import {
  useNotifications,
  useUnreadCount,
  useMarkAllAsRead,
  useNotificationWebSocket,
} from "@/hooks/use-notifications";
import { cn } from "@/lib/utils";

export function NotificationBell() {
  // Connect to WebSocket for real-time updates
  useNotificationWebSocket();

  const { data: notificationsData, isLoading } = useNotifications();
  const { data: unreadData } = useUnreadCount();
  const markAllAsRead = useMarkAllAsRead();

  const notifications = notificationsData?.notifications ?? [];
  const unreadCount = unreadData?.unread_count ?? 0;

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span
              className={cn(
                "absolute -top-1 -right-1 flex items-center justify-center",
                "min-w-[18px] h-[18px] px-1 rounded-full",
                "bg-destructive text-destructive-foreground",
                "text-xs font-medium"
              )}
            >
              {unreadCount > 99 ? "99+" : unreadCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-80 p-0">
        <div className="flex items-center justify-between p-3 border-b">
          <h3 className="font-semibold text-sm">Notifications</h3>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="text-xs h-7"
              onClick={() => markAllAsRead.mutate()}
              disabled={markAllAsRead.isPending}
            >
              Mark all as read
            </Button>
          )}
        </div>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : (
          <NotificationList notifications={notifications} />
        )}
      </PopoverContent>
    </Popover>
  );
}
