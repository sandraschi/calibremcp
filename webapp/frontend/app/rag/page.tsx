'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import Link from 'next/link';
import {
  ragMetadataBuild,
  ragMetadataBuildStatus,
  ragMetadataSearch,
  type RagMetadataSearchHit,
  type RagMetadataBuildStatus as BuildStatusType,
} from '@/common/api';

const POLL_INTERVAL_MS = 1500;

export default function RagPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<RagMetadataSearchHit[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [building, setBuilding] = useState(false);
  const [buildStatus, setBuildStatus] = useState<BuildStatusType | null>(null);
  const [searching, setSearching] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    setBuilding(false);
  }, []);

  async function handleBuild(forceRebuild: boolean) {
    setError(null);
    setMessage(null);
    setBuildStatus(null);
    setBuilding(true);
    try {
      const res = await ragMetadataBuild(forceRebuild);
      if (res.error || res.success === false) {
        setError(res.error ?? res.message ?? 'Build failed');
        setBuilding(false);
        return;
      }
      if (res.status === 'started') {
        const poll = async () => {
          try {
            const status = await ragMetadataBuildStatus();
            setBuildStatus(status);
            if (status.status === 'done') {
              stopPolling();
              setMessage(status.total ? `Indexed ${status.total} books.` : (status.message || 'Done.'));
            } else if (status.status === 'error') {
              stopPolling();
              setError(status.message || 'Build failed');
            }
          } catch {
            // keep polling on transient errors
          }
        };
        await poll();
        pollRef.current = setInterval(poll, POLL_INTERVAL_MS);
      } else {
        setMessage(res.message ?? `Indexed ${res.books_indexed ?? 0} books.`);
        setBuilding(false);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Build failed');
      setBuilding(false);
    }
  }

  async function handleSearch() {
    if (!query.trim()) return;
    setError(null);
    setMessage(null);
    setSearching(true);
    try {
      const res = await ragMetadataSearch(query.trim(), 10);
      setResults(res.results ?? []);
      setMessage(res.message ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Search failed');
      setResults([]);
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Semantic Search (Metadata RAG)</h1>
      <p className="text-slate-400 mb-6">
        Search your library by meaning using LanceDB over title, authors, tags, and comments. Build the index once per library, then search with natural language.
      </p>

      <div className="space-y-6 max-w-2xl">
        <section className="rounded-lg border border-slate-600 bg-slate-800/50 p-4">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Index</h2>
          <p className="text-sm text-slate-400 mb-3">
            Build or rebuild the metadata index for the current library. Run after adding many books.
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleBuild(false)}
              disabled={building}
              className="px-4 py-2 rounded-lg bg-amber/20 text-amber font-medium hover:bg-amber/30 disabled:opacity-50"
            >
              {building ? 'Building…' : 'Build index'}
            </button>
            <button
              type="button"
              onClick={() => handleBuild(true)}
              disabled={building}
              className="px-4 py-2 rounded-lg bg-slate-600 text-slate-200 font-medium hover:bg-slate-500 disabled:opacity-50"
            >
              {building ? 'Building…' : 'Rebuild from scratch'}
            </button>
          </div>
          {building && buildStatus && (
            <div className="mt-3 space-y-1">
              <div className="flex justify-between text-sm text-slate-400">
                <span>{buildStatus.message || 'Building…'}</span>
                <span>
                  {buildStatus.total > 0
                    ? `${buildStatus.current} / ${buildStatus.total} (${buildStatus.percentage}%)`
                    : '…'}
                </span>
              </div>
              <div className="h-2 rounded-full bg-slate-700 overflow-hidden">
                <div
                  className="h-full bg-amber/60 transition-[width] duration-300"
                  style={{ width: `${buildStatus.percentage}%` }}
                />
              </div>
            </div>
          )}
        </section>

        <section className="rounded-lg border border-slate-600 bg-slate-800/50 p-4">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Search</h2>
          <p className="text-sm text-slate-400 mb-3">
            e.g. &quot;Japanese mystery light novels&quot;, &quot;Python programming&quot;
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Describe what you want to find…"
              className="flex-1 rounded-lg border border-slate-600 bg-slate-900 text-slate-100 px-3 py-2 placeholder-slate-500"
            />
            <button
              type="button"
              onClick={handleSearch}
              disabled={searching || !query.trim()}
              className="px-4 py-2 rounded-lg bg-amber/20 text-amber font-medium hover:bg-amber/30 disabled:opacity-50"
            >
              {searching ? 'Searching…' : 'Search'}
            </button>
          </div>
        </section>

        {error && (
          <div className="rounded-lg border border-red-800 bg-red-900/30 p-3 text-red-200 text-sm">
            {error}
          </div>
        )}
        {message && !error && (
          <p className="text-slate-300 text-sm">{message}</p>
        )}

        {results.length > 0 && (
          <ul className="space-y-2">
            {results.map((hit, i) => (
              <li key={`${hit.book_id}-${i}`} className="rounded-lg border border-slate-600 bg-slate-800/50 p-3">
                <Link href={`/book/${hit.book_id}`} className="font-medium text-amber hover:underline">
                  {hit.title}
                </Link>
                {hit.text && (
                  <p className="text-sm text-slate-400 mt-1 line-clamp-2">{hit.text}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
