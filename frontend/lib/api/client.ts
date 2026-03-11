import "server-only";

import {
  buildQueryString,
  normalizeApiError,
  parseAnalyticsEnvelope,
  parseDirectModel,
  parsePaginatedEnvelope,
  parseWrappedData,
  readJson,
} from "@/lib/api/normalizers";
import type {
  AnalyticsEnvelope,
  ApiErrorPayload,
  PaginatedEnvelope,
  QueryValue,
  WrappedData,
} from "@/lib/api/types";

type ApiFetchOptions = Omit<RequestInit, "body"> & {
  accessToken?: string;
  body?: unknown;
  query?: Record<string, QueryValue>;
};

export class ApiError extends Error {
  status: number;
  payload: ApiErrorPayload;
  retryAfter: string | null;

  constructor(status: number, payload: ApiErrorPayload, retryAfter: string | null) {
    super(payload.message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
    this.retryAfter = retryAfter;
  }
}

function resolveApiBaseUrl() {
  const rawValue = process.env.FASTAPI_BASE_URL;

  if (!rawValue) {
    if (process.env.NODE_ENV === "production") {
      throw new Error("FASTAPI_BASE_URL is not configured for the deployed frontend.");
    }

    return "http://127.0.0.1:8000";
  }

  const trimmedValue = rawValue.trim();
  const normalizedValue =
    (trimmedValue.startsWith('"') && trimmedValue.endsWith('"')) ||
    (trimmedValue.startsWith("'") && trimmedValue.endsWith("'"))
      ? trimmedValue.slice(1, -1).trim()
      : trimmedValue;

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(normalizedValue);
  } catch {
    throw new Error(`FASTAPI_BASE_URL is not a valid absolute URL: ${JSON.stringify(rawValue)}`);
  }

  return parsedUrl.toString().replace(/\/$/, "");
}

const apiBaseUrl = resolveApiBaseUrl();

async function apiFetch(path: string, options: ApiFetchOptions = {}) {
  const { accessToken, body, headers, query, ...init } = options;
  const url = `${apiBaseUrl}${path}${buildQueryString(query)}`;
  const requestHeaders = new Headers(headers);

  requestHeaders.set("Accept", "application/json");

  if (accessToken) {
    requestHeaders.set("Authorization", `Bearer ${accessToken}`);
  }

  let requestBody: BodyInit | undefined;
  if (body !== undefined && body !== null) {
    requestHeaders.set("Content-Type", "application/json");
    requestBody = JSON.stringify(body);
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      body: requestBody,
      headers: requestHeaders,
      cache: init.cache ?? "no-store",
    });
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new Error(`Request to ${url} failed before a response was received: ${reason}`);
  }

  const payload = await readJson(response);

  if (!response.ok) {
    const normalized = normalizeApiError(payload, response);
    throw new ApiError(response.status, normalized, response.headers.get("Retry-After"));
  }

  return payload;
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export async function getPaginated<T>(
  path: string,
  options?: ApiFetchOptions,
): Promise<PaginatedEnvelope<T>> {
  const payload = await apiFetch(path, { method: "GET", ...options });
  return parsePaginatedEnvelope<T>(payload);
}

export async function getAnalytics<T>(
  path: string,
  options?: ApiFetchOptions,
): Promise<AnalyticsEnvelope<T>> {
  const payload = await apiFetch(path, { method: "GET", ...options });
  return parseAnalyticsEnvelope<T>(payload);
}

export async function getWrapped<T>(
  path: string,
  options?: ApiFetchOptions,
): Promise<WrappedData<T>> {
  const payload = await apiFetch(path, { method: "GET", ...options });
  return parseWrappedData<T>(payload);
}

export async function getModel<T>(path: string, options?: ApiFetchOptions): Promise<T> {
  const payload = await apiFetch(path, { method: "GET", ...options });
  return parseDirectModel<T>(payload);
}

export async function postModel<T>(path: string, options?: ApiFetchOptions): Promise<T> {
  const payload = await apiFetch(path, { method: "POST", ...options });
  return parseDirectModel<T>(payload);
}

export async function postWrapped<T>(path: string, options?: ApiFetchOptions): Promise<WrappedData<T>> {
  const payload = await apiFetch(path, { method: "POST", ...options });
  return parseWrappedData<T>(payload);
}

export async function putModel<T>(path: string, options?: ApiFetchOptions): Promise<T> {
  const payload = await apiFetch(path, { method: "PUT", ...options });
  return parseDirectModel<T>(payload);
}

export async function deleteVoid(path: string, options?: ApiFetchOptions): Promise<void> {
  await apiFetch(path, { method: "DELETE", ...options });
}
