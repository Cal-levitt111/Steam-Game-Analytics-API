import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { TaxonomyListItem } from "@/lib/api/types";

type CatalogFilterValues = {
  genre?: string;
  tag?: string;
  developer?: string;
  publisher?: string;
  platform?: string;
  is_free?: string;
  min_price?: string;
  max_price?: string;
  min_score?: string;
  release_from?: string;
  release_to?: string;
  sort?: string;
  order?: string;
};

type CatalogFilterPanelProps = {
  values: CatalogFilterValues;
  genres: TaxonomyListItem[];
  tags: TaxonomyListItem[];
  developers: TaxonomyListItem[];
  publishers: TaxonomyListItem[];
};

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-primary">{label}</label>
      {children}
    </div>
  );
}

export function CatalogFilterPanel({
  values,
  genres,
  tags,
  developers,
  publishers,
}: CatalogFilterPanelProps) {
  return (
    <div className="space-y-4">
      <details className="rounded-[1.6rem] border border-border/80 bg-card p-4 lg:hidden" open>
        <summary className="cursor-pointer list-none text-base font-semibold text-primary">
          Filters and sorting
        </summary>
        <div className="mt-4">
          <FilterForm
            values={values}
            genres={genres}
            tags={tags}
            developers={developers}
            publishers={publishers}
          />
        </div>
      </details>

      <div className="hidden lg:block">
        <FilterForm
          values={values}
          genres={genres}
          tags={tags}
          developers={developers}
          publishers={publishers}
        />
      </div>
    </div>
  );
}

function FilterForm({
  values,
  genres,
  tags,
  developers,
  publishers,
}: CatalogFilterPanelProps) {
  return (
    <form className="space-y-4 rounded-[1.6rem] border border-border/80 bg-card p-5" method="GET">
      <div className="space-y-1">
        <p className="font-display text-2xl font-semibold text-primary">Catalog filters</p>
        <p className="text-sm leading-6 text-muted">
          Every control maps directly to a supported `/api/v1/games` query parameter.
        </p>
      </div>

      <Field label="Genre">
        <Select defaultValue={values.genre ?? ""} name="genre">
          <option value="">Any genre</option>
          {genres.map((genre) => (
            <option key={genre.slug} value={genre.slug}>
              {genre.name}
            </option>
          ))}
        </Select>
      </Field>

      <Field label="Tag">
        <Select defaultValue={values.tag ?? ""} name="tag">
          <option value="">Any tag</option>
          {tags.map((tag) => (
            <option key={tag.slug} value={tag.slug}>
              {tag.name}
            </option>
          ))}
        </Select>
      </Field>

      <Field label="Developer">
        <Select defaultValue={values.developer ?? ""} name="developer">
          <option value="">Any developer</option>
          {developers.map((developer) => (
            <option key={developer.slug} value={developer.slug}>
              {developer.name}
            </option>
          ))}
        </Select>
      </Field>

      <Field label="Publisher">
        <Select defaultValue={values.publisher ?? ""} name="publisher">
          <option value="">Any publisher</option>
          {publishers.map((publisher) => (
            <option key={publisher.slug} value={publisher.slug}>
              {publisher.name}
            </option>
          ))}
        </Select>
      </Field>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Platform">
          <Select defaultValue={values.platform ?? ""} name="platform">
            <option value="">Any platform</option>
            <option value="windows">Windows</option>
            <option value="mac">Mac</option>
            <option value="linux">Linux</option>
          </Select>
        </Field>

        <Field label="Free / paid">
          <Select defaultValue={values.is_free ?? ""} name="is_free">
            <option value="">Any pricing</option>
            <option value="true">Free only</option>
            <option value="false">Paid only</option>
          </Select>
        </Field>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Min price">
          <Input defaultValue={values.min_price ?? ""} min="0" name="min_price" step="0.01" type="number" />
        </Field>
        <Field label="Max price">
          <Input defaultValue={values.max_price ?? ""} min="0" name="max_price" step="0.01" type="number" />
        </Field>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Min score">
          <Input defaultValue={values.min_score ?? ""} max="100" min="0" name="min_score" type="number" />
        </Field>
        <Field label="Sort">
          <Select defaultValue={values.sort ?? "name"} name="sort">
            <option value="name">Name</option>
            <option value="price_usd">Price</option>
            <option value="metacritic_score">Metacritic</option>
            <option value="release_date">Release date</option>
            <option value="positive_reviews">Positive reviews</option>
          </Select>
        </Field>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Release from">
          <Input defaultValue={values.release_from ?? ""} name="release_from" type="date" />
        </Field>
        <Field label="Release to">
          <Input defaultValue={values.release_to ?? ""} name="release_to" type="date" />
        </Field>
      </div>

      <Field label="Order">
        <Select defaultValue={values.order ?? "asc"} name="order">
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </Select>
      </Field>

      <div className="flex gap-2">
        <Button className="flex-1">Apply filters</Button>
        <Button asChild className="flex-1" variant="outline">
          <Link href="/games">Reset</Link>
        </Button>
      </div>
    </form>
  );
}
