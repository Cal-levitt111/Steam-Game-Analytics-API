import { NextResponse } from "next/server";

import { getCurrentUser, loginUser, registerUser } from "@/lib/api/auth";
import { attachSessionCookie, toErrorResponse } from "@/lib/auth/session";

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    await registerUser(payload);
    const token = await loginUser({
      email: payload.email,
      password: payload.password,
    });
    const user = await getCurrentUser(token.access_token);
    const response = NextResponse.json({ authenticated: true, user }, { status: 201 });
    return attachSessionCookie(response, token.access_token);
  } catch (error) {
    return toErrorResponse(error);
  }
}
