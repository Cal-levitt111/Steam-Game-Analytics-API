import { getAnalytics } from "@/lib/api/client";
import type {
  AnalyticsGenreGrowthQuery,
  AnalyticsTopDevelopersQuery,
  FreeVsPaidRow,
  GenreGrowthRow,
  PlatformBreakdownRow,
  PriceDistributionRow,
  ReleaseTrendQuery,
  ReleaseTrendRow,
  ReviewSentimentRow,
  ScoreByGenreRow,
  TopDeveloperRow,
  TopGenreRow,
} from "@/lib/api/types";

export function getReleaseTrends(accessToken: string, query?: ReleaseTrendQuery) {
  return getAnalytics<ReleaseTrendRow>("/api/v1/analytics/release-trends", {
    accessToken,
    query,
  });
}

export function getTopGenres(accessToken: string, limit = 10) {
  return getAnalytics<TopGenreRow>("/api/v1/analytics/top-genres", {
    accessToken,
    query: { limit },
  });
}

export function getGenreGrowth(accessToken: string, query?: AnalyticsGenreGrowthQuery) {
  return getAnalytics<GenreGrowthRow>("/api/v1/analytics/genre-growth", {
    accessToken,
    query,
  });
}

export function getPriceDistribution(accessToken: string) {
  return getAnalytics<PriceDistributionRow>("/api/v1/analytics/price-distribution", { accessToken });
}

export function getTopDevelopers(accessToken: string, query?: AnalyticsTopDevelopersQuery) {
  return getAnalytics<TopDeveloperRow>("/api/v1/analytics/top-developers", {
    accessToken,
    query,
  });
}

export function getScoreByGenre(accessToken: string) {
  return getAnalytics<ScoreByGenreRow>("/api/v1/analytics/score-by-genre", { accessToken });
}

export function getFreeVsPaid(accessToken: string) {
  return getAnalytics<FreeVsPaidRow>("/api/v1/analytics/free-vs-paid", { accessToken });
}

export function getPlatformBreakdown(accessToken: string) {
  return getAnalytics<PlatformBreakdownRow>("/api/v1/analytics/platform-breakdown", {
    accessToken,
  });
}

export function getReviewSentiment(accessToken: string) {
  return getAnalytics<ReviewSentimentRow>("/api/v1/analytics/review-sentiment", {
    accessToken,
  });
}
