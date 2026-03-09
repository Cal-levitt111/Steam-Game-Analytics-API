import {
  getModel,
  getPaginated,
  getWrapped,
} from "@/lib/api/client";
import type {
  GameDetail,
  GameListItem,
  GamesQuery,
  SearchGameItem,
  SearchQuery,
  SimilarGameItem,
} from "@/lib/api/types";

export function listGames(query?: GamesQuery) {
  return getPaginated<GameListItem>("/api/v1/games", { query });
}

export function getGame(gameId: number) {
  return getModel<GameDetail>(`/api/v1/games/${gameId}`);
}

export async function getSimilarGames(gameId: number, limit = 10) {
  const response = await getWrapped<SimilarGameItem[]>(`/api/v1/games/${gameId}/similar`, {
    query: { limit },
  });
  return response.data;
}

export function searchGames(query: SearchQuery) {
  return getPaginated<SearchGameItem>("/api/v1/search", { query });
}
