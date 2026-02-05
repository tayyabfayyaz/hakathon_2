import { NextResponse } from "next/server";

/**
 * Health check endpoint for Kubernetes liveness/readiness probes
 * GET /api/health
 */
export async function GET() {
  return NextResponse.json(
    {
      status: "healthy",
      timestamp: new Date().toISOString(),
      service: "todolist-frontend",
    },
    { status: 200 }
  );
}
