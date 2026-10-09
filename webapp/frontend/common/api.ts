/** API client for Calibre webapp. All calls go through Next.js API proxies (same-origin). */

/** Get stored Anna's Archive mirror URL(s) from backend. */
export async function getAnnasMirrors(): Promise<string[]> {
  const settings = await getSettings();
  return settings.annas_mirrors || [];
}

/** Store Anna's Archive mirror URL(s) in backend. */
export async function setAnnasMirrors(mirrors: string | string[]): Promise<void> {
  const annas_mirrors =
    typeof mirrors === 'string'
      ? mirrors
          .split(',')
          .map((m) => m.trim())
          .filter(Boolean)
      : mirrors;
  await updateSettings({ annas_mirrors });
}

/** Backend base URL.
 * - `NEXT_PUBLIC_API_BASE` wins when set (LAN / Tailscale / reverse-proxy setups).
 * - Dev defaults to '' (same-origin; Next.js rewrites /api to the backend — LAN-safe).
 * - Non-dev (incl. Tauri, which has no rewrite server) defaults to loopback backend.
 */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ??
  (process.env.NODE_ENV === 'development' ? '' : 'http://127.0.0.1:10720');

/** Base URL for fetch. Server needs absolute URL; client uses relative in dev. */
export function getBaseUrl(): string {
  return API_BASE;
}

async function fetchWithRetry(url: string, attempts = 15, delayMs = 400): Promise<Response> {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fetch(url);
    } catch (error) {
      lastError = error;
      if (i < attempts - 1) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
  }
  throw lastError;
}

export interface Book {
  id: number;
  title: string;
  authors: string[] | { name?: string }[];
  rating?: number;
  tags: string[] | { name?: string }[];
  formats?: string[] | { format?: string; path?: string; name?: string }[];
  cover_url?: string;
  comments?: string;
  description?: string;
  path?: string;
  uuid?: string;
  publisher?: string;
  pubdate?: string;
  series?: string | { name?: string };
  series_index?: number;
  timestamp?: string;
  last_modified?: string;
  identifiers?: Record<string, string>;
  /** Match snippet from full-text search (HTML may include <mark>). */
  snippet?: string;
}

/** Calibre stores `rating` on a 0–10 scale; five-star UI uses half steps (same as book modal). */
export function ratingToFiveStarCount(rating: number | undefined | null): number {
  if (rating == null || rating <= 0) return 0;
  return Math.min(5, Math.max(0, Math.round(rating / 2)));
}

export interface BookListResponse {
  items: Book[];
  total: number;
  page?: number;
  per_page?: number;
}

export type BookSortBy = 'title' | 'author' | 'series' | 'rating' | 'timestamp' | 'pubdate';
export type SortOrder = 'asc' | 'desc';

export interface BookQueryParams {
  limit?: number;
  offset?: number;
  author?: string;
  tag?: string;
  publisher?: string;
  series?: string;
  text?: string;
  title?: string;
  rating?: number;
  min_rating?: number;
  max_rating?: number;
  unrated?: boolean;
  formats?: string;
  pubdate_start?: string;
  pubdate_end?: string;
  added_after?: string;
  added_before?: string;
  has_publisher?: boolean;
  sort_by?: BookSortBy;
  sort_order?: SortOrder;
}

export async function getBooks(params?: BookQueryParams): Promise<BookListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.author) searchParams.set('author', params.author);
  if (params?.tag) searchParams.set('tag', params.tag);
  if (params?.publisher) searchParams.set('publisher', params.publisher);
  if (params?.series) searchParams.set('series', params.series);
  if (params?.text) searchParams.set('text', params.text);
  if (params?.title) searchParams.set('title', params.title);
  if (params?.rating) searchParams.set('rating', params.rating.toString());
  if (params?.min_rating) searchParams.set('min_rating', params.min_rating.toString());
  if (params?.max_rating) searchParams.set('max_rating', params.max_rating.toString());
  if (params?.unrated) searchParams.set('unrated', '1');
  if (params?.formats) searchParams.set('formats', params.formats);
  if (params?.pubdate_start) searchParams.set('pubdate_start', params.pubdate_start);
  if (params?.pubdate_end) searchParams.set('pubdate_end', params.pubdate_end);
  if (params?.added_after) searchParams.set('added_after', params.added_after);
  if (params?.added_before) searchParams.set('added_before', params.added_before);
  if (params?.has_publisher === true) searchParams.set('has_publisher', '1');
  if (params?.has_publisher === false) searchParams.set('has_publisher', '0');
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order);

  const response = await fetch(`${getBaseUrl()}/api/books?${searchParams}`);
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail = (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? '';
    } catch {
      detail = response.statusText;
    }
    const msg = detail
      ? `Failed to fetch books (${response.status}): ${detail}`
      : `Failed to fetch books (${response.status}). Run webapp\\start.ps1 from repo root.`;
    throw new Error(msg);
  }
  return response.json();
}

export function getBookCoverUrl(bookId: number): string {
  return `${getBaseUrl()}/api/books/${bookId}/cover`;
}

export async function getBook(id: number): Promise<Book> {
  const response = await fetch(`${getBaseUrl()}/api/books/${id}`);
  if (!response.ok) throw new Error('Failed to fetch book');
  return response.json();
}

export type FetchBookMetadataOnlineResult = {
  success: boolean;
  message?: string;
  warning?: string;
  error?: string;
};

/** Calibre-style “Download metadata” for an existing book (local library + Calibre CLI on PATH). */
export async function fetchBookMetadataOnline(
  bookId: number,
  options?: { includeCover?: boolean },
): Promise<FetchBookMetadataOnlineResult> {
  const include_cover = options?.includeCover !== false;
  const response = await fetch(`${getBaseUrl()}/api/books/${bookId}/fetch-metadata`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ include_cover }),
  });
  const data = (await response.json().catch(() => ({}))) as FetchBookMetadataOnlineResult & {
    detail?: string | { msg?: string }[];
  };
  if (!response.ok) {
    const detail = data.detail;
    const msg =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg ?? '').join('; ')
          : 'Metadata download failed';
    return { success: false, error: msg || `HTTP ${response.status}` };
  }
  return data;
}

