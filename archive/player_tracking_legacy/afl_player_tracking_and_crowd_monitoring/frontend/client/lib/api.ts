import { getFriendlyErrorMessage } from "./errors";

export async function apiRequest(
    url: string,
    options: RequestInit = {},
) {
    const token = localStorage.getItem("accessToken");

    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(options.headers || {}),
        },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(getFriendlyErrorMessage(data));
    }

    return data;
}