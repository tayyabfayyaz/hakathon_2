import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Only protect dashboard routes
  if (pathname.startsWith("/dashboard")) {
    // Check for Better-Auth session cookie (try all possible cookie names)
    // The cookie name depends on the cookiePrefix setting in auth.ts
    const sessionCookie =
      request.cookies.get("better-auth.session_token") ||
      request.cookies.get("better-auth.session") ||
      request.cookies.get("__Secure-better-auth.session_token") ||
      request.cookies.get("__Secure-better-auth.session");

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
