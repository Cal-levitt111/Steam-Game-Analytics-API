import Link from "next/link";

import { Button } from "@/components/ui/button";

type PaginationNavProps = {
  page: number;
  totalPages: number;
  previousHref: string | null;
  nextHref: string | null;
};

export function PaginationNav({
  page,
  totalPages,
  previousHref,
  nextHref,
}: PaginationNavProps) {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <div className="flex flex-col gap-3 rounded-[1.4rem] border border-border/80 bg-card p-4 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm text-muted">
        Page {page} of {totalPages}
      </p>
      <div className="flex gap-2">
        <Button asChild variant="outline" disabled={!previousHref}>
          {previousHref ? <Link href={previousHref}>Previous</Link> : <span>Previous</span>}
        </Button>
        <Button asChild variant="outline" disabled={!nextHref}>
          {nextHref ? <Link href={nextHref}>Next</Link> : <span>Next</span>}
        </Button>
      </div>
    </div>
  );
}
