"use client";

import { ChatContainer } from "@/components/chat/chat-container";

export default function ChatPage() {
  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background to-muted">
      <div className="flex-1 flex items-center justify-center animate-fade-in">
        <div className="w-full max-w-4xl h-full max-h-[calc(100vh-4rem)] p-4">
          <ChatContainer className="h-full shadow-2xl" />
        </div>
      </div>
    </div>
  );
}
