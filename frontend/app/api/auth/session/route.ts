import { NextResponse } from "next/server";

import { clearSessionCookie, getSessionToken, getSessionUser } from "@/lib/auth/session";

export async function GET() {
  const token = await getSessionToken();
  const user = await getSessionUser();

  const response = NextResponse.json({
    authenticated: Boolean(user),
    user,
  });

  if (token && !user) {
    clearSessionCookie(response);
  }

  return response;
}