export async function openBookViewer(bookId: number): Promise<void> {
  const response = await fetch(`${getBaseUrl()}/api/viewer/open-file`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ book_id: bookId }),
  });
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail =
        (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        (err as { message?: string }).message ??
        '';
    } catch {
      detail = response.statusText;
    }
    throw new Error(detail || `Failed to open book (${response.status})`);
  }
}

export async function searchBooks(params?: {
  query?: string;
  author?: string;
  tag?: string;
  min_rating?: number;
  fulltext?: boolean;
  limit?: number;
  offset?: number;
}): Promise<BookListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.query) searchParams.set('query', params.query);
  if (params?.author) searchParams.set('author', params.author);
  if (params?.tag) searchParams.set('tag', params.tag);
  if (params?.min_rating) searchParams.set('min_rating', params.min_rating.toString());
  if (params?.fulltext) searchParams.set('fulltext', '1');
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());

  const response = await fetch(`${getBaseUrl()}/api/search?${searchParams}`);
  if (!response.ok) throw new Error('Failed to search books');
  return response.json();
}

export interface Library {
  name: string;
  path: string;
  book_count?: number;
  size_mb?: number;
  is_active?: boolean;
}

export interface LibraryListResponse {
  libraries: Library[];
  current_library?: string;
  total_libraries: number;
}

export interface LibraryStats {
  library_name: string;
  total_books: number;
  total_authors: number;
  total_series: number;
  total_tags: number;
  format_distribution: Record<string, number>;
  language_distribution: Record<string, number>;
  rating_distribution: Record<string, number>;
  last_modified?: string;
}

export async function listLibraries(): Promise<LibraryListResponse> {
  const response = await fetchWithRetry(`${getBaseUrl()}/api/libraries/list`);
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail =
        (err as { hint?: string }).hint ??
        (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        '';
    } catch {
      detail = 'Run webapp\\start.ps1 from repo root.';
    }
    throw new Error(detail || `Failed to fetch libraries (${response.status})`);
  }
  const data = await response.json();
  return {
    libraries: data.libraries,
    current_library: data.current_library,
    total_libraries: data.total_libraries,
  };
}

export async function getLibraryStats(libraryName?: string): Promise<LibraryStats> {
  const params = libraryName ? `?library_name=${encodeURIComponent(libraryName)}` : '';
  const response = await fetch(`${getBaseUrl()}/api/libraries/stats${params}`);
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail = (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? '';
    } catch {
      detail = response.statusText;
    }
    throw new Error(detail || `Failed to fetch library stats (${response.status})`);
  }
  const data = await response.json();
  return normalizeLibraryStats(data);
}

function normalizeLibraryStats(data: Record<string, unknown>): LibraryStats {
  return {
    library_name: (data.library_name as string) ?? (data.library as string) ?? 'Unknown',
    total_books: (data.total_books as number) ?? (data.books as number) ?? 0,
    total_authors: (data.total_authors as number) ?? (data.authors as number) ?? 0,
    total_series: (data.total_series as number) ?? (data.series as number) ?? 0,
    total_tags: (data.total_tags as number) ?? (data.tags as number) ?? 0,
    format_distribution: (data.format_distribution as Record<string, number>) ?? {},
    language_distribution: (data.language_distribution as Record<string, number>) ?? {},
    rating_distribution: (data.rating_distribution as Record<string, number>) ?? {},
    last_modified: data.last_modified as string | undefined,
  };
}

export async function switchLibrary(libraryName: string): Promise<{
  success: boolean;
  library_name: string;
  library_path: string;
  message: string;
}> {
  const response = await fetch(`${getBaseUrl()}/api/libraries/switch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ library_name: libraryName }),
  });
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail = (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? '';
    } catch {
      detail = response.statusText;
    }
    throw new Error(detail || `Failed to switch library (${response.status})`);
  }
  return response.json();
}

export async function getHelp(level = 'basic', topic?: string): Promise<Record<string, unknown>> {
  const params = new URLSearchParams({ level });
  if (topic) params.set('topic', topic);
  const response = await fetch(`${getBaseUrl()}/api/system/help?${params}`);
  if (!response.ok) throw new Error('Failed to fetch help');
  return response.json();
}

export async function getSystemStatus(level = 'diagnostic'): Promise<Record<string, unknown>> {
  const base = getBaseUrl();
  const response = await fetch(`${base}/api/system/status?status_level=${level}`);
  if (!response.ok) throw new Error('Failed to fetch status');
  return response.json();
}

export interface LogsResponse {
  lines: string[];
  total: number;
  file?: string;
  error?: string;
}

export async function getLogs(params?: {
  tail?: number;
  filter?: string;
  level?: string;
}): Promise<LogsResponse> {
  const sp = new URLSearchParams();
  if (params?.tail) sp.set('tail', String(params.tail));
  if (params?.filter) sp.set('filter', params.filter);
  if (params?.level) sp.set('level', params.level);
  const base = getBaseUrl();
  const response = await fetch(`${base}/api/logs?${sp}`);
  if (!response.ok) throw new Error('Failed to fetch logs');
  return response.json();
}

export interface AuthorItem {
  id: number;
  name: string;
  book_count?: number;
}

export interface TagItem {
  id: number;
  name: string;
  book_count?: number;
}

export async function listAuthors(params?: {
  query?: string;
  limit?: number;
  offset?: number;
}): Promise<{ items: AuthorItem[]; total: number }> {
  const searchParams = new URLSearchParams();
  if (params?.query) searchParams.set('query', params.query);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  const response = await fetch(`${getBaseUrl()}/api/authors?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch authors');
  const data = await response.json();
  return { items: data.items ?? [], total: data.total ?? 0 };
}

export interface PublisherItem {
  id: number | null;
  name: string;
  book_count?: number;
}

export async function listPublishers(params?: {
  query?: string;
  limit?: number;
  offset?: number;
}): Promise<{
  items: PublisherItem[];
  total: number;
  error?: string;
  message?: string;
}> {
  const searchParams = new URLSearchParams();
  if (params?.query) searchParams.set('query', params.query);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  const response = await fetch(`${getBaseUrl()}/api/publishers?${searchParams}`);
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail = (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? '';
    } catch {
      detail = response.statusText;
    }
    throw new Error(detail || 'Failed to fetch publishers');
  }
  const data = await response.json();
  const rawItems = data.items ?? data.publishers ?? [];
  const items = Array.isArray(rawItems) ? rawItems : [];
  const total = typeof data.total === 'number' ? data.total : items.length;
  return {
    items,
    total,
    error: data.error as string | undefined,
    message: data.message as string | undefined,
  };
}

