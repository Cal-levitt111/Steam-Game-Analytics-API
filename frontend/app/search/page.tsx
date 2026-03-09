import Link from "next/link";
import { Search as SearchIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Input } from "@/components/ui/input";
import { PaginationNav } from "@/components/ui/pagination-nav";
import { Select } from "@/components/ui/select";
import { buildQueryString } from "@/lib/api/normalizers";
import { searchGames } from "@/lib/api/games";
import { listGenres, listTags } from "@/lib/api/taxonomy";
import { formatCompactNumber, formatCurrency } from "@/lib/formatters";

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

function buildSearchHref(params: Record<string, string | undefined>) {
  return `/search${buildQueryString(params)}`;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const rawParams = await searchParams;
  const q = readString(rawParams.q)?.trim() ?? "";
  const page = readNumber(readString(rawParams.page)) ?? 1;
  const genre = readString(rawParams.genre);
  const tag = readString(rawParams.tag);
  const isFree = readBoolean(readString(rawParams.is_free));
  const minScore = readNumber(readString(rawParams.min_score));

  const [genresResult, tagsResult] = await Promise.allSettled([listGenres(1, 40), listTags(1, 40)]);

  const searchResult =
    q.length > 0
      ? await searchGames({
          q,
          page,
          per_page: 12,
          genre,
          tag,
          is_free: isFree,
          min_score: minScore,
        }).catch(() => null)
      : null;

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <Badge variant="outline">Full-text search</Badge>
        <div className="mt-4 space-y-3">
          <h1 className="font-display text-4xl font-semibold tracking-tight">
            Search game metadata with backend ranking.
          </h1>
          <p className="max-w-3xl text-base leading-7 text-primary-foreground/76">
            This page maps to `/api/v1/search`, so it only exposes the filters that endpoint
            supports: query, genre, tag, free/paid, and minimum score.
          </p>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <form className="space-y-4 rounded-[1.6rem] border border-border/80 bg-card p-5" method="GET">
          <div className="space-y-1">
            <p className="font-display text-2xl font-semibold text-primary">Search controls</p>
            <p className="text-sm leading-6 text-muted">
              Search is required. Other filters refine the backend’s ranked results.
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="q">
              Query
            </label>
            <Input defaultValue={q} id="q" name="q" placeholder="zombie co-op roguelike" required />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="genre">
              Genre
            </label>
            <Select defaultValue={genre ?? ""} id="genre" name="genre">
              <option value="">Any genre</option>
              {genresResult.status === "fulfilled"
                ? genresResult.value.data.map((item) => (
                    <option key={item.slug} value={item.slug}>
                      {item.name}
                    </option>
                  ))
                : null}
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="tag">
              Tag
            </label>
            <Select defaultValue={tag ?? ""} id="tag" name="tag">
              <option value="">Any tag</option>
              {tagsResult.status === "fulfilled"
                ? tagsResult.value.data.map((item) => (
                    <option key={item.slug} value={item.slug}>
                      {item.name}
                    </option>
                  ))
                : null}
            </Select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            <div className="space-y-2">
              <label className="text-sm font-medium text-primary" htmlFor="is_free">
                Free / paid
              </label>
              <Select defaultValue={isFree === undefined ? "" : isFree ? "true" : "false"} id="is_free" name="is_free">
                <option value="">Any pricing</option>
                <option value="true">Free only</option>
                <option value="false">Paid only</option>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-primary" htmlFor="min_score">
                Min score
              </label>
              <Input defaultValue={minScore?.toString() ?? ""} id="min_score" max="100" min="0" name="min_score" type="number" />
            </div>
          </div>

          <div className="flex gap-2">
            <Button className="flex-1">
              <SearchIcon className="size-4" />
              Search
            </Button>
            <Button asChild className="flex-1" variant="outline">
              <Link href="/search">Reset</Link>
            </Button>
          </div>
        </form>

        <section className="space-y-6">
          {!q ? (
            <EmptyState
              title="Start with a search term"
              description="The backend requires the `q` parameter. Try a genre, mechanic, studio, or mood."
            />
          ) : searchResult === null ? (
            <ErrorState description="The search endpoint could not be reached. Confirm the FastAPI app is running and seeded." />
          ) : searchResult.data.length === 0 ? (
            <EmptyState
              title="No results matched your query"
              description="Try loosening the tag or score filters, or search with a broader term."
            />
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Search results</CardTitle>
                  <CardDescription>
                    {searchResult.pagination.total} results for &quot;{q}&quot;.
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4 xl:grid-cols-2">
                  {searchResult.data.map((game) => (
                    <Link
                      key={game.id}
                      href={`/games/${game.id}`}
                      className="rounded-[1.5rem] border border-border/80 bg-white/80 p-5 transition hover:-translate-y-1 hover:border-accent/50"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h2 className="font-display text-2xl font-semibold text-primary">
                            {game.name}
                          </h2>
                          <p className="mt-2 text-sm text-muted">
                            {game.release_date ?? "Unknown release"} • {game.is_free ? "Free" : formatCurrency(game.price_usd)}
                          </p>
                        </div>
                        <Badge variant="accent">
                          Rank {game.rank !== null ? game.rank.toFixed(3) : "N/A"}
                        </Badge>
                      </div>

                      <div className="mt-5 grid grid-cols-2 gap-4 text-sm">
                        <div className="rounded-[1.2rem] bg-background-alt p-4">
                          <p className="text-xs uppercase tracking-[0.16em] text-muted">Metacritic</p>
                          <p className="mt-2 font-medium text-primary">{game.metacritic_score ?? "Unrated"}</p>
                        </div>
                        <div className="rounded-[1.2rem] bg-background-alt p-4">
                          <p className="text-xs uppercase tracking-[0.16em] text-muted">Positive reviews</p>
                          <p className="mt-2 font-medium text-primary">
                            {formatCompactNumber(game.positive_reviews)}
                          </p>
                        </div>
                      </div>
                    </Link>
                  ))}
                </CardContent>
              </Card>

              <PaginationNav
                page={searchResult.pagination.page}
                totalPages={searchResult.pagination.total_pages}
                previousHref={
                  searchResult.pagination.page > 1
                    ? buildSearchHref({
                        q,
                        genre,
                        tag,
                        is_free: isFree === undefined ? undefined : isFree ? "true" : "false",
                        min_score: minScore?.toString(),
                        page: String(searchResult.pagination.page - 1),
                      })
                    : null
                }
                nextHref={
                  searchResult.pagination.page < searchResult.pagination.total_pages
                    ? buildSearchHref({
                        q,
                        genre,
                        tag,
                        is_free: isFree === undefined ? undefined : isFree ? "true" : "false",
                        min_score: minScore?.toString(),
                        page: String(searchResult.pagination.page + 1),
                      })
                    : null
                }
              />
            </>
          )}
        </section>
      </div>
    </div>
  );
}
