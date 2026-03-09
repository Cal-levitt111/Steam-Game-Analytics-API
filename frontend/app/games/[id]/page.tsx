import Link from "next/link";
import { notFound } from "next/navigation";
import Image from "next/image";
import { ExternalLink, Layers3, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { getGame, getSimilarGames } from "@/lib/api/games";
import { ApiError, isApiError } from "@/lib/api/client";
import { formatCompactNumber, formatCurrency } from "@/lib/formatters";

function stripHtml(value: string | null) {
  if (!value) {
    return "No description is available for this game.";
  }

  return value.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
}

function parseMediaList(value: string | null) {
  if (!value) {
    return [];
  }

  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function TaxonomyLinks({
  label,
  items,
  param,
}: {
  label: string;
  items: Array<{ id: number; name: string; slug: string }>;
  param: "genre" | "tag" | "developer" | "publisher";
}) {
  return (
    <div className="space-y-3">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
      <div className="flex flex-wrap gap-2">
        {items.length > 0 ? (
          items.map((item) => (
            <Link key={item.id} href={`/games?${param}=${item.slug}`}>
              <Badge>{item.name}</Badge>
            </Link>
          ))
        ) : (
          <Badge>No data</Badge>
        )}
      </div>
    </div>
  );
}

export default async function GameDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const gameId = Number(id);

  if (Number.isNaN(gameId)) {
    notFound();
  }

  let game;
  try {
    game = await getGame(gameId);
  } catch (error) {
    if (isApiError(error) && error.status === 404) {
      notFound();
    }

    return (
      <ErrorState description="The game detail view could not load from the backend. Confirm the local API and database are running." />
    );
  }

  let similarGames:
    | { state: "ready"; data: Awaited<ReturnType<typeof getSimilarGames>> }
    | { state: "missing-embedding"; message: string }
    | { state: "feature-unavailable"; message: string }
    | { state: "error"; message: string };

  try {
    const data = await getSimilarGames(gameId, 8);
    similarGames = { state: "ready", data };
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.payload.code === "EMBEDDING_NOT_AVAILABLE") {
        similarGames = { state: "missing-embedding", message: error.payload.message };
      } else if (error.payload.code === "FEATURE_UNAVAILABLE") {
        similarGames = { state: "feature-unavailable", message: error.payload.message };
      } else {
        similarGames = { state: "error", message: error.payload.message };
      }
    } else {
      similarGames = {
        state: "error",
        message: "Similarity recommendations could not be loaded.",
      };
    }
  }

  const screenshots = parseMediaList(game.screenshots).slice(0, 4);

  return (
    <div className="space-y-6">
      <section className="glass-panel overflow-hidden rounded-[2rem] border border-border/70 bg-surface text-primary-foreground shadow-lg">
        {game.header_image ? (
          <Image
            alt={`${game.name} header art`}
            className="h-56 w-full object-cover"
            height={900}
            src={game.header_image}
            unoptimized={false}
            width={1600}
          />
        ) : null}
        <div className="space-y-6 px-6 py-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline">Game detail</Badge>
                <Badge variant="outline">Steam App #{game.steam_app_id}</Badge>
                <Badge variant="outline">{game.is_free ? "Free" : formatCurrency(game.price_usd)}</Badge>
              </div>
              <h1 className="font-display text-4xl font-semibold tracking-tight">{game.name}</h1>
              <p className="max-w-3xl text-base leading-7 text-primary-foreground/76">
                {stripHtml(game.about_the_game)}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 lg:min-w-80">
              <div className="rounded-[1.3rem] bg-white/8 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-primary-foreground/55">
                  Metacritic
                </p>
                <p className="mt-2 font-display text-3xl font-semibold">
                  {game.metacritic_score ?? "N/A"}
                </p>
              </div>
              <div className="rounded-[1.3rem] bg-white/8 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-primary-foreground/55">
                  Recommendations
                </p>
                <p className="mt-2 font-display text-3xl font-semibold">
                  {formatCompactNumber(game.recommendations)}
                </p>
              </div>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-[1.4rem] bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-primary-foreground/55">Release date</p>
              <p className="mt-2 font-medium">{game.release_date ?? "Unknown"}</p>
            </div>
            <div className="rounded-[1.4rem] bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-primary-foreground/55">Owners</p>
              <p className="mt-2 font-medium">{game.estimated_owners ?? "Unknown"}</p>
            </div>
            <div className="rounded-[1.4rem] bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-primary-foreground/55">Peak CCU</p>
              <p className="mt-2 font-medium">{formatCompactNumber(game.peak_ccu)}</p>
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Taxonomy and metadata</CardTitle>
              <CardDescription>
                Taxonomy badges deep-link back into catalog filters for rapid exploration.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <TaxonomyLinks items={game.genres} label="Genres" param="genre" />
              <TaxonomyLinks items={game.tags} label="Tags" param="tag" />
              <TaxonomyLinks items={game.developers} label="Developers" param="developer" />
              <TaxonomyLinks items={game.publishers} label="Publishers" param="publisher" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Supporting details</CardTitle>
              <CardDescription>Selected fields from the richer game detail response.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="rounded-[1.2rem] bg-background-alt p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted">Languages</p>
                <p className="mt-2 text-sm leading-6 text-primary">
                  {game.supported_languages ?? "Not provided"}
                </p>
              </div>
              <div className="rounded-[1.2rem] bg-background-alt p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted">User score</p>
                <p className="mt-2 text-sm leading-6 text-primary">{game.user_score ?? "N/A"}</p>
              </div>
              <div className="rounded-[1.2rem] bg-background-alt p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted">Positive reviews</p>
                <p className="mt-2 text-sm leading-6 text-primary">
                  {formatCompactNumber(game.positive_reviews)}
                </p>
              </div>
              <div className="rounded-[1.2rem] bg-background-alt p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-muted">Negative reviews</p>
                <p className="mt-2 text-sm leading-6 text-primary">
                  {formatCompactNumber(game.negative_reviews)}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="mb-3 inline-flex w-fit rounded-2xl bg-primary p-3 text-primary-foreground">
                <Sparkles className="size-5" />
              </div>
              <CardTitle>Similar games</CardTitle>
              <CardDescription>
                Powered by the backend&apos;s pgvector cosine similarity endpoint.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {similarGames.state === "ready" ? (
                similarGames.data.length > 0 ? (
                  similarGames.data.map((similar) => (
                    <Link
                      key={similar.id}
                      href={`/games/${similar.id}`}
                      className="block rounded-[1.3rem] border border-border/80 bg-white/80 p-4 transition hover:-translate-y-0.5 hover:border-accent/50"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-medium text-primary">{similar.name}</p>
                          <p className="mt-1 text-sm text-muted">
                            Similarity {similar.similarity !== null ? similar.similarity.toFixed(3) : "N/A"}
                          </p>
                        </div>
                        <Badge variant="accent">
                          {similar.is_free ? "Free" : formatCurrency(similar.price_usd)}
                        </Badge>
                      </div>
                    </Link>
                  ))
                ) : (
                  <EmptyState
                    title="No similar games returned"
                    description="The endpoint succeeded, but it did not return any neighbors for this game."
                  />
                )
              ) : (
                <div className="rounded-[1.4rem] border border-border/80 bg-background-alt p-4 text-sm leading-6 text-muted">
                  {similarGames.state === "missing-embedding" ? (
                    <>
                      <p className="font-medium text-primary">Embedding not available</p>
                      <p className="mt-2">{similarGames.message}</p>
                    </>
                  ) : similarGames.state === "feature-unavailable" ? (
                    <>
                      <p className="font-medium text-primary">Similarity disabled</p>
                      <p className="mt-2">{similarGames.message}</p>
                    </>
                  ) : (
                    <>
                      <p className="font-medium text-primary">Similarity failed</p>
                      <p className="mt-2">{similarGames.message}</p>
                    </>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="mb-3 inline-flex w-fit rounded-2xl bg-accent-alt p-3 text-accent-foreground">
                <Layers3 className="size-5" />
              </div>
              <CardTitle>Media and links</CardTitle>
              <CardDescription>Useful outbound links and preview screenshots.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {game.website ? (
                  <Button asChild variant="secondary">
                    <Link href={game.website} rel="noreferrer" target="_blank">
                      Official site
                      <ExternalLink className="size-4" />
                    </Link>
                  </Button>
                ) : null}
                {game.metacritic_url ? (
                  <Button asChild variant="outline">
                    <Link href={game.metacritic_url} rel="noreferrer" target="_blank">
                      Metacritic
                      <ExternalLink className="size-4" />
                    </Link>
                  </Button>
                ) : null}
              </div>

              {screenshots.length > 0 ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  {screenshots.map((url) => (
                    <Image
                      key={url}
                      alt={`${game.name} screenshot`}
                      className="h-36 w-full rounded-[1.2rem] object-cover"
                      height={450}
                      src={url}
                      width={800}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted">No screenshots were provided in the current dataset.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
