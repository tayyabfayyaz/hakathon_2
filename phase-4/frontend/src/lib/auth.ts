import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL?.includes('neon.tech') ? { rejectUnauthorized: false } : false,
});

// Parse trusted origins from environment (comma-separated) for K8s flexibility
const additionalOrigins = process.env.TRUSTED_ORIGINS?.split(",").map(o => o.trim()).filter(Boolean) || [];

// Static trusted origins for production
const staticOrigins = [
  "https://todoproweb.vercel.app",
  "https://fayyaztayyab684-todolist-pro-api.hf.space",
  process.env.BETTER_AUTH_URL,
  process.env.NEXT_PUBLIC_API_URL,
  "http://localhost:3000",
  "http://localhost:8000",
  ...additionalOrigins,
].filter(Boolean) as string[];

// Dynamic origin validator function for K8s/minikube deployments
// Allows any localhost or 127.0.0.1 origin regardless of port
function getTrustedOrigins(request?: Request): string[] {
  const origins = [...staticOrigins];

  if (request) {
    const origin = request.headers.get("origin");
    if (origin) {
      // Allow any localhost or 127.0.0.1 origin (for K8s/minikube)
      const isLocalhost = /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
      if (isLocalhost && !origins.includes(origin)) {
        origins.push(origin);
      }
    }
  }

  return origins;
}

export const auth = betterAuth({
  baseURL: process.env.BETTER_AUTH_URL,
  trustedOrigins: getTrustedOrigins,
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
