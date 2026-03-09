"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type {
  FreeVsPaidRow,
  PlatformBreakdownRow,
  PriceDistributionRow,
  ReleaseTrendRow,
  ReviewSentimentRow,
  ScoreByGenreRow,
  TopDeveloperRow,
  TopGenreRow,
} from "@/lib/api/types";

const palette = ["#0f3d5e", "#3cb6a2", "#d8f163", "#e29c45", "#b64235", "#7b8794"];

type AnalyticsDashboardProps = {
  releaseTrends: ReleaseTrendRow[];
  topGenres: TopGenreRow[];
  topDevelopers: TopDeveloperRow[];
  priceDistribution: PriceDistributionRow[];
  freeVsPaid: FreeVsPaidRow[];
  platformBreakdown: PlatformBreakdownRow[];
  reviewSentiment: ReviewSentimentRow[];
  scoreByGenre: ScoreByGenreRow[];
};

function ChartShell({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="min-w-0">{children}</CardContent>
    </Card>
  );
}

export function AnalyticsDashboard({
  releaseTrends,
  topGenres,
  topDevelopers,
  priceDistribution,
  freeVsPaid,
  platformBreakdown,
  reviewSentiment,
  scoreByGenre,
}: AnalyticsDashboardProps) {
  const platformRow = platformBreakdown[0];

  return (
    <div className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-2">
        <ChartShell
          title="Release trends"
          description="Game counts by release year from the analytics endpoint."
        >
          <div className="h-80 min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={releaseTrends}>
                <defs>
                  <linearGradient id="releaseTrend" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#3cb6a2" stopOpacity={0.9} />
                    <stop offset="95%" stopColor="#3cb6a2" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(16,32,51,0.08)" vertical={false} />
                <XAxis dataKey="year" stroke="#5c6a7b" />
                <YAxis stroke="#5c6a7b" />
                <Tooltip />
                <Area
                  dataKey="game_count"
                  fill="url(#releaseTrend)"
                  stroke="#0f3d5e"
                  strokeWidth={2}
                  type="monotone"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartShell>

        <ChartShell
          title="Top genres"
          description="Highest-volume genres surfaced from the taxonomy analytics."
        >
          <div className="h-80 min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topGenres}>
                <CartesianGrid stroke="rgba(16,32,51,0.08)" vertical={false} />
                <XAxis dataKey="name" stroke="#5c6a7b" tickLine={false} />
                <YAxis stroke="#5c6a7b" />
                <Tooltip />
                <Bar dataKey="game_count" fill="#0f3d5e" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartShell>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <ChartShell
          title="Price distribution"
          description="Bucketed price bands, including free games."
        >
          <div className="h-80 min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={priceDistribution}
                  dataKey="count"
                  innerRadius={60}
                  nameKey="bucket"
                  outerRadius={100}
                >
                  {priceDistribution.map((entry, index) => (
                    <Cell key={entry.bucket} fill={palette[index % palette.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartShell>

        <ChartShell
          title="Review sentiment"
          description="Distribution of positive review ratio buckets."
        >
          <div className="h-80 min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={reviewSentiment}>
                <CartesianGrid stroke="rgba(16,32,51,0.08)" vertical={false} />
                <XAxis dataKey="bucket" stroke="#5c6a7b" tickLine={false} />
                <YAxis stroke="#5c6a7b" />
                <Tooltip />
                <Bar dataKey="count" fill="#3cb6a2" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartShell>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <ChartShell
          title="Platform breakdown"
          description="Platform coverage counts derived from the games dataset."
        >
          <div className="grid gap-3 sm:grid-cols-2">
            {platformRow ? (
              Object.entries(platformRow).map(([key, value]) => (
                <div key={key} className="rounded-[1.2rem] bg-background-alt p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-muted">
                    {key.replaceAll("_", " ")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold text-primary">{value}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted">No platform data returned.</p>
            )}
          </div>
        </ChartShell>

        <ChartShell
          title="Free vs paid"
          description="Comparative view of catalog volume, average score, and review counts."
        >
          <div className="grid gap-4 md:grid-cols-2">
            {freeVsPaid.map((row, index) => (
              <div
                key={row.type}
                className="rounded-[1.4rem] border border-border/80 bg-white/80 p-5"
                style={{ boxShadow: `inset 0 0 0 1px ${palette[index % palette.length]}20` }}
              >
                <p className="text-xs uppercase tracking-[0.16em] text-muted">{row.type}</p>
                <p className="mt-2 font-display text-3xl font-semibold text-primary">
                  {row.game_count}
                </p>
                <div className="mt-4 space-y-2 text-sm text-muted">
                  <p>Average score: {row.avg_score?.toFixed(1) ?? "N/A"}</p>
                  <p>Average reviews: {row.avg_reviews?.toFixed(0) ?? "N/A"}</p>
                </div>
              </div>
            ))}
          </div>
        </ChartShell>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <ChartShell
          title="Top developers"
          description="Developers ranked by game count and average Metacritic score."
        >
          <div className="space-y-3">
            {topDevelopers.map((developer) => (
              <div
                key={developer.slug}
                className="flex items-center justify-between rounded-[1.2rem] bg-background-alt px-4 py-3 text-sm"
              >
                <div>
                  <p className="font-medium text-primary">{developer.name}</p>
                  <p className="text-muted">
                    Avg score {developer.avg_metacritic_score?.toFixed(1) ?? "N/A"}
                  </p>
                </div>
                <p className="font-medium text-primary">{developer.game_count} games</p>
              </div>
            ))}
          </div>
        </ChartShell>

        <ChartShell
          title="Score by genre"
          description="Average Metacritic score and sentiment for each genre."
        >
          <div className="space-y-3">
            {scoreByGenre.slice(0, 8).map((genre) => (
              <div
                key={genre.slug}
                className="flex items-center justify-between rounded-[1.2rem] bg-background-alt px-4 py-3 text-sm"
              >
                <div>
                  <p className="font-medium text-primary">{genre.name}</p>
                  <p className="text-muted">
                    Sentiment {genre.avg_sentiment ? `${(genre.avg_sentiment * 100).toFixed(1)}%` : "N/A"}
                  </p>
                </div>
                <p className="font-medium text-primary">
                  {genre.avg_score?.toFixed(1) ?? "N/A"}
                </p>
              </div>
            ))}
          </div>
        </ChartShell>
      </div>
    </div>
  );
}
