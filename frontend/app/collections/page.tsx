import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { requireSession } from "@/lib/auth/guards";

export default async function CollectionsPage() {
  const { user } = await requireSession();

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <Badge variant="outline">Authenticated area</Badge>
        <div className="mt-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-3">
            <h1 className="font-display text-4xl font-semibold tracking-tight">
              Welcome back{user.display_name ? `, ${user.display_name}` : ""}.
            </h1>
            <p className="max-w-2xl text-base leading-7 text-primary-foreground/76">
              Your session is active. This protected route is now wired to the backend-backed auth
              cookie and will expand into the full collections dashboard in a later commit.
            </p>
          </div>
          <Button asChild variant="secondary">
            <Link href="/auth">Manage session</Link>
          </Button>
        </div>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Session state confirmed</CardTitle>
          <CardDescription>Authenticated user details resolved from `/api/v1/auth/me`.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="rounded-[1.4rem] bg-background-alt p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted">Email</p>
            <p className="mt-2 font-medium text-primary">{user.email}</p>
          </div>
          <div className="rounded-[1.4rem] bg-background-alt p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted">Display name</p>
            <p className="mt-2 font-medium text-primary">{user.display_name ?? "Not set"}</p>
          </div>
          <div className="rounded-[1.4rem] bg-background-alt p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted">Next step</p>
            <p className="mt-2 font-medium text-primary">Collections CRUD in commit 10</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
