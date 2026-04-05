/** API client for Calibre webapp. All calls go through Next.js API proxies (same-origin). */

/** Get stored Anna's Archive mirror URL(s) from backend. */
export async function getAnnasMirrors(): Promise<string[]> {
  const settings = await getSettings();
  return settings.annas_mirrors || [];
}

/** Store Anna's Archive mirror URL(s) in backend. */
export async function setAnnasMirrors(mirrors: string | string[]): Promise<void> {
  const annas_mirrors = typeof mirrors === 'string' 
    ? mirrors.split(',').map(m => m.trim()).filter(Boolean)
    : mirrors;
  await updateSettings({ annas_mirrors });
}

/** Base URL for fetch. Server needs absolute URL; client uses relative. */
function getBaseUrl(): string {
  if (typeof window !== 'undefined') return '';
  return process.env.NEXT_PUBLIC_APP_URL ?? 'http://127.0.0.1:10721';
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

export interface BookListResponse {
  items: Book[];
  total: number;
  page?: number;
  per_page?: number;
}

export async function getBooks(params?: {
  limit?: number;
  offset?: number;
  author?: string;
  tag?: string;
  publisher?: string;
  text?: string;
}): Promise<BookListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.author) searchParams.set('author', params.author);
  if (params?.tag) searchParams.set('tag', params.tag);
  if (params?.publisher) searchParams.set('publisher', params.publisher);
  if (params?.text) searchParams.set('text', params.text);

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
  return `/api/books/${bookId}/cover`;
}

export async function getBook(id: number): Promise<Book> {
  const response = await fetch(`${getBaseUrl()}/api/books/${id}`);
  if (!response.ok) throw new Error('Failed to fetch book');
  return response.json();
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
      detail = (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? (err as { message?: string }).message ?? '';
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
  const response = await fetch(`${getBaseUrl()}/api/libraries/list`);
  if (!response.ok) {
    let detail = '';
    try {
      const err = await response.json();
      detail = (err as { hint?: string }).hint ?? (err as { detail?: string }).detail ?? (err as { error?: string }).error ?? '';
    } catch {
      detail = 'Run webapp\\start.ps1 from repo root.';
    }
    throw new Error(detail || `Failed to fetch libraries (${response.status})`);
  }
  const data = await response.json();
  return { libraries: data.libraries, current_library: data.current_library, total_libraries: data.total_libraries };
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

export async function switchLibrary(libraryName: string): Promise<{ success: boolean; library_name: string; library_path: string; message: string }> {
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
  const response = await fetch(`${getBaseUrl()}/api/help?${params}`);
  if (!response.ok) throw new Error('Failed to fetch help');
  return response.json();
}

export async function getSystemStatus(level = 'diagnostic'): Promise<Record<string, unknown>> {
  const base = getBaseUrl();
  const response = await fetch(`${base}/api/status?status_level=${level}`);
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

export async function listAuthors(params?: { query?: string; limit?: number; offset?: number }): Promise<{ items: AuthorItem[]; total: number }> {
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
}): Promise<{ items: PublisherItem[]; total: number; error?: string; message?: string }> {
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
}): Promise<{ items: SeriesItem[]; total: number; error?: string; message?: string }> {
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

export async function getSeriesBooks(seriesId: number, params?: { limit?: number; offset?: number }): Promise<{ items: Book[]; series?: { name?: string }; total?: number }> {
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
    throw new Error((err as { detail?: string }).detail ?? (err as { error?: string }).error ?? response.statusText);
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

export async function downloadAnnas(md5: string, options?: { format?: string, title?: string, authors?: string[], tags?: string[], series?: string, library_path?: string }): Promise<AnnasDownloadResponse> {
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
      library_path: options?.library_path
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? (err as { error?: string }).error ?? response.statusText);
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

export async function searchArxiv(query: string, maxResults?: number): Promise<ArxivSearchResponse> {
  const response = await fetch(`${getBaseUrl()}/api/arxiv/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, max_results: maxResults }),
  });
  if (!response.ok) throw new Error('arXiv search failed');
  return response.json();
}

export async function importArxiv(arxivId: string, options?: { title?: string, authors?: string[], tags?: string[], series?: string, library_path?: string }): Promise<{ success: boolean; title?: string }> {
  const response = await fetch(`${getBaseUrl()}/api/arxiv/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      arxiv_id: arxivId,
      title: options?.title,
      authors: options?.authors,
      tags: options?.tags,
      series: options?.series,
      library_path: options?.library_path
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? (err as { error?: string }).error ?? response.statusText);
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

export async function importGutenberg(bookId: number, options?: { format?: string, title?: string, authors?: string[], tags?: string[], series?: string, library_path?: string }): Promise<{ success: boolean; title?: string }> {
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
      library_path: options?.library_path
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? (err as { error?: string }).error ?? response.statusText);
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

export async function updateSettings(settings: Partial<AppSettings>): Promise<{ success: boolean; message: string }> {
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
}): Promise<{ items: TagItem[]; total: number; error?: string; message?: string }> {
  const searchParams = new URLSearchParams();
  if (params?.search) searchParams.set('search', params.search);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
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
    { method: 'POST' }
  );
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? (err as { error?: string }).error ?? response.statusText);
  }
  return response.json();
}

export async function ragMetadataSearch(query: string, topK = 10): Promise<RagMetadataSearchResult> {
  const params = new URLSearchParams({ q: query, top_k: topK.toString() });
  const response = await fetch(`${getBaseUrl()}/api/rag/metadata/search?${params}`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? (err as { error?: string }).error ?? response.statusText);
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
