import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL?.includes('neon.tech') ? { rejectUnauthorized: false } : false,
});

export const auth = betterAuth({
  baseURL: process.env.BETTER_AUTH_URL,
  trustedOrigins: [
    "https://todoproweb.vercel.app",
    "https://fayyaztayyab684-todolist-pro-api.hf.space",
    process.env.BETTER_AUTH_URL,
    process.env.NEXT_PUBLIC_API_URL,
    "http://localhost:3000",
    "http://localhost:8000",
  ].filter(Boolean) as string[],
  database: pool,
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  plugins: [bearer()],
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours
  },
  advanced: {
    useSecureCookies: false, // Disable __Secure- prefix to fix Vercel cookie issues
    cookiePrefix: "better-auth",
    crossSubDomainCookies: {
      enabled: false,
    },
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
