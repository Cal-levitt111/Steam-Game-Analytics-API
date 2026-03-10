import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import type { GameListItem } from "@/lib/api/types";
import { formatCompactNumber, formatCurrency } from "@/lib/formatters";

export function GameCatalogCard({ game }: { game: GameListItem }) {
  const platformFlags = [
    game.windows ? "Windows" : null,
    game.mac ? "Mac" : null,
    game.linux ? "Linux" : null,
  ].filter(Boolean);

  return (
    <Link
      href={`/games/${game.id}`}
      className="group rounded-[1.5rem] border border-border/80 bg-card p-5 transition hover:-translate-y-1 hover:border-accent/50 hover:shadow-[0_20px_50px_rgba(16,32,51,0.1)]"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-2">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-primary">
            {game.name}
          </h2>
          <p className="text-sm text-muted">
            Released {game.release_date ?? "unknown"} • Steam App #{game.steam_app_id}
          </p>
        </div>
        <Badge variant="accent">{game.is_free ? "Free" : formatCurrency(game.price_usd)}</Badge>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-4 text-sm">
        <div className="rounded-[1.2rem] bg-background-alt p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Metacritic</p>
          <p className="mt-2 font-medium text-primary">{game.metacritic_score ?? "Unrated"}</p>
        </div>
        <div className="rounded-[1.2rem] bg-background-alt p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-muted">Positive reviews</p>
          <p className="mt-2 font-medium text-primary">
            {formatCompactNumber(game.positive_reviews)}
          </p>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {platformFlags.length > 0 ? (
          platformFlags.map((platform) => <Badge key={platform}>{platform}</Badge>)
        ) : (
          <Badge>No platform data</Badge>
        )}
      </div>

      <p className="mt-5 text-sm text-muted group-hover:text-primary">
        Open details to inspect metadata, similarity, and collection actions.
      </p>
    </Link>
  );
}
