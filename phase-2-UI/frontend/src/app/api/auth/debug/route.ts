import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function GET(request: NextRequest) {
  const cookieStore = await cookies();
  const allCookies = cookieStore.getAll();

  // Check environment configuration (don't expose actual values)
  const config = {
    NODE_ENV: process.env.NODE_ENV,
    BETTER_AUTH_SECRET_SET: !!process.env.BETTER_AUTH_SECRET,
    DATABASE_URL_SET: !!process.env.DATABASE_URL,
    BETTER_AUTH_URL: process.env.BETTER_AUTH_URL || "not set",
    NEXT_PUBLIC_BETTER_AUTH_URL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "not set",
  };

  // List cookie names (not values for security)
  const cookieNames = allCookies.map(c => ({
    name: c.name,
    hasValue: !!c.value,
  }));

  // Check for session cookie specifically
  const sessionCookie = allCookies.find(c => c.name === "better-auth.session_token");

  return NextResponse.json({
    status: "debug",
    timestamp: new Date().toISOString(),
    config,
    cookies: cookieNames,
    hasSessionCookie: !!sessionCookie,
    warnings: [
      !process.env.BETTER_AUTH_SECRET && "CRITICAL: BETTER_AUTH_SECRET is not set!",
      !process.env.DATABASE_URL && "CRITICAL: DATABASE_URL is not set!",
    ].filter(Boolean),
  });
}
