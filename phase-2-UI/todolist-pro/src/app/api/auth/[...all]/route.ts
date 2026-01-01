import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest } from "next/server";

const handlers = toNextJsHandler(auth);

export const GET = handlers.GET;

export async function POST(request: NextRequest) {
  // Clone the request to log the body
  const clonedRequest = request.clone();
  try {
    const body = await clonedRequest.json();
    console.log("[Auth API] POST request body:", JSON.stringify(body, null, 2));
  } catch (e) {
    console.log("[Auth API] Could not parse body:", e);
  }

  return handlers.POST(request);
}
