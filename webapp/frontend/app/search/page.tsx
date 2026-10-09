'use client';

import {
  type AdvancedSearchParams,
  type Book,
  type SmartSearchMode,
  advancedSearch,
  searchBooks,
  smartSearch,
} from '@/common/api';
import { BookGrid } from '@/components/books/book-grid';
import { SearchBar } from '@/components/search/search-bar';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';

type SearchTab = 'keyword' | 'advanced' | 'smart';

const SMART_MODES: { value: SmartSearchMode; label: string }[] = [
  { value: 'auto', label: 'Auto' },
  { value: 'keyword', label: 'Keyword' },
  { value: 'advanced', label: 'Advanced' },
  { value: 'semantic', label: 'Semantic' },
  { value: 'fulltext', label: 'Full-text' },
];

function buildSearchPageUrl(
  base: string,
  page: number,
  p: Record<string, string | undefined>,
): string {
  const params = new URLSearchParams();
  if (page > 1) params.set('page', page.toString());
  for (const [k, v] of Object.entries(p)) {
    if (v) params.set(k, v);
  }
  const q = params.toString();
  return q ? `${base}?${q}` : base;
}

function usePagination(total: number, limit: number, page: number) {
  const totalPages = Math.ceil(total / limit);
  return { totalPages, hasPrev: page > 1, hasNext: page < totalPages };
}

function Pagination({
  base,
  page,
  total,
  limit,
  params,
}: {
  base: string;
  page: number;
  total: number;
  limit: number;
  params: Record<string, string | undefined>;
}) {
  const { totalPages, hasPrev, hasNext } = usePagination(total, limit, page);
  const offset = (page - 1) * limit;
  if (total <= limit) return null;
  return (
    <nav className="mt-6 flex flex-wrap items-center justify-center gap-2" aria-label="Pagination">
      <p className="w-full text-center text-sm text-slate-400 mb-2">
        Showing {offset + 1}-{Math.min(offset + limit, total)} of {total} books
      </p>
      <div className="flex items-center gap-2">
        {hasPrev ? (
          <Link
            href={buildSearchPageUrl(base, page - 1, params)}
            className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
          >
            Previous
          </Link>
        ) : (
          <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Previous</span>
        )}
        <span className="px-3 py-2 text-sm text-slate-400">
          Page {page} of {totalPages}
        </span>
        {hasNext ? (
          <Link
            href={buildSearchPageUrl(base, page + 1, params)}
            className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
          >
            Next
          </Link>
        ) : (
          <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Next</span>
        )}
      </div>
    </nav>
  );
}

// ── Keyword tab (original behavior, preserved) ───────────────────────────────

