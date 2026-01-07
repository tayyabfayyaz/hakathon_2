import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Only protect dashboard routes
  if (pathname.startsWith("/dashboard")) {
    // Check for Better-Auth session cookie
    // Cookie name is "better-auth.session_token" (useSecureCookies is disabled for consistency)
    const sessionCookie = request.cookies.get("better-auth.session_token");

    // Debug logging for production (remove in future if not needed)
    if (process.env.NODE_ENV === "production") {
      const allCookies = request.cookies.getAll();
      console.log("[Middleware] Checking auth for:", pathname);
      console.log("[Middleware] All cookies:", allCookies.map(c => c.name));
      console.log("[Middleware] Session cookie found:", !!sessionCookie?.value);
    }

    const isAuthenticated = !!sessionCookie?.value;

    if (!isAuthenticated) {
      // Build the login URL with callback
      const loginUrl = new URL("/login", request.url);
      // Use the full pathname for callback
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl, { status: 302 });
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
