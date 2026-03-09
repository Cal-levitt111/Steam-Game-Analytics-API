export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export type QueryValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | Array<string | number | boolean>;

export type ApiErrorPayload = {
  code: string;
  message: string;
  detail: JsonValue | null;
};

export type PaginationMeta = {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  next: string | null;
  prev: string | null;
};

export type PaginatedEnvelope<T> = {
  data: T[];
  pagination: PaginationMeta;
};

export type AnalyticsEnvelope<T> = {
  data: T[];
  generated_at: string;
  query_params: Record<string, JsonValue>;
};

export type WrappedData<T> = {
  data: T;
};

export type NamedSlug = {
  id: number;
  name: string;
  slug: string;
};

export type UserRead = {
  id: number;
  email: string;
  display_name: string | null;
  created_at: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  display_name?: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type UpdateMePayload = {
  display_name?: string;
  password?: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type GameListItem = {
  id: number;
  steam_app_id: number;
  name: string;
  release_date: string | null;
  price_usd: number | string | null;
  is_free: boolean;
  metacritic_score: number | null;
  positive_reviews: number;
  negative_reviews: number;
  windows: boolean;
  mac: boolean;
  linux: boolean;
};

export type SearchGameItem = GameListItem & {
  rank: number | null;
};

export type SimilarGameItem = GameListItem & {
  similarity: number | null;
};

export type GameDetail = GameListItem & {
  about_the_game: string | null;
  required_age: number;
  estimated_owners: string | null;
  peak_ccu: number | null;
  discount_percent: number | null;
  dlc_count: number | null;
  supported_languages: string | null;
  full_audio_languages: string | null;
  reviews: string | null;
  website: string | null;
  support_url: string | null;
  support_email: string | null;
  header_image: string | null;
  metacritic_url: string | null;
  user_score: number | null;
  score_rank: string | null;
  achievements: number | null;
  recommendations: number | null;
  notes: string | null;
  average_playtime_forever: number | null;
  average_playtime_two_weeks: number | null;
  median_playtime_forever: number | null;
  median_playtime_two_weeks: number | null;
  screenshots: string | null;
  movies: string | null;
  created_at: string;
  genres: NamedSlug[];
  tags: NamedSlug[];
  categories: NamedSlug[];
  developers: NamedSlug[];
  publishers: NamedSlug[];
};

export type CollectionRead = {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  is_public: boolean;
  created_at: string;
  updated_at: string;
};

export type CollectionListItem = CollectionRead & {
  game_count: number;
};

export type CollectionDetail = CollectionRead & {
  games: GameListItem[];
};

export type CollectionCreatePayload = {
  name: string;
  description?: string;
  is_public?: boolean;
};

export type CollectionUpdatePayload = {
  name?: string;
  description?: string;
  is_public?: boolean;
};

export type CollectionMembershipResponse = {
  collection_id: number;
  game_id: number;
};

export type TaxonomyListItem = {
  id: number;
  name: string;
  slug: string;
  game_count: number;
};

export type GenreDetail = TaxonomyListItem & {
  top_games: GameListItem[];
};

export type TagDetail = TaxonomyListItem;

export type DeveloperDetail = TaxonomyListItem & {
  avg_metacritic_score: number | null;
};

export type PublisherDetail = TaxonomyListItem;

export type ReleaseTrendRow = {
  year: number;
  game_count: number;
};

export type TopGenreRow = {
  name: string;
  slug: string;
  game_count: number;
};

export type GenreGrowthRow = {
  slug: string;
  year: number;
  game_count: number;
};

export type PriceDistributionRow = {
  bucket: string;
  count: number;
  pct: number;
};

export type TopDeveloperRow = {
  name: string;
  slug: string;
  game_count: number;
  avg_metacritic_score: number | null;
};

export type ScoreByGenreRow = {
  name: string;
  slug: string;
  avg_score: number | null;
  avg_sentiment: number | null;
  game_count: number;
};

export type FreeVsPaidRow = {
  type: "free" | "paid";
  game_count: number;
  avg_score: number | null;
  avg_reviews: number | null;
};

export type PlatformBreakdownRow = {
  total_games: number;
  windows: number;
  mac: number;
  linux: number;
  windows_mac: number;
  windows_linux: number;
  mac_linux: number;
  all_three: number;
};

export type ReviewSentimentRow = {
  bucket: string;
  count: number;
  pct: number;
};

export type GamesQuery = {
  page?: number;
  per_page?: number;
  genre?: string;
  tag?: string;
  developer?: string;
  publisher?: string;
  platform?: "windows" | "mac" | "linux";
  is_free?: boolean;
  min_price?: number;
  max_price?: number;
  min_score?: number;
  release_from?: string;
  release_to?: string;
  sort?: "name" | "price_usd" | "metacritic_score" | "release_date" | "positive_reviews";
  order?: "asc" | "desc";
};

export type SearchQuery = {
  q: string;
  page?: number;
  per_page?: number;
  genre?: string;
  tag?: string;
  is_free?: boolean;
  min_score?: number;
};

export type AnalyticsTopDevelopersQuery = {
  sort?: "game_count" | "avg_metacritic_score";
  limit?: number;
};

export type AnalyticsGenreGrowthQuery = {
  genres?: string;
  from?: number;
  to?: number;
};

export type ReleaseTrendQuery = {
  release_from?: string;
  release_to?: string;
};