export interface SeriesItem {
  id: number;
  name: string;
  book_count?: number;
}

export async function listSeries(params?: {
  query?: string;
  limit?: number;
  offset?: number;
  letter?: string;
}): Promise<{
  items: SeriesItem[];
  total: number;
  error?: string;
  message?: string;
}> {
  const searchParams = new URLSearchParams();
  if (params?.query) searchParams.set('query', params.query);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.letter) searchParams.set('letter', params.letter);
  const response = await fetch(`${getBaseUrl()}/api/series?${searchParams}`);
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail = (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? '';
    } catch {
      detail = response.statusText;
    }
    throw new Error(detail || 'Failed to fetch series');
  }
  const data = await response.json();
  const rawItems = data.items ?? data.series ?? [];
  const items = Array.isArray(rawItems) ? rawItems : [];
  const total = typeof data.total === 'number' ? data.total : items.length;
  return {
    items,
    total,
    error: data.error as string | undefined,
    message: data.message as string | undefined,
  };
}

export async function getSeriesBooks(
  seriesId: number,
  params?: { limit?: number; offset?: number },
): Promise<{ items: Book[]; series?: { name?: string }; total?: number }> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  const q = searchParams.toString();
  const url = `${getBaseUrl()}/api/series/${seriesId}/books${q ? `?${q}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch series books');
  return response.json();
}

export interface AnnasSearchResult {
  title: string;
  author: string;
  formats: string;
  detail_url: string;
  detail_item: string;
}

export interface AnnasSearchResponse {
  success: boolean;
  query: string;
  results: AnnasSearchResult[];
  total_found: number;
  mirror_used?: string;
  error?: string;
}

