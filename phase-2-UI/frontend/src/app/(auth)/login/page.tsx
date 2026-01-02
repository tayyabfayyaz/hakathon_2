import { Suspense } from "react";
import { LoginForm } from "@/components/auth/login-form";
import { Metadata } from "next";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Login | TodoList Pro",
  description: "Sign in to your TodoList Pro account",
};

function LoginFormSkeleton() {
  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-4 text-center">
        <Skeleton className="h-8 w-32 mx-auto" />
        <Skeleton className="h-6 w-48 mx-auto" />
        <Skeleton className="h-4 w-64 mx-auto" />
      </CardHeader>
      <CardContent className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </CardContent>
    </Card>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginFormSkeleton />}>
      <LoginForm />
    </Suspense>
  );
}
