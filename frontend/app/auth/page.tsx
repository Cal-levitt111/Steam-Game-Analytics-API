import { redirect } from "next/navigation";

import { AuthPanel } from "@/components/auth/auth-panel";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getSessionUser } from "@/lib/auth/session";

export default async function AuthPage() {
  const user = await getSessionUser();

  if (user) {
    redirect("/collections");
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <Badge variant="outline">Protected area enabled</Badge>
        <div className="mt-6 space-y-4">
          <h1 className="font-display text-4xl font-semibold tracking-tight text-balance">
            Sign in to test collections and authenticated flows.
          </h1>
          <p className="max-w-2xl text-base leading-7 text-primary-foreground/76">
            The demo frontend stores the API access token in a secure HTTP-only cookie. Browser code
            never calls the backend auth endpoints directly.
          </p>
        </div>
      </section>

      <AuthPanel />

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>What this unlocks</CardTitle>
          <CardDescription>
            Signing in unlocks the protected catalogue, analytics, and collection workflows used by
            the rest of the frontend.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="rounded-[1.4rem] bg-background-alt p-4">
            <p className="font-medium text-primary">Current account lookup</p>
            <p className="mt-2 text-sm leading-6 text-muted">Resolved server-side through `/auth/me`.</p>
          </div>
          <div className="rounded-[1.4rem] bg-background-alt p-4">
            <p className="font-medium text-primary">Protected application routes</p>
            <p className="mt-2 text-sm leading-6 text-muted">
              All frontend pages except `/auth` require a valid session.
            </p>
          </div>
          <div className="rounded-[1.4rem] bg-background-alt p-4">
            <p className="font-medium text-primary">Auto-login after register</p>
            <p className="mt-2 text-sm leading-6 text-muted">
              Registration immediately creates a session and sends users into the protected area.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
