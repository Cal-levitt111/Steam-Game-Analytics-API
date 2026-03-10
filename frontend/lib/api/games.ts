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

export function listGames(accessToken: string, query?: GamesQuery) {
  return getPaginated<GameListItem>("/api/v1/games", { accessToken, query });
}

export function getGame(accessToken: string, gameId: number) {
  return getModel<GameDetail>(`/api/v1/games/${gameId}`, { accessToken });
}

export async function getSimilarGames(accessToken: string, gameId: number, limit = 10) {
  const response = await getWrapped<SimilarGameItem[]>(`/api/v1/games/${gameId}/similar`, {
    accessToken,
    query: { limit },
  });
  return response.data;
}

export function searchGames(accessToken: string, query: SearchQuery) {
  return getPaginated<SearchGameItem>("/api/v1/search", { accessToken, query });
}
