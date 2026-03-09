import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  ChevronRight,
  Gamepad2,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { getReleaseTrends, getTopGenres } from "@/lib/api/analytics";
import { listGames } from "@/lib/api/games";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { formatCompactNumber, formatCurrency } from "@/lib/formatters";

const featureCards = [
  {
    title: "Catalog exploration",
    description: "Responsive discovery views for games, taxonomies, filters, and search.",
    icon: Search,
  },
  {
    title: "Authenticated flows",
    description: "A cookie-backed BFF layer for login, profile retrieval, and protected actions.",
    icon: ShieldCheck,
  },
  {
    title: "Analytics storytelling",
    description: "Dedicated surfaces for trends, breakdowns, and similarity-driven exploration.",
    icon: BarChart3,
  },
];

export default async function Home() {
  const [gamesResult, genresResult, trendsResult] = await Promise.allSettled([
    listGames({ per_page: 6, sort: "positive_reviews", order: "desc" }),
    getTopGenres(6),
    getReleaseTrends(),
  ]);

  const games = gamesResult.status === "fulfilled" ? gamesResult.value.data : [];
  const topGenres = genresResult.status === "fulfilled" ? genresResult.value.data : [];
  const releaseTrends = trendsResult.status === "fulfilled" ? trendsResult.value.data.slice(-6) : [];
  const hasShowcaseData = games.length > 0 || topGenres.length > 0 || releaseTrends.length > 0;

  return (
    <div className="space-y-10">
      <section className="glass-panel animate-rise overflow-hidden rounded-[2rem] border border-border/70 bg-surface px-6 py-10 text-primary-foreground shadow-lg sm:px-8 lg:px-12">
        <div className="grid gap-8 lg:grid-cols-[1.35fr_0.9fr] lg:items-end">
          <div className="space-y-6">
            <Badge variant="accent">Next.js demo frontend</Badge>
            <div className="space-y-4">
              <h1 className="max-w-3xl font-display text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl">
                Live demo frontend for search, analytics, similarity, and collections.
              </h1>
              <p className="max-w-2xl text-base leading-7 text-primary-foreground/78 sm:text-lg">
                This landing page is already backed by the FastAPI API. Featured games, top genres,
                and release-trend previews are pulled directly from the local backend so the
                frontend stays honest to real project data.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/games">
                  Explore games
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button asChild variant="secondary" size="lg">
                <Link href="/analytics">View analytics</Link>
              </Button>
            </div>
          </div>

          <div className="animate-rise-delay rounded-[1.5rem] border border-white/10 bg-white/8 p-6">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-full bg-accent/20 p-2 text-accent-alt">
                <Sparkles className="size-5" />
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.28em] text-primary-foreground/55">
                  Live preview
                </p>
                <p className="text-lg font-medium text-primary-foreground">
                  {hasShowcaseData ? "Backend data connected" : "Waiting on backend data"}
                </p>
              </div>
            </div>
            <ul className="space-y-3 text-sm text-primary-foreground/78">
              <li>{games.length} featured games loaded from `/api/v1/games`</li>
              <li>{topGenres.length} top genres loaded from `/api/v1/analytics/top-genres`</li>
              <li>{releaseTrends.length} release-trend points previewed from analytics</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {featureCards.map(({ title, description, icon: Icon }) => (
          <Card key={title} className="animate-rise">
            <CardHeader>
              <div className="mb-4 inline-flex w-fit rounded-2xl bg-primary p-3 text-primary-foreground">
                <Icon className="size-5" />
              </div>
              <CardTitle>{title}</CardTitle>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent className="text-sm leading-6 text-muted">
              The app shell is ready to receive the API client, BFF auth routes, and the feature
              pages described in the implementation plan.
            </CardContent>
          </Card>
        ))}
      </section>

      {hasShowcaseData ? (
        <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <Card>
            <CardHeader className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <CardTitle>Featured games</CardTitle>
                <CardDescription>
                  Top catalog entries by positive reviews, pulled from the live games endpoint.
                </CardDescription>
              </div>
              <Button asChild variant="ghost">
                <Link href="/games">
                  Browse full catalog
                  <ChevronRight className="size-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {games.map((game) => (
                <Link
                  key={game.id}
                  href={`/games/${game.id}`}
                  className="group rounded-[1.4rem] border border-border/80 bg-white/80 p-4 transition hover:-translate-y-1 hover:border-accent/50"
                >
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <Badge variant="accent">{game.is_free ? "Free" : formatCurrency(game.price_usd)}</Badge>
                    <div className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted">
                      <Gamepad2 className="size-4" />
                      #{game.steam_app_id}
                    </div>
                  </div>
                  <h3 className="font-display text-xl font-semibold text-primary">{game.name}</h3>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-muted">
                    <div>
                      <p className="text-xs uppercase tracking-[0.16em]">Score</p>
                      <p className="mt-1 font-medium text-primary">
                        {game.metacritic_score ?? "Unrated"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.16em]">Positive reviews</p>
                      <p className="mt-1 font-medium text-primary">
                        {formatCompactNumber(game.positive_reviews)}
                      </p>
                    </div>
                  </div>
                  <p className="mt-4 text-sm text-muted group-hover:text-primary">
                    Open details, then branch into similarity and collection actions.
                  </p>
                </Link>
              ))}
            </CardContent>
          </Card>

          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Top genres snapshot</CardTitle>
                <CardDescription>A quick analytics read on the strongest taxonomy buckets.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {topGenres.map((genre) => (
                  <div key={genre.slug} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-primary">{genre.name}</span>
                      <span className="text-muted">{formatCompactNumber(genre.game_count)}</span>
                    </div>
                    <div className="h-2 rounded-full bg-background-alt">
                      <div
                        className="h-2 rounded-full bg-accent"
                        style={{
                          width: `${Math.max(
                            12,
                            topGenres[0] ? (genre.game_count / topGenres[0].game_count) * 100 : 0,
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Release trends preview</CardTitle>
                <CardDescription>Recent yearly game counts from the analytics endpoints.</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-3">
                {releaseTrends.map((row) => (
                  <div key={row.year} className="rounded-[1.2rem] bg-background-alt p-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-muted">{row.year}</p>
                    <p className="mt-2 font-display text-2xl font-semibold text-primary">
                      {formatCompactNumber(row.game_count)}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </section>
      ) : (
        <ErrorState description="The landing page could not load live backend data. Start the API and database, then refresh this page." />
      )}
    </div>
  );
}