export async function searchAnnas(params: {
  query: string;
  max_results?: number;
  mirrors?: string[];
}): Promise<AnnasSearchResponse> {
  const response = await fetch(`${getBaseUrl()}/api/annas/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: params.query,
      max_results: params.max_results ?? 20,
      mirrors: params.mirrors,
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

export interface AnnasDownloadResponse {
  success: boolean;
  title?: string;
  error_code?: string;
  message?: string;
  detail_url?: string;
}

export async function downloadAnnas(
  md5: string,
  options?: {
    format?: string;
    title?: string;
    authors?: string[];
    tags?: string[];
    series?: string;
    library_path?: string;
  },
): Promise<AnnasDownloadResponse> {
  const response = await fetch(`${getBaseUrl()}/api/annas/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      md5,
      target_format: options?.format,
      title: options?.title,
      authors: options?.authors,
      tags: options?.tags,
      series: options?.series,
      library_path: options?.library_path,
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

export interface ArxivSearchResult {
  id: string;
  title: string;
  authors: string[];
  summary: string;
  pdf_url: string;
  abs_url: string;
  published?: string;
}

export interface ArxivSearchResponse {
  success: boolean;
  results: ArxivSearchResult[];
  count: number;
  error?: string;
}

export async function searchArxiv(
  query: string,
  maxResults?: number,
): Promise<ArxivSearchResponse> {
  const response = await fetch(`${getBaseUrl()}/api/arxiv/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, max_results: maxResults }),
  });
  if (!response.ok) throw new Error('arXiv search failed');
  return response.json();
}

export async function importArxiv(
  arxivId: string,
  options?: {
    title?: string;
    authors?: string[];
    tags?: string[];
    series?: string;
    library_path?: string;
  },
): Promise<{ success: boolean; title?: string }> {
  const response = await fetch(`${getBaseUrl()}/api/arxiv/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      arxiv_id: arxivId,
      title: options?.title,
      authors: options?.authors,
      tags: options?.tags,
      series: options?.series,
      library_path: options?.library_path,
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

export interface GutenbergSearchResult {
  id: number;
  title: string;
  authors: string[];
  formats: Record<string, string>;
  detail_url: string;
}

export interface GutenbergSearchResponse {
  success: boolean;
  results: GutenbergSearchResult[];
  count: number;
  error?: string;
}

export async function searchGutenberg(query: string): Promise<GutenbergSearchResponse> {
  const response = await fetch(`${getBaseUrl()}/api/gutenberg/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) throw new Error('Gutenberg search failed');
  return response.json();
}

export async function importGutenberg(
  bookId: number,
  options?: {
    format?: string;
    title?: string;
    authors?: string[];
    tags?: string[];
    series?: string;
    library_path?: string;
  },
): Promise<{ success: boolean; title?: string }> {
  const response = await fetch(`${getBaseUrl()}/api/gutenberg/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      book_id: bookId,
      format: options?.format,
      title: options?.title,
      authors: options?.authors,
      tags: options?.tags,
      series: options?.series,
      library_path: options?.library_path,
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

export interface AppSettings {
  annas_mirrors: string[];
  gutenberg_mirror: string;
}

export async function getSettings(): Promise<AppSettings> {
  const response = await fetch(`${getBaseUrl()}/api/settings/`);
  if (!response.ok) throw new Error('Failed to fetch settings');
  return response.json();
}

export async function updateSettings(
  settings: Partial<AppSettings>,
): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${getBaseUrl()}/api/settings/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!response.ok) throw new Error('Failed to update settings');
  return response.json();
}

export async function listTags(params?: {
  search?: string;
  limit?: number;
  offset?: number;
  sort_by?: 'name' | 'book_count';
  sort_order?: 'asc' | 'desc';
  unused_only?: boolean;
  min_book_count?: number;
  max_book_count?: number;
}): Promise<{
  items: TagItem[];
  total: number;
  error?: string;
  message?: string;
}> {
  const searchParams = new URLSearchParams();
  if (params?.search) searchParams.set('search', params.search);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order);
  if (params?.unused_only) searchParams.set('unused_only', 'true');
  if (params?.min_book_count) searchParams.set('min_book_count', String(params.min_book_count));
  if (params?.max_book_count) searchParams.set('max_book_count', String(params.max_book_count));
  const response = await fetch(`${getBaseUrl()}/api/tags?${searchParams}`);
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail = (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? '';
    } catch {
      detail = response.statusText;
    }
    throw new Error(detail || 'Failed to fetch tags');
  }
  const data = await response.json();
  const rawItems = data.items ?? data.tags ?? data.results ?? [];
  const items = Array.isArray(rawItems) ? rawItems : [];
  const total = typeof data.total === 'number' ? data.total : items.length;
  return {
    items,
    total,
    error: data.error as string | undefined,
    message: data.message as string | undefined,
  };
}

export interface RagMetadataBuildResult {
  status?: string;
  books_indexed?: number;
  message?: string;
  execution_time_ms?: number;
  error?: string;
  success?: boolean;
}

export interface RagMetadataBuildStatus {
  status: string;
  current: number;
  total: number;
  percentage: number;
  message: string;
}

export async function ragMetadataBuildStatus(): Promise<RagMetadataBuildStatus> {
  const response = await fetch(`${getBaseUrl()}/api/rag/metadata/build/status`);
  if (!response.ok) throw new Error('Failed to fetch build status');
  return response.json();
}

export interface RagMetadataSearchHit {
  book_id: number;
  title: string;
  text: string;
  score?: number;
}

export interface RagMetadataSearchResult {
  results: RagMetadataSearchHit[];
  message?: string;
  execution_time_ms?: number;
  error?: string;
}

export async function ragMetadataBuild(forceRebuild = false): Promise<RagMetadataBuildResult> {
  const response = await fetch(
    `${getBaseUrl()}/api/rag/metadata/build?force_rebuild=${forceRebuild ? 'true' : 'false'}`,
    { method: 'POST' },
  );
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

export async function ragMetadataSearch(
  query: string,
  topK = 10,
): Promise<RagMetadataSearchResult> {
  const params = new URLSearchParams({ q: query, top_k: topK.toString() });
  const response = await fetch(`${getBaseUrl()}/api/rag/metadata/search?${params}`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

// ── RAG: full-text passage retrieval ─────────────────────────────────────────

export interface RagPassageHit {
  arxiv_id?: string;
  book_id?: number;
  title: string;
  published?: string;
  chunk_idx?: number;
  format?: string;
  snippet: string;
  rank?: number;
  score?: number;
}

export interface RagRetrieveResult {
  query: string;
  hits: RagPassageHit[];
  filters?: { book_ids?: string | null; formats?: string | null };
  engine?: string;
  error?: string;
  message?: string;
}

export async function ragRetrieve(
  query: string,
  topK = 10,
  options?: { bookIds?: string; formats?: string },
): Promise<RagRetrieveResult> {
  const params = new URLSearchParams({ q: query, top_k: topK.toString() });
  if (options?.bookIds?.trim()) params.set('book_ids', options.bookIds.trim());
  if (options?.formats?.trim()) params.set('formats', options.formats.trim());
  const response = await fetch(`${getBaseUrl()}/api/rag/retrieve?${params}`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

// ── RAG: content index build ──────────────────────────────────────────────────

export async function ragContentBuild(forceRebuild = false): Promise<RagMetadataBuildResult> {
  const response = await fetch(
    `${getBaseUrl()}/api/rag/content/build?force_rebuild=${forceRebuild ? 'true' : 'false'}`,
    { method: 'POST' },
  );
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

// ── RAG: synopsis ─────────────────────────────────────────────────────────────

export interface RagSynopsisResult {
  book_id: number;
  title?: string;
  synopsis: string;
  spoilers: boolean;
  error?: string;
}

export async function ragSynopsis(bookId: number, spoilers = false): Promise<RagSynopsisResult> {
  const response = await fetch(`${getBaseUrl()}/api/rag/synopsis/${bookId}?spoilers=${spoilers}`, {
    method: 'POST',
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

// ── RAG: book deep research ───────────────────────────────────────────────────

export interface RagResearchResult {
  success: boolean;
  book_id: number;
  title?: string;
  authors?: string[];
  report: string;
  sources_fetched: string[];
  sources_failed: string[];
  local_data?: {
    rating?: number;
    series?: string;
    personal_notes?: boolean;
    rag_passages?: number;
  };
  error?: string;
}

export async function ragResearchBook(
  bookId: number,
  includeSpoilers = false,
): Promise<RagResearchResult> {
  const response = await fetch(
    `${getBaseUrl()}/api/rag/research/${bookId}?include_spoilers=${includeSpoilers}`,
    { method: 'POST' },
  );
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

// ── Series: analysis ──────────────────────────────────────────────────────────

export interface SeriesAnalysisBook {
  index?: number;
  series_index?: number;
  title: string;
  book_id?: number;
  owned: boolean;
  read?: boolean;
}

export interface SeriesAnalysisResult {
  series: string;
  books: SeriesAnalysisBook[];
  missing?: string[];
  total_volumes?: number;
  owned_count?: number;
  error?: string;
  message?: string;
}

export async function getSeriesAnalysis(seriesName: string): Promise<SeriesAnalysisResult> {
  const params = new URLSearchParams({ series_name: seriesName });
  const response = await fetch(`${getBaseUrl()}/api/series/analysis?${params}`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        response.statusText,
    );
  }
  return response.json();
}

export interface Skill {
  id: string;
  name: string;
  prompt: string;
  /** MCP resource URI when bundled as skill:// (FastMCP 3.1 SkillsDirectoryProvider). */
  resource?: string;
}

export async function listSkills(): Promise<{ skills: Skill[] }> {
  const response = await fetch(`${getBaseUrl()}/api/skills/`);
  if (!response.ok) throw new Error('Failed to fetch skills');
  return response.json();
}

// ── Fleet discovery ──────────────────────────────────────────────────────────

export interface FleetApp {
  label: string;
  port: number;
  url: string;
  description: string;
  up: boolean;
}

export interface FleetStatus {
  webapps: FleetApp[];
  containers: FleetApp[];
  total: number;
  total_up: number;
}

export async function fetchFleetStatus(): Promise<FleetStatus> {
  const response = await fetch(`${getBaseUrl()}/api/fleet/webapps`);
  if (!response.ok) throw new Error('Failed to fetch fleet status');
  return response.json();
}

// ── Content Server Reader Integration ────────────────────────────────────────

export function getContentServerUrl(): string {
  return process.env.NEXT_PUBLIC_CALIBRE_CONTENT_SERVER_URL || 'http://goliath:8099';
}

export function getBookReaderUrl(bookId: number): string {
  const base = getContentServerUrl().replace(/\/+$/, '');
  return `${base}/#book_id=${bookId}&panel=book_details`;
}

// ── Library Analysis & Health ────────────────────────────────────────────────

export interface LibraryHealthIssue {
  type?: string;
  description?: string;
  category?: string;
  severity?: 'low' | 'medium' | 'high';
  book_ids?: number[];
  count?: number;
}

export interface LibraryHealthResult {
  health_score: number;
  database_integrity: boolean;
  issues_found: Array<string | LibraryHealthIssue>;
  recommendations: string[];
  total_books_analyzed?: number;
}

export async function getLibraryHealth(): Promise<LibraryHealthResult> {
  const response = await fetch(`${getBaseUrl()}/api/analysis/health`);
  if (!response.ok) throw new Error('Failed to fetch library health analysis');
  return response.json();
}

// ── Duplicate Books ──────────────────────────────────────────────────────────

export interface DuplicateGroup {
  title?: string;
  key?: string;
  confidence?: number;
  books: Book[];
  reason?: string;
}

export interface DuplicateBooksResult {
  duplicate_groups: DuplicateGroup[];
  total_duplicates: number;
  confidence_scores?: Record<string, number>;
}

export async function getDuplicateBooks(): Promise<DuplicateBooksResult> {
  const response = await fetch(`${getBaseUrl()}/api/analysis/duplicates`);
  if (!response.ok) throw new Error('Failed to fetch duplicate books');
  return response.json();
}

// ── Reading Analytics & Priorities ───────────────────────────────────────────

export interface PrioritizedBook {
  id: number;
  title: string;
  authors?: string[] | { name?: string }[];
  rating?: number;
  series?: string | { name?: string };
  series_index?: number;
  priority_score?: number;
  reason?: string;
  tags?: string[] | { name?: string }[];
  cover_url?: string;
}

export interface UnreadPriorityResult {
  prioritized_books: PrioritizedBook[];
  priority_reasons: Record<string, string>;
  total_unread: number;
}

export async function getUnreadPriority(): Promise<UnreadPriorityResult> {
  const response = await fetch(`${getBaseUrl()}/api/analysis/unread-priority`);
  if (!response.ok) throw new Error('Failed to fetch unread priority list');
  return response.json();
}

export interface ReadingStatisticsResult {
  total_books_read: number;
  average_rating: number;
  favorite_genres: Array<string | { name: string; count: number }>;
  reading_patterns: Record<string, unknown>;
  estimated_total_hours?: number;
  average_days_per_book?: number;
}

export async function getReadingStatistics(): Promise<ReadingStatisticsResult> {
  const response = await fetch(`${getBaseUrl()}/api/analysis/reading-stats`);
  if (!response.ok) throw new Error('Failed to fetch reading statistics');
  return response.json();
}

// ── Smart Collections ────────────────────────────────────────────────────────

export interface SmartCollection {
  id: string;
  name: string;
  description?: string;
  rule_count?: number;
  book_count?: number;
  criteria?: Record<string, unknown>;
  created_at?: string;
}

export interface SmartCollectionsResult {
  success: boolean;
  collections: SmartCollection[];
}

export async function getSmartCollections(): Promise<SmartCollectionsResult> {
  const response = await fetch(`${getBaseUrl()}/api/collections/`);
  if (!response.ok) throw new Error('Failed to fetch smart collections');
  return response.json();
}

export async function createSmartCollection(data: {
  name: string;
  description?: string;
  criteria: Record<string, unknown>;
}): Promise<{ success: boolean; collection?: SmartCollection }> {
  const response = await fetch(`${getBaseUrl()}/api/collections/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create smart collection');
  return response.json();
}

// ── Search: advanced + smart (previously unsurfaced) ─────────────────────────

export interface AdvancedSearchParams {
  query?: string;
  text?: string;
  title?: string;
  author?: string;
  tag?: string;
  series?: string;
  publisher?: string;
  rating?: number;
  min_rating?: number;
  max_rating?: number;
  unrated?: boolean;
  pubdate_start?: string;
  pubdate_end?: string;
  added_after?: string;
  added_before?: string;
  formats?: string[];
  comment?: string;
  limit?: number;
  offset?: number;
}

async function postJson<T>(url: string, body: unknown, errMsg: string): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ??
        (err as { error?: string }).error ??
        `${errMsg} (${response.status})`,
    );
  }
  return response.json();
}

export async function advancedSearch(params: AdvancedSearchParams): Promise<BookListResponse> {
  return postJson(`${getBaseUrl()}/api/search/advanced`, params, 'Advanced search failed');
}

export type SmartSearchMode = 'auto' | 'keyword' | 'advanced' | 'semantic' | 'fulltext';

export async function smartSearch(
  params: AdvancedSearchParams & { mode?: SmartSearchMode },
): Promise<BookListResponse & { engine?: string; message?: string }> {
  return postJson(`${getBaseUrl()}/api/search/smart`, params, 'Smart search failed');
}

// ── Authors: detail routes (previously unsurfaced) ───────────────────────────

export async function getAuthor(authorId: number): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/authors/${authorId}`);
  if (!response.ok) throw new Error('Failed to fetch author');
  return response.json();
}

export async function getAuthorBooks(
  authorId: number,
  params?: { limit?: number; offset?: number },
): Promise<BookListResponse> {
  const sp = new URLSearchParams();
  if (params?.limit) sp.set('limit', String(params.limit));
  if (params?.offset) sp.set('offset', String(params.offset));
  const q = sp.toString();
  const response = await fetch(`${getBaseUrl()}/api/authors/${authorId}/books${q ? `?${q}` : ''}`);
  if (!response.ok) throw new Error('Failed to fetch author books');
  return response.json();
}

export async function getAuthorsStats(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/authors/stats/summary`);
  if (!response.ok) throw new Error('Failed to fetch author stats');
  return response.json();
}

export async function listAuthorsByLetter(
  letter: string,
): Promise<{ items: AuthorItem[]; total: number }> {
  const response = await fetch(`${getBaseUrl()}/api/authors/by-letter/${letter}`);
  if (!response.ok) throw new Error('Failed to fetch authors by letter');
  const data = await response.json();
  return { items: data.items ?? data.authors ?? [], total: data.total ?? 0 };
}

// ── Series: stats + completion + detail (previously unsurfaced) ──────────────

export async function getSeriesStats(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/series/stats`);
  if (!response.ok) throw new Error('Failed to fetch series stats');
  return response.json();
}

export async function getSeriesCompletion(params?: {
  min_books?: number;
  incomplete_only?: boolean;
}): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams();
  if (params?.min_books) sp.set('min_books', String(params.min_books));
  if (params?.incomplete_only === false) sp.set('incomplete_only', 'false');
  const q = sp.toString();
  const response = await fetch(`${getBaseUrl()}/api/series/completion${q ? `?${q}` : ''}`);
  if (!response.ok) throw new Error('Failed to fetch series completion');
  return response.json();
}

export async function getSeries(seriesId: number): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/series/${seriesId}`);
  if (!response.ok) throw new Error('Failed to fetch series');
  return response.json();
}

// ── Analysis extras (previously unsurfaced) ──────────────────────────────────

export async function getTagStatistics(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/analysis/tag-statistics`);
  if (!response.ok) throw new Error('Failed to fetch tag statistics');
  return response.json();
}

export async function getLibrarySeriesAnalysis(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/analysis/series`);
  if (!response.ok) throw new Error('Failed to fetch series analysis');
  return response.json();
}

// ── Books: write ops + details + file path (previously unsurfaced) ──────────

export async function getBookDetails(bookId: number): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/books/${bookId}/details`);
  if (!response.ok) throw new Error('Failed to fetch book details');
  return response.json();
}

export async function getBookFilePath(
  bookId: number,
  formatPreference = 'EPUB',
): Promise<Record<string, unknown>> {
  const response = await fetch(
    `${getBaseUrl()}/api/books/${bookId}/file?format_preference=${formatPreference}`,
  );
  if (!response.ok) throw new Error('Failed to fetch book file path');
  return response.json();
}

export async function addBook(data: {
  file_path?: string;
  metadata?: Record<string, unknown>;
  tags?: string[];
  fetch_metadata?: boolean;
  convert_to?: string;
  library_path?: string;
}): Promise<Record<string, unknown>> {
  return postJson(`${getBaseUrl()}/api/books/`, data, 'Failed to add book');
}

export async function updateBook(
  bookId: number,
  data: {
    metadata?: Record<string, unknown>;
    status?: string;
    progress?: number;
    cover_path?: string;
  },
): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/books/${bookId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update book');
  return response.json();
}

export async function deleteBook(
  bookId: number,
  deleteFiles = true,
): Promise<Record<string, unknown>> {
  const response = await fetch(
    `${getBaseUrl()}/api/books/${bookId}?delete_files=${deleteFiles ? 'true' : 'false'}`,
    { method: 'DELETE' },
  );
  if (!response.ok) throw new Error('Failed to delete book');
  return response.json();
}

// ── Tags: management (previously list-only) ──────────────────────────────────

export async function createTag(name: string): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/tags/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(name),
  });
  if (!response.ok) throw new Error('Failed to create tag');
  return response.json();
}

export async function renameTag(tagId: number, newName: string): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/tags/${tagId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newName),
  });
  if (!response.ok) throw new Error('Failed to rename tag');
  return response.json();
}

