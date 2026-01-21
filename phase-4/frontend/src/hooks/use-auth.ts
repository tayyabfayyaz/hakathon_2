"use client";

import { useSession, signOut } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useCallback } from "react";

export function useAuth() {
  const { data: session, isPending, error } = useSession();
  const router = useRouter();

  const logout = useCallback(async () => {
    try {
      // Clear bearer token from localStorage
      if (typeof window !== "undefined") {
        localStorage.removeItem("bearer_token");
      }

      // Sign out from Better-Auth
      await signOut();

      // Redirect to home page
      router.push("/");
    } catch (err) {
      console.error("Logout failed:", err);
      // Even if signOut fails, clear local data and redirect
      if (typeof window !== "undefined") {
        localStorage.removeItem("bearer_token");
      }
      router.push("/");
    }
  }, [router]);

  return {
    user: session?.user ?? null,
    session: session?.session ?? null,
    isLoading: isPending,
    isAuthenticated: !!session?.user,
    error,
    logout,
  };
}
