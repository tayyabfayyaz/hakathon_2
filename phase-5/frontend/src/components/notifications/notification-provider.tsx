"use client";

import { NotificationToastProvider } from "./notification-toast-provider";

interface NotificationProviderProps {
  children: React.ReactNode;
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  return (
    <>
      {children}
      <NotificationToastProvider />
    </>
  );
}
