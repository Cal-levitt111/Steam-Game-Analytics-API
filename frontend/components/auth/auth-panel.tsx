"use client";

import { startTransition, useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const loginSchema = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(1, "Password is required."),
});

const registerSchema = loginSchema.extend({
  display_name: z
    .string()
    .max(120, "Display name must be 120 characters or fewer.")
    .optional()
    .or(z.literal("")),
  password: z.string().min(8, "Password must be at least 8 characters."),
});

type AuthMode = "login" | "register";

type ErrorShape = {
  message: string;
  retryAfter?: string | null;
};

async function readResponse(response: Response) {
  const text = await response.text();
  return text ? (JSON.parse(text) as Record<string, unknown>) : {};
}

export function AuthPanel() {
  const router = useRouter();
  const [mode, setMode] = useState<AuthMode>("login");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ErrorShape | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  async function handleSubmit(formData: FormData) {
    setError(null);
    setFieldErrors({});

    const values = {
      email: String(formData.get("email") ?? "").trim(),
      password: String(formData.get("password") ?? ""),
      display_name: String(formData.get("display_name") ?? "").trim(),
    };

    const schema = mode === "login" ? loginSchema : registerSchema;
    const parsed = schema.safeParse(values);

    if (!parsed.success) {
      const nextFieldErrors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        const key = issue.path[0];
        if (typeof key === "string" && !(key in nextFieldErrors)) {
          nextFieldErrors[key] = issue.message;
        }
      }
      setFieldErrors(nextFieldErrors);
      return;
    }

    setPending(true);

    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsed.data),
      });

      const payload = await readResponse(response);

      if (!response.ok) {
        const backendError = payload.error as
          | { message?: string; code?: string; detail?: unknown }
          | undefined;
        setError({
          message:
            backendError?.message ??
            (mode === "login" ? "Unable to sign in." : "Unable to create your account."),
          retryAfter: response.headers.get("Retry-After"),
        });
        return;
      }

      startTransition(() => {
        router.replace("/collections");
        router.refresh();
      });
    } catch {
      setError({
        message: "The frontend could not reach the local Next.js auth route.",
      });
    } finally {
      setPending(false);
    }
  }

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <Badge>{mode === "login" ? "Sign in" : "Register"}</Badge>
        <CardTitle>{mode === "login" ? "Access protected demo flows" : "Create a demo account"}</CardTitle>
        <CardDescription>
          Auth is handled through Next.js route handlers, which store the FastAPI bearer token in
          an HTTP-only cookie.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-2 rounded-full bg-background-alt p-1">
          <Button
            type="button"
            variant={mode === "login" ? "default" : "ghost"}
            onClick={() => setMode("login")}
          >
            Login
          </Button>
          <Button
            type="button"
            variant={mode === "register" ? "default" : "ghost"}
            onClick={() => setMode("register")}
          >
            Register
          </Button>
        </div>

        <form
          className="space-y-4"
          action={(formData) => {
            void handleSubmit(formData);
          }}
        >
          {mode === "register" ? (
            <div className="space-y-2">
              <label className="text-sm font-medium text-primary" htmlFor="display_name">
                Display name
              </label>
              <Input id="display_name" name="display_name" placeholder="Steam data explorer" />
              {fieldErrors.display_name ? (
                <p className="text-sm text-danger">{fieldErrors.display_name}</p>
              ) : null}
            </div>
          ) : null}

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="email">
              Email
            </label>
            <Input id="email" name="email" type="email" placeholder="you@example.com" required />
            {fieldErrors.email ? <p className="text-sm text-danger">{fieldErrors.email}</p> : null}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="password">
              Password
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder={mode === "login" ? "Your password" : "At least 8 characters"}
              required
            />
            {fieldErrors.password ? (
              <p className="text-sm text-danger">{fieldErrors.password}</p>
            ) : null}
          </div>

          {error ? (
            <div className="rounded-2xl border border-danger/20 bg-danger/8 px-4 py-3 text-sm text-danger">
              <p>{error.message}</p>
              {error.retryAfter ? <p className="mt-1">Retry after {error.retryAfter} seconds.</p> : null}
            </div>
          ) : null}

          <Button className="w-full" size="lg" disabled={pending}>
            {pending
              ? mode === "login"
                ? "Signing in..."
                : "Creating account..."
              : mode === "login"
                ? "Sign in"
                : "Create account"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
