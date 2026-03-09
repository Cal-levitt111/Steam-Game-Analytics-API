"use client";

import { useActionState } from "react";

import { createCollectionAction, type CreateCollectionState } from "@/app/collections/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

const initialState: CreateCollectionState = {};

export function CreateCollectionForm() {
  const [state, action, pending] = useActionState(createCollectionAction, initialState);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create a collection</CardTitle>
        <CardDescription>
          Collections are stored against the authenticated user and can be private or public.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form action={action} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="name">
              Name
            </label>
            <Input id="name" name="name" placeholder="Weekend multiplayer shortlist" required />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="description">
              Description
            </label>
            <Textarea
              id="description"
              name="description"
              placeholder="Why these games belong together, who this collection is for, and what you want to test."
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-primary" htmlFor="visibility">
              Visibility
            </label>
            <Select defaultValue="private" id="visibility" name="visibility">
              <option value="private">Private</option>
              <option value="public">Public</option>
            </Select>
          </div>

          {state.error ? (
            <div className="rounded-2xl border border-danger/20 bg-danger/8 px-4 py-3 text-sm text-danger">
              {state.error}
            </div>
          ) : null}

          <Button className="w-full" disabled={pending}>
            {pending ? "Creating collection..." : "Create collection"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
