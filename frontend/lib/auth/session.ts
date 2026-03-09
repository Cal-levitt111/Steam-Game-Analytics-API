import "server-only";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getCurrentUser } from "@/lib/api/auth";
import { ApiError, isApiError } from "@/lib/api/client";
import type { UserRead } from "@/lib/api/types";

export const SESSION_COOKIE_NAME = "sga_session";

function getSessionCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  };
}

export function attachSessionCookie(response: NextResponse, accessToken: string) {
  response.cookies.set(SESSION_COOKIE_NAME, accessToken, getSessionCookieOptions());
  return response;
}

export function clearSessionCookie(response: NextResponse) {
  response.cookies.set(SESSION_COOKIE_NAME, "", {
    ...getSessionCookieOptions(),
    maxAge: 0,
  });
  return response;
}

export async function getSessionToken() {
  const cookieStore = await cookies();
  return cookieStore.get(SESSION_COOKIE_NAME)?.value ?? null;
}

export function isAuthFailure(error: unknown) {
  return (
    isApiError(error) &&
    (error.status === 401 ||
      error.payload.code === "TOKEN_INVALID" ||
      error.payload.code === "TOKEN_EXPIRED" ||
      error.payload.code === "UNAUTHORIZED")
  );
}

export async function getSessionUser(): Promise<UserRead | null> {
  const token = await getSessionToken();
  if (!token) {
    return null;
  }

  try {
    return await getCurrentUser(token);
  } catch (error) {
    if (isAuthFailure(error)) {
      return null;
    }

    throw error;
  }
}

export function toErrorResponse(error: unknown) {
  if (isApiError(error)) {
    const response = NextResponse.json({ error: error.payload }, { status: error.status });

    if (error.retryAfter) {
      response.headers.set("Retry-After", error.retryAfter);
    }

    if (isAuthFailure(error)) {
      clearSessionCookie(response);
    }

    return response;
  }

  return NextResponse.json(
    {
      error: {
        code: "INTERNAL_SERVER_ERROR",
        message: "An unexpected frontend server error occurred.",
        detail: null,
      },
    },
    { status: 500 },
  );
}

export function assertApiError(error: unknown): asserts error is ApiError {
  if (!isApiError(error)) {
    throw error;
  }
}
