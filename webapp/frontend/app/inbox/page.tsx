'use client';

import { type Book, getBookCoverUrl, getBooks } from '@/common/api';
import Link from 'next/link';
import { Suspense, useEffect, useState } from 'react';

const BACKEND_HINT = 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721).';
const PAGE_SIZE = 20;

function authorNames(book: Book): string {
  const a = book.authors ?? [];
  return a
    .map((x) => (typeof x === 'string' ? x : (x.name ?? '')))
    .filter(Boolean)
    .join(', ');
}

function InboxPageInner() {
  const [items, setItems] = useState<Book[]>([]);
  const [total, setTotal] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await getBooks({ sort_by: 'timestamp', sort_order: 'desc', limit: PAGE_SIZE });
        if (!cancelled) {
          setItems(res.items ?? []);
          setTotal(res.total ?? null);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-6" data-testid="inbox-page">
        <p className="text-slate-300" data-testid="inbox-loading">
          Loading inbox…
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6" data-testid="inbox-page">
        <h1 className="text-3xl font-bold mb-2 text-slate-100" data-testid="inbox-title">
          Inbox
        </h1>
        <p className="text-slate-300 mb-2" data-testid="inbox-error">
          Backend unreachable: {error}. {BACKEND_HINT}
        </p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="rounded border border-slate-600 px-3 py-1 text-slate-200"
          data-testid="inbox-retry"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6" data-testid="inbox-page">
      <h1 className="text-3xl font-bold mb-2 text-slate-100" data-testid="inbox-title">
        Inbox
      </h1>
      <p className="text-slate-300 mb-6" data-testid="inbox-summary">
        {total != null ? `${total} books in library — ` : ''}showing the {items.length} most
        recently added. Open one to file it (tags, series, rating) or start reading.
      </p>
      {items.length === 0 ? (
        <p className="text-slate-300" data-testid="inbox-empty">
          Inbox clear — no books found. Import one via{' '}
          <Link href="/import" className="underline">
            Import
          </Link>
          .
        </p>
      ) : (
        <ul className="grid gap-3 max-w-3xl" data-testid="inbox-list">
          {items.map((b) => (
            <li
              key={b.id}
              className="rounded-lg border border-slate-600 bg-slate-800/50 p-4 flex gap-4 items-center"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={getBookCoverUrl(b.id)}
                alt=""
                width={48}
                height={72}
                className="rounded object-cover bg-slate-700"
                loading="lazy"
              />
              <div className="min-w-0">
                <Link
                  href={`/book/${b.id}`}
                  className="font-medium text-slate-100 underline truncate block"
                >
                  {b.title}
                </Link>
                <p className="text-sm text-slate-300 truncate">
                  {authorNames(b) || 'Unknown author'}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function InboxPage() {
  return (
    <Suspense fallback={<p className="p-6 text-slate-300">Loading inbox…</p>}>
      <InboxPageInner />
    </Suspense>
  );
}
