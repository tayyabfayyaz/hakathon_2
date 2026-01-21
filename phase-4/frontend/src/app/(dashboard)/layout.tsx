import { redirect } from "next/navigation";
import { headers } from "next/headers";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { auth } from "@/lib/auth";

// Force dynamic rendering to prevent caching issues
export const dynamic = "force-dynamic";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Server-side session validation - redirect if not authenticated
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session || !session.user) {
    // User is not authenticated, redirect to login
    redirect("/login");
  }

  const userName = session.user.name || session.user.email || "User";

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar isAuthenticated={true} userName={userName} />
      <main className="flex-1 container py-8">{children}</main>
      <Footer />
    </div>
  );
}
