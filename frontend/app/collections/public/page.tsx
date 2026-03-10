import { CollectionCard } from "@/components/collections/collection-card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { buildQueryString } from "@/lib/api/normalizers";
import { PaginationNav } from "@/components/ui/pagination-nav";
import { listPublicCollections } from "@/lib/api/collections";
import { requireSession } from "@/lib/auth/guards";

function readString(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

function readNumber(value: string | undefined) {
  if (!value) {
    return 1;
  }

  const parsed = Number(value);
  return Number.isNaN(parsed) ? 1 : parsed;
}

function buildPublicCollectionsHref(page: number) {
  return `/collections/public${buildQueryString({ page })}`;
}

export default async function PublicCollectionsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { token } = await requireSession();
  const rawParams = await searchParams;
  const page = readNumber(readString(rawParams.page));
  let collections;
  try {
    collections = await listPublicCollections(token, page, 20, "game_count");
  } catch {
    return (
      <ErrorState description="Public collections could not be loaded from the backend. Confirm the API is running." />
    );
  }

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <Badge variant="outline">Public discovery</Badge>
        <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight">
          Browse public collections
        </h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-primary-foreground/76">
          This view is backed by `/api/v1/collections/public`, sorted by game count to highlight
          the most substantial public lists first.
        </p>
      </section>

      {collections.data.length > 0 ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {collections.data.map((collection) => (
              <CollectionCard
                key={collection.id}
                collection={collection}
                href={`/collections/${collection.id}`}
              />
            ))}
          </div>
          <PaginationNav
            nextHref={
              collections.pagination.page < collections.pagination.total_pages
                ? buildPublicCollectionsHref(collections.pagination.page + 1)
                : null
            }
            page={collections.pagination.page}
            previousHref={
              collections.pagination.page > 1
                ? buildPublicCollectionsHref(collections.pagination.page - 1)
                : null
            }
            totalPages={collections.pagination.total_pages}
          />
        </>
      ) : (
        <EmptyState
          title="No public collections found"
          description="Create a public collection from the protected dashboard and it will appear here."
        />
      )}
    </div>
  );
}
