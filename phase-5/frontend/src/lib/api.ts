const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public data: { detail?: string; [key: string]: unknown }
  ) {
    super(data.detail || "An error occurred");
    this.name = "ApiError";
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("bearer_token") : null;

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Unknown error" }));

    // Handle session expiry - don't auto-redirect, let components handle it
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("bearer_token");
      }
    }

    throw new ApiError(response.status, error);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Task API functions
export interface TaskCreate {
  text: string;
}

export interface TaskUpdate {
  text?: string;
  completed?: boolean;
}

export interface Task {
  id: string;
  task_number: number;  // Short random ID for voice/chat agents (e.g., 4521)
  user_id: string;
  text: string;
  description: string | null;
  completed: boolean;
  deadline: string | null;  // ISO datetime string
  order: number;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface DeadlineRequest {
  deadline: string;  // ISO datetime string
}

export interface DeadlineResponse {
  task_id: string;
  deadline: string | null;
  message: string;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

export const tasksApi = {
  getAll: async (): Promise<Task[]> => {
    const response = await apiClient<TaskListResponse>("/tasks");
    return response.tasks;
  },

  getById: (id: string) => apiClient<Task>(`/tasks/${id}`),

  getByNumber: (taskNumber: number) => apiClient<Task>(`/tasks/by-number/${taskNumber}`),

  create: (data: TaskCreate) =>
    apiClient<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: TaskUpdate) =>
    apiClient<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiClient<void>(`/tasks/${id}`, {
      method: "DELETE",
    }),

  toggle: (id: string, completed: boolean) =>
    apiClient<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    }),

  setDeadline: (id: string, deadline: string) =>
    apiClient<DeadlineResponse>(`/tasks/${id}/deadline`, {
      method: "PUT",
      body: JSON.stringify({ deadline }),
    }),

  removeDeadline: (id: string) =>
    apiClient<DeadlineResponse>(`/tasks/${id}/deadline`, {
      method: "DELETE",
    }),
};

// WhatsApp API
export interface WhatsAppStatus {
  registered: boolean;
  verified: boolean;
  phone_number: string | null;
}

export interface WhatsAppRegisterRequest {
  phone_number: string;
  country_code: string;
}

export interface WhatsAppVerifyRequest {
  code: string;
}

export interface WhatsAppVerificationResponse {
  success: boolean;
  message: string;
  verified_at: string | null;
}

export interface WhatsAppResendResponse {
  success: boolean;
  message: string;
  expires_in_minutes: number;
}

export const whatsappApi = {
  getStatus: () => apiClient<WhatsAppStatus>("/users/me/whatsapp"),

  register: (data: WhatsAppRegisterRequest) =>
    apiClient<WhatsAppStatus>("/users/me/whatsapp", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  verify: (data: WhatsAppVerifyRequest) =>
    apiClient<WhatsAppVerificationResponse>("/users/me/whatsapp/verify", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  resend: () =>
    apiClient<WhatsAppResendResponse>("/users/me/whatsapp/resend", {
      method: "POST",
    }),

  delete: () =>
    apiClient<void>("/users/me/whatsapp", {
      method: "DELETE",
    }),
};

// Reminder Preferences API
export interface ReminderPreferences {
  id: string;
  user_id: string;
  enabled: boolean;
  default_intervals: string[];
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface ReminderPreferencesUpdate {
  enabled?: boolean;
  default_intervals?: string[];
  timezone?: string;
}

export const preferencesApi = {
  get: () => apiClient<ReminderPreferences>("/users/me/reminder-preferences"),

  update: (data: ReminderPreferencesUpdate) =>
    apiClient<ReminderPreferences>("/users/me/reminder-preferences", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// Reminder History API
export interface ReminderLog {
  id: string;
  scheduled_reminder_id: string | null;
  task_id: string;
  user_id: string;
  phone_number: string;
  message_content: string;
  sent_at: string;
  delivery_status: "sent" | "delivered" | "failed" | "read";
  whatsapp_message_id: string | null;
  error_message: string | null;
  created_at: string;
}

export interface ReminderHistoryResponse {
  logs: ReminderLog[];
  count: number;
  total_sent: number;
  total_delivered: number;
  total_failed: number;
}

export interface ScheduledReminder {
  id: string;
  task_id: string;
  user_id: string;
  scheduled_for: string;
  reminder_interval: string;
  status: "pending" | "sent" | "failed" | "cancelled";
  celery_task_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskRemindersResponse {
  task_id: string;
  scheduled: ScheduledReminder[];
  history: ReminderLog[];
}

export const remindersApi = {
  getHistory: (limit = 50, offset = 0) =>
    apiClient<ReminderHistoryResponse>(
      `/users/me/reminders/history?limit=${limit}&offset=${offset}`
    ),

  getTaskReminders: (taskId: string) =>
    apiClient<TaskRemindersResponse>(`/tasks/${taskId}/reminders`),
};

// Notification Types
export type NotificationType =
  | "deadline_reminder"
  | "deadline_reached"
  | "task_overdue"
  | "system";

export type NotificationStatus = "pending" | "sent" | "read" | "dismissed";

export interface Notification {
  id: string;
  user_id: string;
  task_id: string | null;
  type: NotificationType;
  title: string;
  message: string;
  status: NotificationStatus;
  read_at: string | null;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  count: number;
  unread_count: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkAsReadRequest {
  notification_ids: string[];
}

export interface MarkAsReadResponse {
  marked_count: number;
  message: string;
}

// Notification API
export const notificationsApi = {
  getAll: (unreadOnly = false, limit = 50, offset = 0) =>
    apiClient<NotificationListResponse>(
      `/notifications?unread_only=${unreadOnly}&limit=${limit}&offset=${offset}`
    ),

  getUnreadCount: () => apiClient<UnreadCountResponse>("/notifications/unread-count"),

  markAsRead: (notificationIds: string[]) =>
    apiClient<MarkAsReadResponse>("/notifications/mark-read", {
      method: "POST",
      body: JSON.stringify({ notification_ids: notificationIds }),
    }),

  markAllAsRead: () =>
    apiClient<MarkAsReadResponse>("/notifications/mark-all-read", {
      method: "POST",
    }),

  dismiss: (id: string) =>
    apiClient<void>(`/notifications/${id}`, {
      method: "DELETE",
    }),
};
