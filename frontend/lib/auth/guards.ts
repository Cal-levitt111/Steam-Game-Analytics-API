import "server-only";

import { redirect } from "next/navigation";

import { getSessionToken, getSessionUser } from "@/lib/auth/session";

export async function requireSession() {
  const token = await getSessionToken();
  const user = await getSessionUser();

  if (!token || !user) {
    redirect("/auth");
  }

  return { token, user };
}