export async function deleteTag(tagId: number, force = false): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/tags/${tagId}${force ? '?force=true' : ''}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete tag');
  return response.json();
}

export async function findDuplicateTags(
  similarityThreshold = 0.8,
): Promise<Record<string, unknown>> {
  const response = await fetch(
    `${getBaseUrl()}/api/tags/duplicates/find?similarity_threshold=${similarityThreshold}`,
  );
  if (!response.ok) throw new Error('Failed to find duplicate tags');
  return response.json();
}

export async function mergeTags(
  sourceTagIds: number[],
  targetTagId: number,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/tags/merge`,
    { source_tag_ids: sourceTagIds, target_tag_id: targetTagId },
    'Failed to merge tags',
  );
}

export async function getUnusedTags(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/tags/unused/list`);
  if (!response.ok) throw new Error('Failed to fetch unused tags');
  return response.json();
}

export async function deleteUnusedTags(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/tags/unused/all`, { method: 'DELETE' });
  if (!response.ok) throw new Error('Failed to delete unused tags');
  return response.json();
}

// ── Collections: full CRUD + generators (previously list/create only) ────────

export async function getSmartCollection(collectionId: string): Promise<SmartCollection> {
  const response = await fetch(`${getBaseUrl()}/api/collections/${collectionId}`);
  if (!response.ok) throw new Error('Failed to fetch collection');
  return response.json();
}

export async function querySmartCollection(
  collectionId: string,
  params?: { limit?: number; offset?: number },
): Promise<BookListResponse> {
  const sp = new URLSearchParams();
  if (params?.limit) sp.set('limit', String(params.limit));
  if (params?.offset) sp.set('offset', String(params.offset));
  const q = sp.toString();
  const response = await fetch(
    `${getBaseUrl()}/api/collections/${collectionId}/query${q ? `?${q}` : ''}`,
  );
  if (!response.ok) throw new Error('Failed to query collection');
  return response.json();
}

export async function updateSmartCollection(
  collectionId: string,
  updates: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/collections/${collectionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!response.ok) throw new Error('Failed to update collection');
  return response.json();
}

export async function deleteSmartCollection(
  collectionId: string,
): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/collections/${collectionId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete collection');
  return response.json();
}

export async function createSeriesCollection(
  name: string,
  seriesName: string,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/collections/series`,
    { name, series_name: seriesName },
    'Failed to create series collection',
  );
}

