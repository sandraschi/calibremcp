'use client';

import { listPublishers } from '@/common/api';
import { TaxonomyList, ViewToggle, parseTaxonomyView } from '@/components/taxonomy/taxonomy-view';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';

function PublishersPageInner() {
  const searchParams = useSearchParams();
  const query = searchParams?.get('query') ?? undefined;
  const view = parseTaxonomyView(searchParams?.get('view'));
  const sortBy = searchParams?.get('sort_by') === 'book_count' ? 'book_count' : 'name';
  const sortOrder = searchParams?.get('sort_order') === 'desc' ? 'desc' : 'asc';
  const page = Math.max(1, Number.parseInt(searchParams?.get('page') ?? '1', 10));
  const limit = 50;
  const offset = (page - 1) * limit;

  const [data, setData] = useState<{
    items: { id: number | null; name: string; book_count?: number }[];
    total: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    listPublishers({ query, limit, offset, sort_by: sortBy, sort_order: sortOrder })
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
  }, [query, limit, offset, sortBy, sortOrder]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Loading publishers…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Publishers</h1>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load publishers</p>
          <p className="mt-2 text-sm text-slate-400">{error ?? 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  const total = data.total;
  const totalPages = Math.ceil(total / limit);
  const hasPrev = page > 1;
  const hasNext = page < totalPages;

  const pageHref = (p: number, v: typeof view = view) => {
    const sp = new URLSearchParams();
    if (p > 1) sp.set('page', String(p));
    if (query) sp.set('query', query);
    if (sortBy !== 'name') sp.set('sort_by', sortBy);
    if (sortOrder !== 'asc') sp.set('sort_order', sortOrder);
    if (v !== 'card') sp.set('view', v);
    const q = sp.toString();
    return q ? `/publishers?${q}` : '/publishers';
  };

  const inputCls =
    'px-3 py-1.5 bg-slate-700 border border-slate-600 rounded-md text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber';

  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h1 className="text-3xl font-bold text-slate-100">Publishers</h1>
        <ViewToggle
          cardHref={pageHref(page, 'card')}
          listHref={pageHref(page, 'list')}
          view={view}
        />
      </div>
      <div className="flex flex-wrap items-center gap-2 mb-6">
        <form className="flex-1 min-w-52" action="/publishers" method="get">
          {view !== 'card' && <input type="hidden" name="view" value={view} />}
          {sortBy !== 'name' && <input type="hidden" name="sort_by" value={sortBy} />}
          {sortOrder !== 'asc' && <input type="hidden" name="sort_order" value={sortOrder} />}
          <input
            type="search"
            name="query"
            defaultValue={query}
            placeholder="Search publishers..."
            className="w-full max-w-md px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </form>
        <form action="/publishers" method="get" className="flex items-center gap-2">
          {query && <input type="hidden" name="query" value={query} />}
          {view !== 'card' && <input type="hidden" name="view" value={view} />}
          <select name="sort_by" defaultValue={sortBy} className={inputCls} title="Sort by">
            <option value="name">Name</option>
            <option value="book_count">Book count</option>
          </select>
          <select name="sort_order" defaultValue={sortOrder} className={inputCls} title="Order">
            <option value="asc">Asc</option>
            <option value="desc">Desc</option>
          </select>
          <button
            type="submit"
            className="px-3 py-1.5 text-sm rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600"
          >
            Sort
          </button>
        </form>
      </div>
      {view === 'list' ? (
        <TaxonomyList
          items={data.items.map((p) => ({
            key: String(p.id ?? p.name),
            name: p.name,
            meta: p.book_count != null ? `${p.book_count} books` : null,
          }))}
          getHref={(it) => `/books?publisher=${encodeURIComponent(it.name)}`}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {data.items.map((p) => (
            <Link
              key={p.id ?? p.name}
              href={`/books?publisher=${encodeURIComponent(p.name)}`}
              className="block p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 hover:bg-slate-700 transition-colors"
            >
              <span className="text-slate-200 font-medium">{p.name}</span>
              {p.book_count != null && (
                <span className="block text-sm text-slate-500 mt-1">{p.book_count} books</span>
              )}
            </Link>
          ))}
        </div>
      )}
      {total > limit && (
        <nav
          className="mt-6 flex flex-wrap items-center justify-center gap-2"
          aria-label="Pagination"
        >
          <p className="w-full text-center text-sm text-slate-400 mb-2">
            Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            {hasPrev ? (
              <Link
                href={pageHref(page - 1)}
                className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
              >
                Previous
              </Link>
            ) : (
              <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Previous</span>
            )}
            {hasNext ? (
              <Link
                href={pageHref(page + 1)}
                className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
              >
                Next
              </Link>
            ) : (
              <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Next</span>
            )}
          </div>
        </nav>
      )}
    </div>
  );
}

export default function PublishersPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <PublishersPageInner />
    </Suspense>
  );
}
