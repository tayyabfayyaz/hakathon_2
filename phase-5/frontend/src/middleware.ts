import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that require authentication
const protectedRoutes = ["/dashboard", "/chat"];

// Routes that should redirect to dashboard if already authenticated
const authRoutes = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for Better-Auth session cookie (check all possible variants)
  // Note: Real session validation happens in server components/layouts
  const sessionCookie =
    request.cookies.get("better-auth.session_token") ||
    request.cookies.get("__Secure-better-auth.session_token") ||
    request.cookies.get("better-auth.session_token.0") ||
    request.cookies.get("__Secure-better-auth.session_token.0");

  const hasSessionCookie = !!sessionCookie?.value;

  // Protect dashboard and chat routes - require session cookie
  // Actual session validation happens in the dashboard layout
  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    if (!hasSessionCookie) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // Redirect users with session cookie away from auth pages
  // If the session is invalid, the dashboard will redirect them back
  if (authRoutes.some((route) => pathname.startsWith(route))) {
    if (hasSessionCookie) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/chat/:path*", "/login", "/register"],
};