export async function createRecentlyAddedCollection(
  name?: string,
  days = 30,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/collections/recently-added`,
    { name: name ?? null, days },
    'Failed to create recently-added collection',
  );
}

export async function createUnreadCollection(name?: string): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/collections/unread`,
    { name: name ?? null },
    'Failed to create unread collection',
  );
}

export async function createAiRecommendedCollection(
  name?: string,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/collections/ai-recommended`,
    { name: name ?? null },
    'Failed to create AI collection',
  );
}

// ── Export: HTML + Pandoc (previously CSV/JSON only) ─────────────────────────

export async function exportBooks(
  format: 'csv' | 'json' | 'html' | 'pandoc',
  options?: {
    output_path?: string;
    book_ids?: number[];
    author?: string;
    tag?: string;
    limit?: number;
    include_fields?: string[];
    open_file?: boolean;
    format_type?: string;
    html_style?: string;
  },
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/export/${format}`,
    {
      output_path: options?.output_path ?? null,
      book_ids: options?.book_ids ?? null,
      author: options?.author ?? null,
      tag: options?.tag ?? null,
      limit: options?.limit ?? 1000,
      include_fields: options?.include_fields ?? null,
      open_file: options?.open_file ?? false,
      ...(format === 'pandoc' ? { format_type: options?.format_type ?? 'docx' } : {}),
      ...(format === 'html' ? { html_style: options?.html_style ?? 'gallery' } : {}),
    },
    `Export to ${format} failed`,
  );
}

