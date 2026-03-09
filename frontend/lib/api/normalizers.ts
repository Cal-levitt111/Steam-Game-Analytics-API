import type {
  AnalyticsEnvelope,
  ApiErrorPayload,
  JsonValue,
  PaginatedEnvelope,
  QueryValue,
  WrappedData,
} from "@/lib/api/types";

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function buildQueryString(query?: Record<string, QueryValue>) {
  if (!query) {
    return "";
  }

  const params = new URLSearchParams();

  for (const [key, rawValue] of Object.entries(query)) {
    if (rawValue === undefined || rawValue === null || rawValue === "") {
      continue;
    }

    if (Array.isArray(rawValue)) {
      if (rawValue.length > 0) {
        params.set(key, rawValue.join(","));
      }
      continue;
    }

    params.set(key, String(rawValue));
  }

  const value = params.toString();
  return value ? `?${value}` : "";
}

export async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) {
    return null;
  }

  return JSON.parse(text) as JsonValue;
}

export function normalizeApiError(payload: unknown, response: Response): ApiErrorPayload {
  if (isObject(payload) && isObject(payload.error)) {
    const error = payload.error;

    return {
      code: String(error.code ?? `HTTP_${response.status}`),
      message: String(error.message ?? response.statusText),
      detail: (error.detail as JsonValue | null | undefined) ?? null,
    };
  }

  return {
    code: `HTTP_${response.status}`,
    message: response.statusText || "Request failed.",
    detail: isObject(payload) ? (payload as JsonValue) : null,
  };
}

export function parsePaginatedEnvelope<T>(payload: unknown): PaginatedEnvelope<T> {
  if (!isObject(payload) || !Array.isArray(payload.data) || !isObject(payload.pagination)) {
    throw new Error("Expected a paginated API envelope.");
  }

  return payload as PaginatedEnvelope<T>;
}

export function parseAnalyticsEnvelope<T>(payload: unknown): AnalyticsEnvelope<T> {
  if (!isObject(payload) || !Array.isArray(payload.data) || !("generated_at" in payload)) {
    throw new Error("Expected an analytics API envelope.");
  }

  return payload as AnalyticsEnvelope<T>;
}

export function parseWrappedData<T>(payload: unknown): WrappedData<T> {
  if (!isObject(payload) || !("data" in payload)) {
    throw new Error("Expected a wrapped data payload.");
  }

  return payload as WrappedData<T>;
}

export function parseDirectModel<T>(payload: unknown): T {
  if (!isObject(payload)) {
    throw new Error("Expected an object payload.");
  }

  return payload as T;
}
