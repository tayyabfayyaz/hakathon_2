"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  whatsappApi,
  WhatsAppStatus,
  WhatsAppRegisterRequest,
  WhatsAppVerifyRequest,
} from "@/lib/api";

// Query key factory
export const whatsappKeys = {
  status: ["whatsapp", "status"] as const,
};

// Hook to fetch WhatsApp status
export function useWhatsAppStatus() {
  return useQuery({
    queryKey: whatsappKeys.status,
    queryFn: whatsappApi.getStatus,
    staleTime: 60 * 1000, // 1 minute
    retry: false,
  });
}

// Hook to register WhatsApp number
export function useRegisterWhatsApp() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WhatsAppRegisterRequest) => whatsappApi.register(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: whatsappKeys.status });
    },
  });
}

// Hook to verify WhatsApp with OTP
export function useVerifyWhatsApp() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WhatsAppVerifyRequest) => whatsappApi.verify(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: whatsappKeys.status });
    },
  });
}

// Hook to resend verification code
export function useResendVerification() {
  return useMutation({
    mutationFn: () => whatsappApi.resend(),
  });
}

// Hook to delete WhatsApp registration
export function useDeleteWhatsApp() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => whatsappApi.delete(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: whatsappKeys.status });
    },
  });
}
