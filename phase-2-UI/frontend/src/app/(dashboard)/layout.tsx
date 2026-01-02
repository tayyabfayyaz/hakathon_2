import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";

// Force dynamic rendering to prevent caching issues
export const dynamic = "force-dynamic";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Simplified layout - middleware handles auth, session check happens client-side if needed
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar isAuthenticated={true} userName="User" />
      <main className="flex-1 container py-8">{children}</main>
      <Footer />
    </div>
  );
}
