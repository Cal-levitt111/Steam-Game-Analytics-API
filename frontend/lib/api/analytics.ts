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

export function getReleaseTrends(query?: ReleaseTrendQuery) {
  return getAnalytics<ReleaseTrendRow>("/api/v1/analytics/release-trends", { query });
}

export function getTopGenres(limit = 10) {
  return getAnalytics<TopGenreRow>("/api/v1/analytics/top-genres", {
    query: { limit },
  });
}

export function getGenreGrowth(query?: AnalyticsGenreGrowthQuery) {
  return getAnalytics<GenreGrowthRow>("/api/v1/analytics/genre-growth", { query });
}

export function getPriceDistribution() {
  return getAnalytics<PriceDistributionRow>("/api/v1/analytics/price-distribution");
}

export function getTopDevelopers(query?: AnalyticsTopDevelopersQuery) {
  return getAnalytics<TopDeveloperRow>("/api/v1/analytics/top-developers", { query });
}

export function getScoreByGenre() {
  return getAnalytics<ScoreByGenreRow>("/api/v1/analytics/score-by-genre");
}

export function getFreeVsPaid() {
  return getAnalytics<FreeVsPaidRow>("/api/v1/analytics/free-vs-paid");
}

export function getPlatformBreakdown() {
  return getAnalytics<PlatformBreakdownRow>("/api/v1/analytics/platform-breakdown");
}

export function getReviewSentiment() {
  return getAnalytics<ReviewSentimentRow>("/api/v1/analytics/review-sentiment");
}
