import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
import ErrorBoundary from '@/components/ErrorBoundary';
import Footer from '@/components/layout/Footer';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
});

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#4f46e5',
};

export const metadata: Metadata = {
  title: {
    default: 'TodoList Pro',
    template: '%s | TodoList Pro',
  },
  description: 'A modern, secure, and efficient todo list application for managing your tasks',
  keywords: ['todo', 'task manager', 'productivity', 'task list'],
  authors: [{ name: 'Tayyab Fayyaz' }],
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex flex-col min-h-screen`}>
        <ErrorBoundary>
          <AuthProvider>
            <main className="flex-1">
              {children}
            </main>
            <Footer />
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
