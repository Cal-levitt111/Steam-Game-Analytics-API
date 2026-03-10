"use client";

import Link from "next/link";
import { useActionState } from "react";

import {
  addGameToCollectionAction,
  type CollectionMembershipState,
} from "@/app/collections/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import type { CollectionListItem } from "@/lib/api/types";

const initialState: CollectionMembershipState = {};

export function AddToCollectionForm({
  collections,
  gameId,
}: {
  collections: CollectionListItem[];
  gameId: number;
}) {
  const [state, action, pending] = useActionState(addGameToCollectionAction, initialState);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Save to a collection</CardTitle>
        <CardDescription>
          Authenticated action backed by the collection membership endpoint.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {collections.length > 0 ? (
          <form action={action} className="space-y-4">
            <input name="game_id" type="hidden" value={gameId} />
            <div className="space-y-2">
              <label className="text-sm font-medium text-primary" htmlFor="collection_id">
                Choose a collection
              </label>
              <Select defaultValue={collections[0]?.id.toString()} id="collection_id" name="collection_id">
                {collections.map((collection) => (
                  <option key={collection.id} value={collection.id}>
                    {collection.name} ({collection.is_public ? "public" : "private"})
                  </option>
                ))}
              </Select>
            </div>

            {state.error ? (
              <div className="rounded-2xl border border-danger/20 bg-danger/8 px-4 py-3 text-sm text-danger">
                {state.error}
              </div>
            ) : null}
            {state.success ? (
              <div className="rounded-2xl border border-accent/20 bg-accent/8 px-4 py-3 text-sm text-accent-foreground">
                {state.success}
              </div>
            ) : null}

            <Button className="w-full" disabled={pending}>
              {pending ? "Adding game..." : "Add to collection"}
            </Button>
          </form>
        ) : (
          <div className="space-y-4">
            <p className="text-sm leading-6 text-muted">
              You need at least one collection before this game can be saved.
            </p>
            <Button asChild variant="secondary">
              <Link href="/collections">Create a collection</Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
