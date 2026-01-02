import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { QueryProvider } from "@/components/providers/query-provider";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TodoList Pro - Professional Task Management",
  description:
    "Stay focused, organized, and in control. TodoList Pro helps you manage tasks efficiently with a beautiful, intuitive interface designed for productivity.",
  keywords: ["todo", "task management", "productivity", "organization", "tasks"],
  authors: [{ name: "Tayyab Fayyaz" }],
  openGraph: {
    title: "TodoList Pro - Professional Task Management",
    description:
      "Stay focused, organized, and in control with TodoList Pro.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