// ── Viewer: session ops + random (previously open-file only) ─────────────────

export async function openRandomBook(params?: {
  author?: string;
  tag?: string;
  series?: string;
  format_preference?: string;
}): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams();
  if (params?.author) sp.set('author', params.author);
  if (params?.tag) sp.set('tag', params.tag);
  if (params?.series) sp.set('series', params.series);
  if (params?.format_preference) sp.set('format_preference', params.format_preference);
  const q = sp.toString();
  const response = await fetch(`${getBaseUrl()}/api/viewer/open-random${q ? `?${q}` : ''}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to open random book');
  return response.json();
}

export async function viewerOpen(
  bookId: number,
  filePath?: string,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/viewer/open`,
    { book_id: bookId, file_path: filePath ?? null },
    'Failed to open viewer session',
  );
}

export async function viewerPage(
  bookId: number,
  filePath: string,
  pageNumber = 0,
): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams({
    book_id: String(bookId),
    file_path: filePath,
    page_number: String(pageNumber),
  });
  const response = await fetch(`${getBaseUrl()}/api/viewer/page?${sp}`);
  if (!response.ok) throw new Error('Failed to fetch viewer page');
  return response.json();
}

export async function viewerMetadata(
  bookId: number,
  filePath: string,
): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams({ book_id: String(bookId), file_path: filePath });
  const response = await fetch(`${getBaseUrl()}/api/viewer/metadata?${sp}`);
  if (!response.ok) throw new Error('Failed to fetch viewer metadata');
  return response.json();
}

export async function viewerGetState(
  bookId: number,
  filePath: string,
): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams({ book_id: String(bookId), file_path: filePath });
  const response = await fetch(`${getBaseUrl()}/api/viewer/state?${sp}`);
  if (!response.ok) throw new Error('Failed to fetch viewer state');
  return response.json();
}

export async function viewerSaveState(state: {
  book_id: number;
  file_path: string;
  current_page?: number;
  reading_direction?: string;
  page_layout?: string;
  zoom_mode?: string;
  zoom_level?: number;
}): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/viewer/state`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state),
  });
  if (!response.ok) throw new Error('Failed to save viewer state');
  return response.json();
}

export async function viewerClose(
  bookId: number,
  filePath?: string,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/viewer/close`,
    { book_id: bookId, file_path: filePath ?? null },
    'Failed to close viewer session',
  );
}

// ── Comments (previously entirely unsurfaced) ────────────────────────────────

export async function getBookComment(bookId: number | string): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/comments/${bookId}`);
  if (!response.ok) throw new Error('Failed to fetch comment');
  return response.json();
}

async function sendCommentText(
  method: string,
  bookId: number | string,
  text: string,
  errMsg: string,
): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/comments/${bookId}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(text),
  });
  if (!response.ok) throw new Error(errMsg);
  return response.json();
}

export async function createBookComment(
  bookId: number | string,
  text: string,
): Promise<Record<string, unknown>> {
  return sendCommentText('POST', bookId, text, 'Failed to create comment');
}

export async function replaceBookComment(
  bookId: number | string,
  text: string,
): Promise<Record<string, unknown>> {
  return sendCommentText('PUT', bookId, text, 'Failed to update comment');
}

export async function appendBookComment(
  bookId: number | string,
  text: string,
): Promise<Record<string, unknown>> {
  return sendCommentText('PATCH', bookId, text, 'Failed to append comment');
}

export async function deleteBookComment(bookId: number | string): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/comments/${bookId}`, { method: 'DELETE' });
  if (!response.ok) throw new Error('Failed to delete comment');
  return response.json();
}

// ── Metadata tools (previously entirely unsurfaced) ──────────────────────────

export async function showMetadata(params?: {
  query?: string;
  author?: string;
}): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams();
  if (params?.query) sp.set('query', params.query);
  if (params?.author) sp.set('author', params.author);
  const q = sp.toString();
  const response = await fetch(`${getBaseUrl()}/api/metadata/show${q ? `?${q}` : ''}`);
  if (!response.ok) throw new Error('Failed to show metadata');
  return response.json();
}

export async function bulkUpdateMetadata(
  updates: { book_id: number; field: string; value: unknown }[],
): Promise<Record<string, unknown>> {
  return postJson(`${getBaseUrl()}/api/metadata/update`, updates, 'Metadata update failed');
}

export async function organizeTags(): Promise<Record<string, unknown>> {
  return postJson(`${getBaseUrl()}/api/metadata/organize-tags`, {}, 'Tag organization failed');
}

export async function fixMetadataIssues(): Promise<Record<string, unknown>> {
  return postJson(`${getBaseUrl()}/api/metadata/fix-issues`, {}, 'Metadata fix failed');
}

// ── Files + bulk (previously entirely unsurfaced) ────────────────────────────

export async function convertBookFile(
  conversionRequests: { book_id: number; target_format: string }[],
): Promise<Record<string, unknown>> {
  return postJson(`${getBaseUrl()}/api/files/convert`, conversionRequests, 'File convert failed');
}

export async function downloadBookFile(
  bookId: number,
  formatPreference = 'EPUB',
): Promise<Record<string, unknown>> {
  const response = await fetch(
    `${getBaseUrl()}/api/files/${bookId}/download?format_preference=${formatPreference}`,
  );
  if (!response.ok) throw new Error('Failed to download book file');
  return response.json();
}

export async function bulkFileOperation(
  operationType: 'convert' | 'validate' | 'cleanup',
  options?: { target_format?: string; book_ids?: number[] },
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/files/bulk`,
    {
      operation_type: operationType,
      target_format: options?.target_format ?? null,
      book_ids: options?.book_ids ?? null,
    },
    'Bulk file operation failed',
  );
}

export async function bulkUpdateBooksMetadata(
  bookIds: number[],
  updates: Record<string, unknown>,
  batchSize = 10,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/bulk/metadata/update`,
    { book_ids: bookIds, updates, batch_size: batchSize },
    'Bulk metadata update failed',
  );
}

