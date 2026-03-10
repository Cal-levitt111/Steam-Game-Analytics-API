import {
  deleteVoid,
  getModel,
  getPaginated,
  postModel,
  postWrapped,
  putModel,
} from "@/lib/api/client";
import type {
  CollectionCreatePayload,
  CollectionDetail,
  CollectionListItem,
  CollectionMembershipResponse,
  CollectionRead,
  CollectionUpdatePayload,
} from "@/lib/api/types";

export function listMyCollections(accessToken: string, page = 1, perPage = 20) {
  return getPaginated<CollectionListItem>("/api/v1/collections", {
    accessToken,
    query: { page, per_page: perPage },
  });
}

export function listPublicCollections(page = 1, perPage = 20, sort: "created_at" | "game_count" = "created_at") {
  return getPaginated<CollectionListItem>("/api/v1/collections/public", {
    query: { page, per_page: perPage, sort },
  });
}

export function getCollection(collectionId: number, accessToken?: string) {
  return getModel<CollectionDetail>(`/api/v1/collections/${collectionId}`, {
    accessToken,
  });
}

export function createCollection(accessToken: string, payload: CollectionCreatePayload) {
  return postModel<CollectionRead>("/api/v1/collections", {
    accessToken,
    body: payload,
  });
}

export function updateCollection(
  accessToken: string,
  collectionId: number,
  payload: CollectionUpdatePayload,
) {
  return putModel<CollectionRead>(`/api/v1/collections/${collectionId}`, {
    accessToken,
    body: payload,
  });
}

export function deleteCollection(accessToken: string, collectionId: number) {
  return deleteVoid(`/api/v1/collections/${collectionId}`, { accessToken });
}

export async function addGameToCollection(accessToken: string, collectionId: number, gameId: number) {
  const response = await postWrapped<CollectionMembershipResponse>(
    `/api/v1/collections/${collectionId}/games/${gameId}`,
    { accessToken },
  );
  return response.data;
}

export function removeGameFromCollection(accessToken: string, collectionId: number, gameId: number) {
  return deleteVoid(`/api/v1/collections/${collectionId}/games/${gameId}`, { accessToken });
}
