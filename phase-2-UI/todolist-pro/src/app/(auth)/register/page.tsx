import { RegisterForm } from "@/components/auth/register-form";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sign Up | TodoList Pro",
  description: "Create your TodoList Pro account",
};

export default function RegisterPage() {
  return <RegisterForm />;
}
