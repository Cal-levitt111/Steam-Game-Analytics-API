import { getPaginated, getWrapped } from "@/lib/api/client";
import type {
  DeveloperDetail,
  GameListItem,
  GamesQuery,
  GenreDetail,
  PublisherDetail,
  TagDetail,
  TaxonomyListItem,
} from "@/lib/api/types";

export function listGenres(page = 1, perPage = 20) {
  return getPaginated<TaxonomyListItem>("/api/v1/genres", {
    query: { page, per_page: perPage },
  });
}

export async function getGenre(slug: string) {
  const response = await getWrapped<GenreDetail>(`/api/v1/genres/${slug}`);
  return response.data;
}

export function listGenreGames(slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/genres/${slug}/games`, { query });
}

export function listTags(page = 1, perPage = 20, q?: string) {
  return getPaginated<TaxonomyListItem>("/api/v1/tags", {
    query: { page, per_page: perPage, q },
  });
}

export async function getTag(slug: string) {
  const response = await getWrapped<TagDetail>(`/api/v1/tags/${slug}`);
  return response.data;
}

export function listTagGames(slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/tags/${slug}/games`, { query });
}

export function listDevelopers(page = 1, perPage = 20, q?: string) {
  return getPaginated<TaxonomyListItem>("/api/v1/developers", {
    query: { page, per_page: perPage, q },
  });
}

export async function getDeveloper(slug: string) {
  const response = await getWrapped<DeveloperDetail>(`/api/v1/developers/${slug}`);
  return response.data;
}

export function listDeveloperGames(slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/developers/${slug}/games`, { query });
}

export function listPublishers(page = 1, perPage = 20) {
  return getPaginated<TaxonomyListItem>("/api/v1/publishers", {
    query: { page, per_page: perPage },
  });
}

export async function getPublisher(slug: string) {
  const response = await getWrapped<PublisherDetail>(`/api/v1/publishers/${slug}`);
  return response.data;
}

export function listPublisherGames(slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/publishers/${slug}/games`, { query });
}
