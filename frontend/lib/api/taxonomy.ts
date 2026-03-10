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

export function listGenres(accessToken: string, page = 1, perPage = 20) {
  return getPaginated<TaxonomyListItem>("/api/v1/genres", {
    accessToken,
    query: { page, per_page: perPage },
  });
}

export async function getGenre(accessToken: string, slug: string) {
  const response = await getWrapped<GenreDetail>(`/api/v1/genres/${slug}`, { accessToken });
  return response.data;
}

export function listGenreGames(accessToken: string, slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/genres/${slug}/games`, { accessToken, query });
}

export function listTags(accessToken: string, page = 1, perPage = 20, q?: string) {
  return getPaginated<TaxonomyListItem>("/api/v1/tags", {
    accessToken,
    query: { page, per_page: perPage, q },
  });
}

export async function getTag(accessToken: string, slug: string) {
  const response = await getWrapped<TagDetail>(`/api/v1/tags/${slug}`, { accessToken });
  return response.data;
}

export function listTagGames(accessToken: string, slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/tags/${slug}/games`, { accessToken, query });
}

export function listDevelopers(accessToken: string, page = 1, perPage = 20, q?: string) {
  return getPaginated<TaxonomyListItem>("/api/v1/developers", {
    accessToken,
    query: { page, per_page: perPage, q },
  });
}

export async function getDeveloper(accessToken: string, slug: string) {
  const response = await getWrapped<DeveloperDetail>(`/api/v1/developers/${slug}`, { accessToken });
  return response.data;
}

export function listDeveloperGames(accessToken: string, slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/developers/${slug}/games`, { accessToken, query });
}

export function listPublishers(accessToken: string, page = 1, perPage = 20) {
  return getPaginated<TaxonomyListItem>("/api/v1/publishers", {
    accessToken,
    query: { page, per_page: perPage },
  });
}

export async function getPublisher(accessToken: string, slug: string) {
  const response = await getWrapped<PublisherDetail>(`/api/v1/publishers/${slug}`, { accessToken });
  return response.data;
}

export function listPublisherGames(accessToken: string, slug: string, query?: GamesQuery) {
  return getPaginated<GameListItem>(`/api/v1/publishers/${slug}/games`, { accessToken, query });
}
