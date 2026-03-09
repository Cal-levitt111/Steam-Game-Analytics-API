import { getModel, postModel, putModel } from "@/lib/api/client";
import type {
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  UpdateMePayload,
  UserRead,
} from "@/lib/api/types";

export function registerUser(payload: RegisterPayload) {
  return postModel<UserRead>("/api/v1/auth/register", { body: payload });
}

export function loginUser(payload: LoginPayload) {
  return postModel<TokenResponse>("/api/v1/auth/login", { body: payload });
}

export function getCurrentUser(accessToken: string) {
  return getModel<UserRead>("/api/v1/auth/me", { accessToken });
}

export function updateCurrentUser(accessToken: string, payload: UpdateMePayload) {
  return putModel<UserRead>("/api/v1/auth/me", { accessToken, body: payload });
}
