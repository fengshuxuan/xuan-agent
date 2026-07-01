export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type AuthResponse = {
  access_token: string;
  token_type: string;
};

export type SessionRead = {
  id: string;
  title: string;
  workspace_id: string;
  status: string;
};

export type ChatResponse = {
  session_id: string;
  reply: string;
  tool_calls: Array<{
    tool_name: string;
    status: string;
    input_summary?: string;
    output_summary?: string;
    error_message?: string;
  }>;
  files: Array<{
    file_id: string;
    name: string;
    download_url: string;
  }>;
};

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function register(email: string, password: string, displayName?: string) {
  return request<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name: displayName }),
  });
}

export function login(email: string, password: string) {
  return request<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function createSession(token: string, title = "New Chat") {
  return request<SessionRead>("/api/sessions", {
    method: "POST",
    body: JSON.stringify({ title }),
  }, token);
}

export function sendChat(token: string, sessionId: string, message: string) {
  return request<ChatResponse>(`/api/sessions/${sessionId}/chat`, {
    method: "POST",
    body: JSON.stringify({ message }),
  }, token);
}

export async function uploadFile(token: string, sessionId: string, file: File) {
  const formData = new FormData();
  formData.append("uploaded_file", file);
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/files`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function downloadFile(token: string, downloadUrl: string, filename: string) {
  const response = await fetch(`${API_BASE_URL}${downloadUrl}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
