import { AnalyticsDashboard } from "@/components/analytics/analytics-dashboard";
import { Badge } from "@/components/ui/badge";
import { ErrorState } from "@/components/ui/error-state";
import {
  getFreeVsPaid,
  getPlatformBreakdown,
  getPriceDistribution,
  getReleaseTrends,
  getReviewSentiment,
  getScoreByGenre,
  getTopDevelopers,
  getTopGenres,
} from "@/lib/api/analytics";

export default async function AnalyticsPage() {
  const [
    releaseTrendsResult,
    topGenresResult,
    topDevelopersResult,
    priceDistributionResult,
    freeVsPaidResult,
    platformBreakdownResult,
    reviewSentimentResult,
    scoreByGenreResult,
  ] = await Promise.allSettled([
    getReleaseTrends(),
    getTopGenres(8),
    getTopDevelopers({ limit: 8 }),
    getPriceDistribution(),
    getFreeVsPaid(),
    getPlatformBreakdown(),
    getReviewSentiment(),
    getScoreByGenre(),
  ]);

  const data = {
    releaseTrends:
      releaseTrendsResult.status === "fulfilled" ? releaseTrendsResult.value.data : [],
    topGenres: topGenresResult.status === "fulfilled" ? topGenresResult.value.data : [],
    topDevelopers:
      topDevelopersResult.status === "fulfilled" ? topDevelopersResult.value.data : [],
    priceDistribution:
      priceDistributionResult.status === "fulfilled" ? priceDistributionResult.value.data : [],
    freeVsPaid: freeVsPaidResult.status === "fulfilled" ? freeVsPaidResult.value.data : [],
    platformBreakdown:
      platformBreakdownResult.status === "fulfilled" ? platformBreakdownResult.value.data : [],
    reviewSentiment:
      reviewSentimentResult.status === "fulfilled" ? reviewSentimentResult.value.data : [],
    scoreByGenre:
      scoreByGenreResult.status === "fulfilled" ? scoreByGenreResult.value.data : [],
  };

  const hasAnyData = Object.values(data).some((value) => value.length > 0);

  if (!hasAnyData) {
    return (
      <ErrorState description="Analytics endpoints could not be reached. Start the backend and ensure the seeded data is loaded." />
    );
  }

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <Badge variant="outline">Analytics dashboard</Badge>
        <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight">
          Explore the API&apos;s aggregate endpoints.
        </h1>
        <p className="mt-3 max-w-3xl text-base leading-7 text-primary-foreground/76">
          This page combines the analytics routes into a single dashboard with charts and summary
          cards so the demo surfaces both the exploratory and analytical value of the backend.
        </p>
      </section>

      <AnalyticsDashboard {...data} />
    </div>
  );
}