export async function bulkExportBooks(
  bookIds: number[],
  exportPath: string,
  format: 'directory' | 'zip' = 'directory',
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/bulk/export`,
    { book_ids: bookIds, export_path: exportPath, format },
    'Bulk export failed',
  );
}

export async function bulkDeleteBooks(
  bookIds: number[],
  deleteFiles = true,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/bulk/delete`,
    { book_ids: bookIds, delete_files: deleteFiles },
    'Bulk delete failed',
  );
}

export async function bulkConvertBooks(
  bookIds: number[],
  targetFormat: string,
  outputPath?: string,
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/bulk/convert`,
    { book_ids: bookIds, target_format: targetFormat, output_path: outputPath ?? null },
    'Bulk convert failed',
  );
}

// ── Specialized curation (previously entirely unsurfaced) ────────────────────

export async function getJapaneseOrganizer(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/specialized/japanese-organizer`);
  if (!response.ok) throw new Error('Japanese organizer failed');
  return response.json();
}

export async function getItCurator(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/specialized/it-curator`);
  if (!response.ok) throw new Error('IT curation failed');
  return response.json();
}

export async function getReadingRecommendations(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/specialized/reading-recommendations`);
  if (!response.ok) throw new Error('Reading recommendations failed');
  return response.json();
}

// ── RAG extras (previously unsurfaced) ───────────────────────────────────────

export async function ragCombinedSearch(
  query: string,
  topK = 10,
  mode: 'auto' | 'metadata' | 'content' = 'auto',
): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams({ q: query, top_k: String(topK), mode });
  const response = await fetch(`${getBaseUrl()}/api/rag/search?${sp}`, { method: 'POST' });
  if (!response.ok) throw new Error('Combined RAG search failed');
  return response.json();
}

export async function ragCriticalReception(bookId: number): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/rag/critical-reception/${bookId}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Critical reception failed');
  return response.json();
}

export async function ragDeepResearch(topic: string, limit = 5): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams({ topic, limit: String(limit) });
  const response = await fetch(`${getBaseUrl()}/api/rag/deep-research?${sp}`, { method: 'POST' });
  if (!response.ok) throw new Error('Deep research failed');
  return response.json();
}

export async function ragMetadataExport(outputPath?: string): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams();
  if (outputPath) sp.set('output_path', outputPath);
  const q = sp.toString();
  const response = await fetch(`${getBaseUrl()}/api/rag/metadata/export${q ? `?${q}` : ''}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('RAG metadata export failed');
  return response.json();
}

// ── Libraries: cross-search / discover / connection (new backend routes) ─────

export async function crossLibrarySearch(
  query: string,
  libraries?: string[],
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/libraries/search`,
    { query, libraries: libraries ?? null },
    'Cross-library search failed',
  );
}

export async function discoverLibraries(options?: {
  wizfile_allowed?: boolean;
  calibre_cli_allowed?: boolean;
  common_paths_allowed?: boolean;
}): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/libraries/discover`,
    {
      wizfile_allowed: options?.wizfile_allowed ?? false,
      calibre_cli_allowed: options?.calibre_cli_allowed ?? false,
      common_paths_allowed: options?.common_paths_allowed ?? true,
    },
    'Library discovery failed',
  );
}

export async function testLibraryConnection(): Promise<Record<string, unknown>> {
  return postJson(`${getBaseUrl()}/api/libraries/test-connection`, {}, 'Connection test failed');
}

// ── System extras (previously unsurfaced) ────────────────────────────────────

export async function listTools(category?: string): Promise<Record<string, unknown>> {
  const sp = new URLSearchParams();
  if (category) sp.set('category', category);
  const q = sp.toString();
  const response = await fetch(`${getBaseUrl()}/api/system/tools${q ? `?${q}` : ''}`);
  if (!response.ok) throw new Error('Failed to list tools');
  return response.json();
}

export async function getToolHelp(
  toolName: string,
  level: 'basic' | 'intermediate' | 'advanced' | 'expert' = 'basic',
): Promise<Record<string, unknown>> {
  const response = await fetch(
    `${getBaseUrl()}/api/system/tools/${toolName}/help?tool_help_level=${level}`,
  );
  if (!response.ok) throw new Error('Failed to fetch tool help');
  return response.json();
}

export async function getApiDocsInfo(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/system/api-docs-info`);
  if (!response.ok) throw new Error('Failed to fetch API docs info');
  return response.json();
}

export async function getHealthCheck(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/system/health-check`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

export async function getContentServerStatus(): Promise<Record<string, unknown>> {
  const response = await fetch(`${getBaseUrl()}/api/system/content-server`);
  if (!response.ok) throw new Error('Content server check failed');
  return response.json();
}

// ── LLM chat (previously unsurfaced: chat page never called /llm/*) ──────────

export async function listLlmModels(params?: {
  provider?: string;
  base_url?: string;
}): Promise<{ models: string[]; provider?: string; error?: string }> {
  const sp = new URLSearchParams();
  if (params?.provider) sp.set('provider', params.provider);
  if (params?.base_url) sp.set('base_url', params.base_url);
  const q = sp.toString();
  const response = await fetch(`${getBaseUrl()}/api/llm/models${q ? `?${q}` : ''}`);
  if (!response.ok) throw new Error('Failed to list LLM models');
  return response.json();
}

export async function llmChat(
  messages: { role: string; content: string }[],
  model = 'llama3.2',
  options?: { provider?: string; base_url?: string },
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/llm/chat`,
    {
      messages,
      model,
      stream: false,
      provider: options?.provider ?? null,
      base_url: options?.base_url ?? null,
    },
    'LLM chat failed',
  );
}

export async function llmAgenticChat(
  messages: { role: string; content: string }[],
  model = 'llama3.2',
  options?: { provider?: string; base_url?: string },
): Promise<Record<string, unknown>> {
  return postJson(
    `${getBaseUrl()}/api/llm/agentic`,
    {
      messages,
      model,
      provider: options?.provider ?? null,
      base_url: options?.base_url ?? null,
    },
    'Agentic chat failed',
  );
}
