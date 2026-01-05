import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Only protect dashboard routes
  if (pathname.startsWith("/dashboard")) {
    // Check for Better-Auth session cookie (try both possible cookie names)
    const sessionCookie =
      request.cookies.get("better-auth.session_token") ||
      request.cookies.get("better-auth.session");

    const isAuthenticated = !!sessionCookie?.value;

    if (!isAuthenticated) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl, { status: 302 });
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
