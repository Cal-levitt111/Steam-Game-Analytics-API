import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { getCollection } from "@/lib/api/collections";
import { isApiError } from "@/lib/api/client";
import { getSessionToken, getSessionUser } from "@/lib/auth/session";

export default async function CollectionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const collectionId = Number(id);

  if (Number.isNaN(collectionId)) {
    notFound();
  }

  const [token, viewer] = await Promise.all([getSessionToken(), getSessionUser()]);

  try {
    const collection = await getCollection(collectionId, token ?? undefined);
    const isOwner = viewer?.id === collection.user_id;

    return (
      <div className="space-y-6">
        <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">{collection.is_public ? "Public" : "Private"}</Badge>
                {isOwner ? <Badge variant="outline">Owner view</Badge> : null}
              </div>
              <h1 className="font-display text-4xl font-semibold tracking-tight">{collection.name}</h1>
              <p className="max-w-2xl text-base leading-7 text-primary-foreground/76">
                {collection.description ?? "No description provided for this collection."}
              </p>
            </div>
            <Button asChild variant="secondary">
              <Link href={isOwner ? "/collections" : "/collections/public"}>
                {isOwner ? "Back to my collections" : "Back to public collections"}
              </Link>
            </Button>
          </div>
        </section>

        {collection.games.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {collection.games.map((game) => (
              <Link key={game.id} href={`/games/${game.id}`}>
                <Card className="h-full transition hover:-translate-y-1 hover:border-accent/50">
                  <CardHeader>
                    <CardTitle>{game.name}</CardTitle>
                    <CardDescription>Steam App #{game.steam_app_id}</CardDescription>
                  </CardHeader>
                  <CardContent className="text-sm text-muted">
                    Open the detail page to inspect similarity and add-to-collection actions.
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState
            title="This collection is empty"
            description={
              isOwner
                ? "Add games from a game detail page in the next commit."
                : "The owner has not added any games yet."
            }
          />
        )}
      </div>
    );
  } catch (error) {
    if (isApiError(error)) {
      if (error.status === 404) {
        notFound();
      }

      if (error.status === 403) {
        return (
          <ErrorState description="This collection is private. Sign in as the owner to view it." />
        );
      }
    }

    return (
      <ErrorState description="The collection detail view could not be loaded from the backend." />
    );
  }
}
