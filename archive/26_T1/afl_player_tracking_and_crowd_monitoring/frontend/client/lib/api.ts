import { getAccessToken } from "./auth";
import { getFriendlyErrorMessage } from "./errors";

export async function apiRequest(
  url: string,
  options: RequestInit = {},
) {
  const token = getAccessToken();

  const isFormData = options.body instanceof FormData;

  const headers = new Headers(options.headers || {});

  // Only set JSON content type when the request is not FormData.
  // For FormData, the browser must generate the multipart boundary itself.
  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(getFriendlyErrorMessage(data));
  }

  return data;
}