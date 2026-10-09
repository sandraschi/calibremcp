'use client';

import {
  type BookListResponse,
  type BookQueryParams,
  getBooks,
  openRandomBook,
} from '@/common/api';
import { BookGrid } from '@/components/books/book-grid';
import { type BooksFilterValue, BooksToolbar } from '@/components/books/books-toolbar';
import { ErrorBanner } from '@/components/ui/error-banner';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useMemo, useState } from 'react';

const BACKEND_HINT = 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721).';

function parseFilters(searchParams: URLSearchParams): BooksFilterValue {
  const pick = (key: string): string | undefined => {
    const v = searchParams.get(key)?.trim();
    return v ? v : undefined;
  };
  const pickInt = (key: string): number | undefined => {
    const raw = searchParams.get(key);
    if (!raw) return undefined;
    const n = Number.parseInt(raw, 10);
    return Number.isFinite(n) ? n : undefined;
  };
  const sortBy = searchParams.get('sort_by');
  const sortOrder = searchParams.get('sort_order');
  const hasPublisher = searchParams.get('has_publisher');
  return {
    text: pick('text'),
    title: pick('title'),
    author: pick('author'),
    tag: pick('tag'),
    series: pick('series'),
    publisher: pick('publisher'),
    rating: pickInt('rating'),
    min_rating: pickInt('min_rating'),
    max_rating: pickInt('max_rating'),
    unrated: searchParams.get('unrated') === '1' ? true : undefined,
    formats: pick('formats'),
    pubdate_start: pick('pubdate_start'),
    pubdate_end: pick('pubdate_end'),
    added_after: pick('added_after'),
    added_before: pick('added_before'),
    has_publisher:
      hasPublisher === null || hasPublisher === ''
        ? undefined
        : hasPublisher === '1' || hasPublisher.toLowerCase() === 'true',
    sort_by: (['title', 'author', 'series', 'rating', 'timestamp', 'pubdate'] as const).includes(
      sortBy as never,
    )
      ? (sortBy as BooksFilterValue['sort_by'])
      : undefined,
    sort_order: sortOrder === 'desc' ? 'desc' : sortOrder === 'asc' ? 'asc' : undefined,
  };
}

function buildPageUrl(base: string, page: number, filters: BooksFilterValue): string {
  const params = new URLSearchParams();
  if (page > 1) params.set('page', page.toString());
  const entries: [string, string | number | boolean | undefined][] = [
    ['text', filters.text],
    ['title', filters.title],
    ['author', filters.author],
    ['tag', filters.tag],
    ['series', filters.series],
    ['publisher', filters.publisher],
    ['rating', filters.rating],
    ['min_rating', filters.min_rating],
    ['max_rating', filters.max_rating],
    ['formats', filters.formats],
    ['pubdate_start', filters.pubdate_start],
    ['pubdate_end', filters.pubdate_end],
    ['added_after', filters.added_after],
    ['added_before', filters.added_before],
    ['sort_by', filters.sort_by],
    ['sort_order', filters.sort_order],
  ];
  for (const [key, val] of entries) {
    if (val !== undefined && val !== '' && val !== null) params.set(key, String(val));
  }
  if (filters.unrated) params.set('unrated', '1');
  if (filters.has_publisher === true) params.set('has_publisher', '1');
  if (filters.has_publisher === false) params.set('has_publisher', '0');
  const q = params.toString();
  return q ? `${base}?${q}` : base;
}

function BooksPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const page = Math.max(1, Number.parseInt(searchParams?.get('page') ?? '1', 10));
  const limit = 50;
  const offset = (page - 1) * limit;

  const filters: BooksFilterValue = useMemo(
    () => parseFilters(new URLSearchParams(searchParams?.toString() ?? '')),
    [searchParams],
  );
  const queryKey = useMemo(() => JSON.stringify({ ...filters, page }), [filters, page]);

  const [data, setData] = useState<BookListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [surprising, setSurprising] = useState(false);
  const [surpriseError, setSurpriseError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    const params: BookQueryParams = { limit, offset, ...filters };
    getBooks(params)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((e) => {
        if (!cancelled) setError(String((e as Error).message));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // Re-run when the serialized query changes (filters or page).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryKey]);

  const handleApply = (next: BooksFilterValue) => {
    router.push(buildPageUrl('/books', 1, next));
  };

  const handleSurprise = async () => {
    setSurprising(true);
    setSurpriseError(null);
    try {
      const res = (await openRandomBook(
        filters.author || filters.tag || filters.series
          ? {
              author: filters.author,
              tag: filters.tag,
              series: filters.series,
            }
          : undefined,
      )) as { book_id?: number; id?: number; book?: { id?: number } };
      const id = res.book_id ?? res.id ?? res.book?.id;
      if (id) {
        router.push(`/book/${id}`);
      } else {
        setSurpriseError('No random pick returned — try widening the filters.');
      }
    } catch (e) {
      setSurpriseError(e instanceof Error ? e.message : 'Surprise-me failed');
    } finally {
      setSurprising(false);
    }
  };

  const handleReset = () => {
    router.push('/books');
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <h1 className="text-3xl font-bold text-slate-100">Browse</h1>
        </div>
        <BooksToolbar value={filters} onApply={handleApply} onReset={handleReset} />
        <p className="text-slate-400">Loading books…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Browse</h1>
        <BooksToolbar value={filters} onApply={handleApply} onReset={handleReset} />
        <ErrorBanner
          title="Could not load books"
          message={error ?? 'Unknown error'}
          hint={BACKEND_HINT}
        />
      </div>
    );
  }

  const items = Array.isArray(data?.items) ? data.items : [];
  const total = typeof data?.total === 'number' ? data.total : 0;
  const totalPages = Math.ceil(total / limit);
  const base = '/books';

  const pageRange = 2;
  const pages: number[] = [];
  for (let i = Math.max(1, page - pageRange); i <= Math.min(totalPages, page + pageRange); i++) {
    pages.push(i);
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <h1 className="text-3xl font-bold text-slate-100">Browse</h1>
        <div className="flex items-center gap-2">
          {surpriseError && <span className="text-xs text-red-400">{surpriseError}</span>}
          <button
            type="button"
            onClick={handleSurprise}
            disabled={surprising}
            title="Open a random book (respects author/tag/series filter)"
            className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors disabled:opacity-50"
          >
            {surprising ? 'Picking…' : '🎲 Surprise me'}
          </button>
        </div>
      </div>

      <BooksToolbar value={filters} onApply={handleApply} onReset={handleReset} />

      {items.length === 0 ? (
        <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-8 text-center">
          <p className="text-slate-300 font-medium">No books match these filters.</p>
          <p className="mt-1 text-sm text-slate-500">Try widening the criteria or reset all.</p>
          <button
            type="button"
            onClick={handleReset}
            className="mt-4 px-4 py-2 text-sm rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600"
          >
            Clear all filters
          </button>
        </div>
      ) : (
        <BookGrid books={items} />
      )}

      {total > limit && (
        <nav className="mt-8 flex flex-col items-center gap-4" aria-label="Pagination Navigation">
          <p className="text-sm text-slate-400">
            Showing <span className="text-slate-200 font-medium">{offset + 1}</span>–
            <span className="text-slate-200 font-medium">{Math.min(offset + limit, total)}</span> of{' '}
            <span className="text-slate-200 font-medium">{total}</span> books
          </p>

          <div className="flex flex-wrap items-center justify-center gap-1">
            {page > 1 && (
              <Link
                href={buildPageUrl(base, 1, filters)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="First Page"
              >
                First
              </Link>
            )}

            {page > 1 ? (
              <Link
                href={buildPageUrl(base, page - 1, filters)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="Previous Page"
              >
                Prev
              </Link>
            ) : (
              <span className="px-3 py-2 text-sm text-slate-500 bg-slate-800/50 border border-slate-700/50 rounded-md cursor-not-allowed">
                Prev
              </span>
            )}

            {pages[0] > 1 && <span className="px-2 text-slate-600">...</span>}
            {pages.map((p) => (
              <Link
                key={p}
                href={buildPageUrl(base, p, filters)}
                className={`w-10 h-10 flex items-center justify-center text-sm font-medium rounded-md transition-all ${
                  p === page
                    ? 'bg-amber text-slate-900 border border-amber'
                    : 'bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300'
                }`}
              >
                {p}
              </Link>
            ))}
            {pages[pages.length - 1] < totalPages && (
              <span className="px-2 text-slate-600">...</span>
            )}

            {page < totalPages ? (
              <Link
                href={buildPageUrl(base, page + 1, filters)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="Next Page"
              >
                Next
              </Link>
            ) : (
              <span className="px-3 py-2 text-sm text-slate-500 bg-slate-800/50 border border-slate-700/50 rounded-md cursor-not-allowed">
                Next
              </span>
            )}

            {page < totalPages && (
              <Link
                href={buildPageUrl(base, totalPages, filters)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="Last Page"
              >
                Last
              </Link>
            )}
          </div>
        </nav>
      )}
    </div>
  );
}

export default function BooksPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <BooksPageInner />
    </Suspense>
  );
}
