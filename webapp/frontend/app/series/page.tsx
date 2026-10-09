'use client';

import { getSeriesCompletion, getSeriesStats, listSeries } from '@/common/api';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';

function CompletionPanel() {
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSeriesStats()
      .then((s) => setStats(s))
      .catch(() => {});
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const r = await getSeriesCompletion({ min_books: 2, incomplete_only: true });
      setReport(r);
      setOpen(true);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  const statChips: string[] = [];
  if (stats) {
    for (const [k, v] of Object.entries(stats)) {
      if (typeof v === 'number') statChips.push(`${k.replace(/_/g, ' ')}: ${v.toLocaleString()}`);
    }
  }

  const items = Array.isArray((report as { series?: unknown[] })?.series)
    ? ((report as { series: { name?: string; owned?: number; total?: number }[] }).series ?? [])
    : Array.isArray((report as { incomplete_series?: unknown[] })?.incomplete_series)
      ? (report as { incomplete_series: { name?: string; owned?: number; total?: number }[] })
          .incomplete_series
      : [];

  return (
    <div className="mb-6 rounded-lg bg-slate-800/60 border border-slate-700 p-4">
      {statChips.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3" data-testid="series-stats">
          {statChips.slice(0, 6).map((c) => (
            <span
              key={c}
              className="px-2.5 py-1 text-xs rounded-full bg-slate-800 border border-slate-600 text-slate-300"
            >
              {c}
            </span>
          ))}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => (open ? setOpen(false) : report ? setOpen(true) : load())}
          disabled={loading}
          className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-600 hover:border-amber/50 text-slate-200 disabled:opacity-50"
        >
          {loading ? 'Checking…' : open ? 'Hide completion report' : 'Completion report'}
        </button>
        <span className="text-xs text-slate-500">
          Which series are missing volumes (/series/completion).
        </span>
      </div>
      {open && (
        <div className="mt-3">
          {items.length === 0 ? (
            <p className="text-sm text-slate-400">No incomplete series found (min 2 books).</p>
          ) : (
            <ul className="space-y-1 max-h-64 overflow-auto">
              {items.slice(0, 100).map((s, i) => (
                <li
                  key={i}
                  className="text-sm text-slate-300 flex justify-between gap-2 px-2 py-1 rounded bg-slate-900/50"
                >
                  <Link
                    href={`/series/analysis?series=${encodeURIComponent(s.name ?? '')}`}
                    className="text-amber hover:underline truncate"
                  >
                    {s.name ?? `Series ${i + 1}`}
                  </Link>
                  <span className="text-slate-500 shrink-0">
                    {s.owned ?? '?'} / {s.total ?? '?'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function SeriesPageInner() {
  const searchParams = useSearchParams();
  const query = searchParams?.get('query') ?? undefined;
  const page = Math.max(1, Number.parseInt(searchParams?.get('page') ?? '1', 10));
  const limit = 50;
  const offset = (page - 1) * limit;

  const [data, setData] = useState<{
    items: { id: number; name: string; book_count?: number }[];
    total: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    listSeries({ query, limit, offset })
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
  }, [query, limit, offset]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Loading series…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-slate-100">Series</h1>
          <Link
            href="/series/analysis"
            className="px-3 py-1.5 rounded-lg bg-amber/20 text-amber text-sm font-medium hover:bg-amber/30"
          >
            Series analysis →
          </Link>
        </div>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load series</p>
          <p className="mt-2 text-sm text-slate-400">{error ?? 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  const total = data.total;
  const totalPages = Math.ceil(total / limit);
  const hasPrev = page > 1;
  const hasNext = page < totalPages;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Series</h1>
      <CompletionPanel />
      <form className="mb-6" action="/series" method="get">
        <input
          type="search"
          name="query"
          defaultValue={query}
          placeholder="Search series..."
          className="w-full max-w-md px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
        />
      </form>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {data.items.map((s) => (
          <Link
            key={s.id}
            href={`/series/${s.id}`}
            className="block p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 hover:bg-slate-700 transition-colors"
          >
            <span className="text-slate-200 font-medium">{s.name}</span>
            {s.book_count != null && (
              <span className="block text-sm text-slate-500 mt-1">{s.book_count} books</span>
            )}
          </Link>
        ))}
      </div>
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
                href={`/series?page=${page - 1}${query ? `&query=${encodeURIComponent(query)}` : ''}`}
                className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
              >
                Previous
              </Link>
            ) : (
              <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Previous</span>
            )}
            {hasNext ? (
              <Link
                href={`/series?page=${page + 1}${query ? `&query=${encodeURIComponent(query)}` : ''}`}
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

export default function SeriesPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <SeriesPageInner />
    </Suspense>
  );
}
