import Link from "next/link";

import { CreateCollectionForm } from "@/components/collections/create-collection-form";
import { CollectionCard } from "@/components/collections/collection-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { listMyCollections } from "@/lib/api/collections";
import { requireSession } from "@/lib/auth/guards";

export default async function CollectionsPage() {
  const { token, user } = await requireSession();

  let collections;
  try {
    collections = await listMyCollections(token);
  } catch {
    return (
      <ErrorState description="Your collections could not be loaded from the backend. Check the API and try again." />
    );
  }

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-3">
            <Badge variant="outline">Authenticated dashboard</Badge>
            <h1 className="font-display text-4xl font-semibold tracking-tight">
              Collections for {user.display_name ?? user.email}
            </h1>
            <p className="max-w-2xl text-base leading-7 text-primary-foreground/76">
              This dashboard pulls from the protected `/api/v1/collections` route and exposes
              creation plus owner-only detail views.
            </p>
          </div>
          <Button asChild variant="secondary">
            <Link href="/collections/public">Browse public collections</Link>
          </Button>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <CreateCollectionForm />

        <section className="space-y-4">
          {collections.data.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {collections.data.map((collection) => (
                <CollectionCard
                  key={collection.id}
                  collection={collection}
                  href={`/collections/${collection.id}`}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              title="No collections yet"
              description="Create your first private or public collection to start grouping games."
            />
          )}
        </section>
      </div>
    </div>
  );
}
