import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";
import { Pool } from "pg";

const isProduction = process.env.NODE_ENV === "production";

// Validate required environment variables in production
if (isProduction) {
  if (!process.env.BETTER_AUTH_SECRET) {
    console.error("CRITICAL: BETTER_AUTH_SECRET is not set in production!");
  }
  if (!process.env.DATABASE_URL) {
    console.error("CRITICAL: DATABASE_URL is not set in production!");
  }
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL?.includes('neon.tech') ? { rejectUnauthorized: false } : false,
});

// Use BETTER_AUTH_URL if set, otherwise fall back to NEXT_PUBLIC_BETTER_AUTH_URL
const baseURL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000";

// Production domain for cookie settings
const productionDomain = "frontend-ten-liard-39.vercel.app";

export const auth = betterAuth({
  database: pool,
  baseURL,
  secret: process.env.BETTER_AUTH_SECRET,
  trustedOrigins: isProduction
    ? [
        `https://${productionDomain}`,
        process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "",
      ].filter(Boolean)
    : ["http://localhost:3000"],
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  plugins: [bearer()],
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  advanced: {
    cookiePrefix: "better-auth",
    // Disable __Secure- prefix to ensure consistent cookie names across environments
    useSecureCookies: false,
    defaultCookieAttributes: {
      sameSite: "lax" as const,
      httpOnly: true,
      secure: isProduction, // Still use HTTPS-only in production
      path: "/",
    },
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