function KeywordTab() {
  const searchParams = useSearchParams();
  const query = searchParams?.get('query') ?? undefined;
  const author = searchParams?.get('author') ?? undefined;
  const tag = searchParams?.get('tag') ?? undefined;
  const minRating = searchParams?.get('min_rating') ?? undefined;
  const fulltextParam = searchParams?.get('fulltext') ?? undefined;
  const page = Math.max(1, Number.parseInt(searchParams?.get('page') ?? '1', 10));
  const limit = 50;
  const offset = (page - 1) * limit;

  const fulltextMode = fulltextParam === '1' && query?.trim();
  const hasSearchParams = Boolean(fulltextMode || query || author || tag || minRating);

  const [data, setData] = useState<{ items?: Book[]; total?: number }>({ items: [], total: 0 });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!hasSearchParams) {
      setData({ items: [], total: 0 });
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    searchBooks({
      query,
      author: fulltextMode ? undefined : author,
      tag: fulltextMode ? undefined : tag,
      min_rating: fulltextMode ? undefined : minRating ? Number.parseInt(minRating, 10) : undefined,
      fulltext: Boolean(fulltextMode),
      limit,
      offset,
    })
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch(() => {
        if (!cancelled) setData({ items: [], total: 0 });
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [query, author, tag, minRating, fulltextMode, hasSearchParams, limit, offset]);

  const total = data.total ?? 0;
  const params = {
    query,
    author,
    tag,
    min_rating: minRating,
    fulltext: fulltextParam === '1' ? '1' : undefined,
  };

  return (
    <div>
      <SearchBar
        initialQuery={query}
        initialAuthor={author}
        initialTag={tag}
        initialMinRating={minRating}
        initialFulltext={fulltextParam === '1'}
      />
      {hasSearchParams && loading && (
        <div className="mt-6 text-center text-slate-400">
          <p>Searching…</p>
        </div>
      )}
      {hasSearchParams && !loading && (
        <>
          {data.items && data.items.length > 0 ? (
            <>
              <div className="mt-6">
                <BookGrid books={data.items} />
              </div>
              <Pagination base="/search" page={page} total={total} limit={limit} params={params} />
            </>
          ) : (
            <div className="mt-6 text-center text-gray-500">
              <p>No books found matching your search criteria.</p>
            </div>
          )}
        </>
      )}
      {!hasSearchParams && (
        <div className="mt-6 text-center text-slate-400">
          <p>Enter search criteria above to find books.</p>
        </div>
      )}
    </div>
  );
}

// ── Advanced tab ─────────────────────────────────────────────────────────────

const inputCls =
  'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber';
const labelCls = 'block text-xs font-medium text-slate-400 mb-1';

function AdvancedTab() {
  const [form, setForm] = useState<AdvancedSearchParams>({});
  const [results, setResults] = useState<Book[]>([]);
  const [total, setTotal] = useState(0);
  const [ran, setRan] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof AdvancedSearchParams, val: string | number | undefined) => {
    setForm((f) => {
      const next = { ...f };
      if (val === undefined || val === '') {
        delete next[key];
      } else {
        (next as Record<string, unknown>)[key] = val;
      }
      return next;
    });
  };

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await advancedSearch({ ...form, limit: 50, offset: 0 });
      setResults(res.items ?? []);
      setTotal(res.total ?? 0);
      setRan(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Advanced search failed');
    } finally {
      setLoading(false);
    }
  };

  const text = (key: 'query' | 'title' | 'author' | 'tag' | 'series' | 'publisher' | 'comment') => (
    <input
      type="search"
      value={String(form[key] ?? '')}
      onChange={(e) => set(key, e.target.value || undefined)}
      className={inputCls}
    />
  );

  return (
    <div>
      <div className="bg-slate-800 border border-slate-600 p-4 rounded-lg mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div>
            <label className={labelCls}>Free text</label>
            {text('query')}
          </div>
          <div>
            <label className={labelCls}>Title</label>
            {text('title')}
          </div>
          <div>
            <label className={labelCls}>Author</label>
            {text('author')}
          </div>
          <div>
            <label className={labelCls}>Tag</label>
            {text('tag')}
          </div>
          <div>
            <label className={labelCls}>Series</label>
            {text('series')}
          </div>
          <div>
            <label className={labelCls}>Publisher</label>
            {text('publisher')}
          </div>
          <div>
            <label className={labelCls}>Comment contains</label>
            {text('comment')}
          </div>
          <div>
            <label className={labelCls}>Min rating</label>
            <select
              value={form.min_rating ?? ''}
              onChange={(e) =>
                set('min_rating', e.target.value ? Number(e.target.value) : undefined)
              }
              className={inputCls}
            >
              <option value="">Any</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  {n}+ stars
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Max rating</label>
            <select
              value={form.max_rating ?? ''}
              onChange={(e) =>
                set('max_rating', e.target.value ? Number(e.target.value) : undefined)
              }
              className={inputCls}
            >
              <option value="">Any</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  up to {n}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Published after</label>
            <input
              type="date"
              value={form.pubdate_start ?? ''}
              onChange={(e) => set('pubdate_start', e.target.value || undefined)}
              className={`${inputCls} [color-scheme:dark]`}
            />
          </div>
          <div>
            <label className={labelCls}>Published before</label>
            <input
              type="date"
              value={form.pubdate_end ?? ''}
              onChange={(e) => set('pubdate_end', e.target.value || undefined)}
              className={`${inputCls} [color-scheme:dark]`}
            />
          </div>
          <div>
            <label className={labelCls}>Added after</label>
            <input
              type="date"
              value={form.added_after ?? ''}
              onChange={(e) => set('added_after', e.target.value || undefined)}
              className={`${inputCls} [color-scheme:dark]`}
            />
          </div>
          <div>
            <label className={labelCls}>Added before</label>
            <input
              type="date"
              value={form.added_before ?? ''}
              onChange={(e) => set('added_before', e.target.value || undefined)}
              className={`${inputCls} [color-scheme:dark]`}
            />
          </div>
          <div>
            <label className={labelCls}>Formats (comma separated)</label>
            <input
              type="text"
              value={(form.formats ?? []).join(', ')}
              onChange={(e) => {
                const parts = e.target.value
                  .split(',')
                  .map((s) => s.trim().toUpperCase())
                  .filter(Boolean);
                setForm((f) => ({ ...f, formats: parts.length > 0 ? parts : undefined }));
              }}
              placeholder="EPUB, PDF"
              className={inputCls}
            />
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={run}
            disabled={loading}
            className="px-4 py-2 bg-amber text-slate-900 rounded-md hover:bg-amber/90 font-medium disabled:opacity-50"
          >
            {loading ? 'Searching…' : 'Advanced search'}
          </button>
          <button
            type="button"
            onClick={() => {
              setForm({});
              setResults([]);
              setTotal(0);
              setRan(false);
            }}
            className="px-4 py-2 bg-slate-700 text-slate-200 rounded-md hover:bg-slate-600"
          >
            Clear
          </button>
        </div>
      </div>
      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}
      {ran && !loading && (
        <>
          <p className="text-sm text-slate-400 mb-4">
            {total} result{total === 1 ? '' : 's'} (all filters AND-combined)
          </p>
          {results.length > 0 ? (
            <BookGrid books={results} />
          ) : (
            <p className="text-center text-slate-500">No books match all filters.</p>
          )}
        </>
      )}
    </div>
  );
}

