'use client';

import Link from 'next/link';
import { getBooks, type BookListResponse } from '@/common/api';
import { BookGrid } from '@/components/books/book-grid';
import { ErrorBanner } from '@/components/ui/error-banner';
import { useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';

const BACKEND_HINT = 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721).';

function buildPageUrl(
  base: string,
  page: number,
  author?: string,
  tag?: string,
  publisher?: string
): string {
  const params = new URLSearchParams();
  if (page > 1) params.set('page', page.toString());
  if (author) params.set('author', author);
  if (tag) params.set('tag', tag);
  if (publisher) params.set('publisher', publisher);
  const q = params.toString();
  return q ? `${base}?${q}` : base;
}

function BooksPageInner() {
  const searchParams = useSearchParams();
  const author = searchParams?.get('author') ?? undefined;
  const tag = searchParams?.get('tag') ?? undefined;
  const publisher = searchParams?.get('publisher') ?? undefined;
  const page = Math.max(1, Number.parseInt(searchParams?.get('page') ?? '1', 10));
  const limit = 50;
  const offset = (page - 1) * limit;

  const [data, setData] = useState<BookListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getBooks({ limit, offset, author, tag, publisher })
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
  }, [author, tag, publisher, limit, offset]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Loading books…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Browse</h1>
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
      </div>

      <BookGrid books={items} />

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
                href={buildPageUrl(base, 1, author, tag, publisher)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="First Page"
              >
                First
              </Link>
            )}

            {page > 1 ? (
              <Link
                href={buildPageUrl(base, page - 1, author, tag, publisher)}
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
                href={buildPageUrl(base, p, author, tag, publisher)}
                className={`w-10 h-10 flex items-center justify-center text-sm font-medium rounded-md transition-all ${p === page
                    ? 'bg-amber text-slate-900 border border-amber'
                    : 'bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300'
                  }`}
              >
                {p}
              </Link>
            ))}
            {pages[pages.length - 1] < totalPages && <span className="px-2 text-slate-600">...</span>}

            {page < totalPages ? (
              <Link
                href={buildPageUrl(base, page + 1, author, tag, publisher)}
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
                href={buildPageUrl(base, totalPages, author, tag, publisher)}
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
    <Suspense fallback={<div className="container mx-auto p-6"><p className="text-slate-400">Loading…</p></div>}>
      <BooksPageInner />
    </Suspense>
  );
}
