"use client";

import { ChatContainer } from "@/components/chat/chat-container";

export default function ChatPage() {
  return (
    <div className="h-[calc(100vh-12rem)] max-w-4xl mx-auto">
      <ChatContainer className="h-full" />
    </div>
  );
}
