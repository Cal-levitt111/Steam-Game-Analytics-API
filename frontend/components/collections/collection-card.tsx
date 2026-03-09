import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { CollectionListItem } from "@/lib/api/types";

export function CollectionCard({
  collection,
  href,
}: {
  collection: CollectionListItem;
  href: string;
}) {
  return (
    <Link href={href}>
      <Card className="h-full transition hover:-translate-y-1 hover:border-accent/50">
        <CardHeader>
          <div className="flex flex-wrap items-center gap-2">
            <Badge>{collection.is_public ? "Public" : "Private"}</Badge>
            <Badge variant="accent">{collection.game_count} games</Badge>
          </div>
          <CardTitle>{collection.name}</CardTitle>
          <CardDescription>{collection.description ?? "No description provided."}</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted">
          Updated {new Date(collection.updated_at).toLocaleDateString()}
        </CardContent>
      </Card>
    </Link>
  );
}
