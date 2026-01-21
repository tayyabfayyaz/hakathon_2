import { createAuthClient } from "better-auth/react";

// Dynamically detect the base URL at runtime for containerized deployments
// This allows the auth to work regardless of which URL/port the app is accessed from
function getBaseURL(): string {
  // Server-side: use environment variable
  if (typeof window === "undefined") {
    return process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000";
  }
  // Client-side: use current origin (works with any URL/port)
  return window.location.origin;
}

export const authClient = createAuthClient({
  baseURL: getBaseURL(),
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

// Helper to get bearer token from Better-Auth
export async function getBearerToken(): Promise<string | null> {
  try {
    const response = await fetch("/api/auth/token", {
      method: "GET",
      credentials: "include",
    });
    if (response.ok) {
      const data = await response.json();
      return data.token || null;
    }
  } catch (error) {
    console.warn("Failed to get bearer token:", error);
  }
  return null;
}
