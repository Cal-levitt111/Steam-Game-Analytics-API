import { NextResponse } from "next/server";

import { getCurrentUser, loginUser } from "@/lib/api/auth";
import { attachSessionCookie, toErrorResponse } from "@/lib/auth/session";

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    const token = await loginUser(payload);
    const user = await getCurrentUser(token.access_token);
    const response = NextResponse.json({ authenticated: true, user });
    return attachSessionCookie(response, token.access_token);
  } catch (error) {
    return toErrorResponse(error);
  }
}