// ── Smart tab ────────────────────────────────────────────────────────────────

function SmartTab() {
  const [query, setQuery] = useState('');
  const [author, setAuthor] = useState('');
  const [tag, setTag] = useState('');
  const [mode, setMode] = useState<SmartSearchMode>('auto');
  const [results, setResults] = useState<Book[]>([]);
  const [engine, setEngine] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [ran, setRan] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await smartSearch({
        query: query.trim() || undefined,
        author: author.trim() || undefined,
        tag: tag.trim() || undefined,
        mode,
        limit: 50,
        offset: 0,
      });
      setResults(res.items ?? []);
      setEngine(res.engine ?? null);
      setMessage(res.message ?? null);
      setRan(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Smart search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="bg-slate-800 border border-slate-600 p-4 rounded-lg mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="md:col-span-2">
            <label className={labelCls}>Query (natural language OK)</label>
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && run()}
              placeholder="e.g. melancholy space operas like Banks…"
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Author filter (optional)</label>
            <input
              type="search"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Tag filter (optional)</label>
            <input
              type="search"
              value={tag}
              onChange={(e) => setTag(e.target.value)}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Engine</label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as SmartSearchMode)}
              className={inputCls}
            >
              {SMART_MODES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Auto picks keyword, advanced, semantic, or full-text based on your query. Natural-language
          queries route to the semantic index when it is built.
        </p>
        <div className="mt-3">
          <button
            type="button"
            onClick={run}
            disabled={loading || (!query.trim() && !author.trim() && !tag.trim())}
            className="px-4 py-2 bg-amber text-slate-900 rounded-md hover:bg-amber/90 font-medium disabled:opacity-50"
          >
            {loading ? 'Searching…' : 'Smart search'}
          </button>
        </div>
      </div>
      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}
      {ran && !loading && (
        <>
          {(engine || message) && (
            <p className="text-sm text-slate-400 mb-4">
              {engine && (
                <span className="px-2 py-0.5 rounded bg-slate-700 text-amber text-xs font-mono mr-2">
                  {engine}
                </span>
              )}
              {message}
            </p>
          )}
          {results.length > 0 ? (
            <BookGrid books={results} />
          ) : (
            <p className="text-center text-slate-500">No results.</p>
          )}
        </>
      )}
    </div>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────

function SearchPageInner() {
  const [tab, setTab] = useState<SearchTab>('keyword');
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Search Books</h1>
      <div className="flex gap-1 border border-slate-600 rounded-lg p-1 bg-slate-800/50 w-fit mb-6">
        {(['keyword', 'advanced', 'smart'] as SearchTab[]).map((t) => (
          <button
            key={t}
            type="button"
            data-testid={`search-tab-${t}`}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors capitalize ${
              tab === t ? 'bg-amber/20 text-amber' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      {tab === 'keyword' && <KeywordTab />}
      {tab === 'advanced' && <AdvancedTab />}
      {tab === 'smart' && <SmartTab />}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <SearchPageInner />
    </Suspense>
  );
}
