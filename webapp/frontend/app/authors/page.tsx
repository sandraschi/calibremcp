'use client';

import { getAuthorsStats, listAuthors, listAuthorsByLetter } from '@/common/api';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';

const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

interface AuthorRow {
  id: number;
  name: string;
  book_count?: number;
}

function AuthorsPageInner() {
  const searchParams = useSearchParams();
  const query = searchParams?.get('query') ?? undefined;
  const letter = searchParams?.get('letter') ?? undefined;
  const page = Math.max(1, Number.parseInt(searchParams?.get('page') ?? '1', 10));
  const limit = 50;
  const offset = (page - 1) * limit;

  const [data, setData] = useState<{ items: AuthorRow[]; total: number } | null>(null);
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuthorsStats()
      .then((s) => setStats(s))
      .catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    const loader =
      letter && !query
        ? listAuthorsByLetter(letter).then((r) => ({
            items: r.items as AuthorRow[],
            total: r.total,
          }))
        : listAuthors({ query, limit, offset }).then((r) => ({
            items: r.items as AuthorRow[],
            total: r.total,
          }));
    loader
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
  }, [query, letter, limit, offset]);

  const statsChips: string[] = [];
  if (stats) {
    for (const [k, v] of Object.entries(stats)) {
      if (typeof v === 'number' && !k.includes('execution_time')) {
        statsChips.push(`${k.replace(/_/g, ' ')}: ${v.toLocaleString()}`);
      }
    }
  }

  const total = data?.total ?? 0;
  const items = data?.items ?? [];
  const totalPages = Math.ceil(total / limit);
  const hasPrev = page > 1 && !letter;
  const hasNext = page < totalPages && !letter;

  const letterHref = (l: string | null) => {
    const p = new URLSearchParams();
    if (l) p.set('letter', l);
    if (query) p.set('query', query);
    const q = p.toString();
    return q ? `/authors?${q}` : '/authors';
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4 text-slate-100">Authors</h1>

      {statsChips.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4" data-testid="authors-stats">
          {statsChips.slice(0, 6).map((c) => (
            <span
              key={c}
              className="px-2.5 py-1 text-xs rounded-full bg-slate-800 border border-slate-600 text-slate-300"
            >
              {c}
            </span>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-1 mb-4" aria-label="Filter by first letter">
        <Link
          href={letterHref(null)}
          className={`px-2.5 py-1.5 text-xs font-medium rounded-md ${
            !letter
              ? 'bg-amber text-slate-900'
              : 'bg-slate-800 border border-slate-700 text-slate-300 hover:border-amber/50'
          }`}
        >
          All
        </Link>
        {LETTERS.map((l) => (
          <Link
            key={l}
            href={letterHref(l)}
            className={`px-2.5 py-1.5 text-xs font-medium rounded-md ${
              letter === l
                ? 'bg-amber text-slate-900'
                : 'bg-slate-800 border border-slate-700 text-slate-300 hover:border-amber/50'
            }`}
          >
            {l}
          </Link>
        ))}
      </div>

      <form className="mb-6" action="/authors" method="get">
        {letter && <input type="hidden" name="letter" value={letter} />}
        <input
          type="search"
          name="query"
          defaultValue={query}
          placeholder="Search authors..."
          className="w-full max-w-md px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
        />
      </form>

      {loading ? (
        <p className="text-slate-400">Loading authors…</p>
      ) : error || !data ? (
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load authors</p>
          <p className="mt-2 text-sm text-slate-400">{error ?? 'Unknown error'}</p>
        </div>
      ) : (
        <>
          <p className="mb-3 text-sm text-slate-400">
            {total} author{total === 1 ? '' : 's'}
            {letter && !query && (
              <>
                {' '}
                starting with <span className="text-amber font-medium">{letter}</span>
              </>
            )}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {items.map((a) => (
              <Link
                key={a.id}
                href={`/books?author=${encodeURIComponent(a.name)}`}
                className="block p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 hover:bg-slate-700 transition-colors"
              >
                <span className="text-slate-200 font-medium">{a.name}</span>
                {a.book_count != null && (
                  <span className="block text-sm text-slate-500 mt-1">{a.book_count} books</span>
                )}
              </Link>
            ))}
          </div>
          {!letter && total > limit && (
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
                    href={`/authors?page=${page - 1}${query ? `&query=${encodeURIComponent(query)}` : ''}`}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
                  >
                    Previous
                  </Link>
                ) : (
                  <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">
                    Previous
                  </span>
                )}
                {hasNext ? (
                  <Link
                    href={`/authors?page=${page + 1}${query ? `&query=${encodeURIComponent(query)}` : ''}`}
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
        </>
      )}
    </div>
  );
}

export default function AuthorsPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <AuthorsPageInner />
    </Suspense>
  );
}
