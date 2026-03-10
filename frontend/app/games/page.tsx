import { Grid2x2, ListFilter } from "lucide-react";

import { CatalogFilterPanel } from "@/components/games/catalog-filter-panel";
import { GameCatalogCard } from "@/components/games/game-catalog-card";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { PaginationNav } from "@/components/ui/pagination-nav";
import { listGames } from "@/lib/api/games";
import { listDevelopers, listGenres, listPublishers, listTags } from "@/lib/api/taxonomy";
import { buildQueryString } from "@/lib/api/normalizers";
import { requireSession } from "@/lib/auth/guards";

type SearchParams = Record<string, string | string[] | undefined>;

function readString(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

function readNumber(value: string | undefined) {
  if (!value) {
    return undefined;
  }

  const parsed = Number(value);
  return Number.isNaN(parsed) ? undefined : parsed;
}

function readBoolean(value: string | undefined) {
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  return undefined;
}

function buildGamesHref(params: Record<string, string | undefined>) {
  return `/games${buildQueryString(params)}`;
}

export default async function GamesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const { token } = await requireSession();
  const rawParams = await searchParams;

  const values = {
    page: readNumber(readString(rawParams.page)) ?? 1,
    per_page: 12,
    genre: readString(rawParams.genre),
    tag: readString(rawParams.tag),
    developer: readString(rawParams.developer),
    publisher: readString(rawParams.publisher),
    platform: readString(rawParams.platform) as "windows" | "mac" | "linux" | undefined,
    is_free: readBoolean(readString(rawParams.is_free)),
    min_price: readNumber(readString(rawParams.min_price)),
    max_price: readNumber(readString(rawParams.max_price)),
    min_score: readNumber(readString(rawParams.min_score)),
    release_from: readString(rawParams.release_from),
    release_to: readString(rawParams.release_to),
    sort:
      (readString(rawParams.sort) as
        | "name"
        | "price_usd"
        | "metacritic_score"
        | "release_date"
        | "positive_reviews"
        | undefined) ?? "name",
    order: (readString(rawParams.order) as "asc" | "desc" | undefined) ?? "asc",
  };

  const [gamesResult, genresResult, tagsResult, developersResult, publishersResult] =
    await Promise.allSettled([
      listGames(token, values),
      listGenres(token, 1, 40),
      listTags(token, 1, 40),
      listDevelopers(token, 1, 40),
      listPublishers(token, 1, 40),
    ]);

  if (gamesResult.status !== "fulfilled") {
    return (
      <ErrorState description="The catalog could not load from the backend. Confirm the API is running and reachable from `FASTAPI_BASE_URL`." />
    );
  }

  const pagination = gamesResult.value.pagination;
  const baseParams = {
    genre: values.genre,
    tag: values.tag,
    developer: values.developer,
    publisher: values.publisher,
    platform: values.platform,
    is_free:
      values.is_free === undefined ? undefined : values.is_free ? "true" : "false",
    min_price: values.min_price?.toString(),
    max_price: values.max_price?.toString(),
    min_score: values.min_score?.toString(),
    release_from: values.release_from,
    release_to: values.release_to,
    sort: values.sort,
    order: values.order,
  };

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <Badge variant="outline">Catalog browser</Badge>
            <h1 className="font-display text-4xl font-semibold tracking-tight">
              Browse games with live backend filtering.
            </h1>
            <p className="max-w-3xl text-base leading-7 text-primary-foreground/76">
              This page mirrors the real `/api/v1/games` surface, including server-side sorting,
              taxonomy filters, pricing, platforms, and release ranges.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm text-primary-foreground/78">
            <div className="rounded-[1.3rem] bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.18em]">Total matches</p>
              <p className="mt-2 font-display text-3xl font-semibold">{pagination.total}</p>
            </div>
            <div className="rounded-[1.3rem] bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.18em]">Current page</p>
              <p className="mt-2 font-display text-3xl font-semibold">{pagination.page}</p>
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="lg:sticky lg:top-28 lg:self-start">
          <CatalogFilterPanel
            values={{
              genre: values.genre,
              tag: values.tag,
              developer: values.developer,
              publisher: values.publisher,
              platform: values.platform,
              is_free:
                values.is_free === undefined ? undefined : values.is_free ? "true" : "false",
              min_price: values.min_price?.toString(),
              max_price: values.max_price?.toString(),
              min_score: values.min_score?.toString(),
              release_from: values.release_from,
              release_to: values.release_to,
              sort: values.sort,
              order: values.order,
            }}
            genres={genresResult.status === "fulfilled" ? genresResult.value.data : []}
            tags={tagsResult.status === "fulfilled" ? tagsResult.value.data : []}
            developers={developersResult.status === "fulfilled" ? developersResult.value.data : []}
            publishers={publishersResult.status === "fulfilled" ? publishersResult.value.data : []}
          />
        </aside>

        <section className="space-y-6">
          <Card>
            <CardHeader className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <div className="mb-3 flex items-center gap-2 text-muted">
                  <Grid2x2 className="size-4" />
                  <span className="text-sm">Paginated catalog response</span>
                </div>
                <CardTitle>Results</CardTitle>
                <CardDescription>
                  URL parameters are the source of truth, so every filter state is shareable.
                </CardDescription>
              </div>
              <div className="inline-flex items-center gap-2 rounded-full bg-background-alt px-4 py-2 text-sm text-muted">
                <ListFilter className="size-4" />
                {pagination.total} matching games
              </div>
            </CardHeader>
            <CardContent>
              {gamesResult.value.data.length > 0 ? (
                <div className="grid gap-4 xl:grid-cols-2">
                  {gamesResult.value.data.map((game) => (
                    <GameCatalogCard key={game.id} game={game} />
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No games matched these filters"
                  description="Adjust the pricing, taxonomy, or release filters and try again."
                />
              )}
            </CardContent>
          </Card>

          <PaginationNav
            page={pagination.page}
            totalPages={pagination.total_pages}
            previousHref={
              pagination.page > 1
                ? buildGamesHref({ ...baseParams, page: String(pagination.page - 1) })
                : null
            }
            nextHref={
              pagination.page < pagination.total_pages
                ? buildGamesHref({ ...baseParams, page: String(pagination.page + 1) })
                : null
            }
          />
        </section>
      </div>
    </div>
  );
}
