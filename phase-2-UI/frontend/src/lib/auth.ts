import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL?.includes('neon.tech') ? { rejectUnauthorized: false } : false,
});

const isProduction = process.env.NODE_ENV === "production";

// Use BETTER_AUTH_URL if set, otherwise fall back to NEXT_PUBLIC_BETTER_AUTH_URL
const baseURL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000";

export const auth = betterAuth({
  database: pool,
  baseURL,
  trustedOrigins: isProduction
    ? [
        "https://frontend-ten-liard-39.vercel.app",
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
    useSecureCookies: isProduction,
    defaultCookieAttributes: {
      sameSite: "lax" as const,
      httpOnly: true,
      secure: isProduction,
      path: "/",
    },
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
