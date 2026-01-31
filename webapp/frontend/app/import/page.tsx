'use client';

import { useState, useCallback } from 'react';
import {
  searchAnnas,
  getAnnasMirrors,
  type AnnasSearchResult,
} from '@/lib/api';

export default function ImportPage() {
  const [path, setPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    success?: boolean;
    message?: string;
    error?: string;
  } | null>(null);

  const [annasQuery, setAnnasQuery] = useState('');
  const [annasLoading, setAnnasLoading] = useState(false);
  const [annasResults, setAnnasResults] = useState<AnnasSearchResult[]>([]);
  const [annasError, setAnnasError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!path.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: path.trim(), fetch_metadata: true }),
      });
      const data = await res.json();
      if (res.ok) {
        setResult({ success: true, message: `Added book: ${data.title ?? 'OK'}` });
        setPath('');
      } else {
        setResult({
          success: false,
          error: data.detail ?? data.error ?? 'Import failed',
        });
      }
    } catch (e) {
      setResult({
        success: false,
        error: e instanceof Error ? e.message : 'Request failed',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAnnasSearch = useCallback(async () => {
    if (!annasQuery.trim()) return;
    setAnnasLoading(true);
    setAnnasError(null);
    setAnnasResults([]);
    try {
      const mirrorsRaw = getAnnasMirrors().trim();
      const mirrors = mirrorsRaw
        ? mirrorsRaw.split(',').map((m) => m.trim()).filter(Boolean)
        : undefined;
      const resp = await searchAnnas({
        query: annasQuery.trim(),
        max_results: 24,
        mirrors,
      });
      if (resp.success) {
        setAnnasResults(resp.results);
        if (resp.results.length === 0 && !resp.error) {
          setAnnasError('No results found. Try a different search.');
        }
      } else {
        setAnnasError(resp.error ?? 'Search failed');
      }
    } catch (e) {
      setAnnasError(e instanceof Error ? e.message : 'Search failed');
      setAnnasResults([]);
    } finally {
      setAnnasLoading(false);
    }
  }, [annasQuery]);

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Import</h1>

      {/* Anna's Archive section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-3 text-slate-200">
          Anna&apos;s Archive
        </h2>
        <p className="text-slate-400 text-sm mb-4">
          Search by book title or author. Click a result to open it on Anna&apos;s
          Archive (configure mirror URL in Settings).
        </p>
        <div className="flex flex-wrap gap-3 mb-4">
          <input
            type="text"
            value={annasQuery}
            onChange={(e) => setAnnasQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAnnasSearch()}
            placeholder="Book title or author"
            className="flex-1 min-w-[200px] px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
          <button
            type="button"
            onClick={handleAnnasSearch}
            disabled={annasLoading || !annasQuery.trim()}
            className="px-6 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {annasLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
        {annasError && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/20 text-red-400 text-sm">
            {annasError}
          </div>
        )}
        {annasResults.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
            {annasResults.map((book, i) => (
              <a
                key={`${book.detail_item}-${i}`}
                href={book.detail_url}
                target="_blank"
                rel="noopener noreferrer"
                className="block border border-slate-600 rounded-lg p-3 bg-slate-800 hover:bg-slate-700 hover:border-amber/50 transition-colors"
              >
                <div className="h-32 bg-slate-700 rounded mb-2 flex items-center justify-center">
                  <span className="text-slate-500 text-xs text-center px-2">
                    No cover
                  </span>
                </div>
                <h3 className="font-medium text-slate-100 text-sm line-clamp-2 mb-1">
                  {book.title || 'Untitled'}
                </h3>
                <p className="text-xs text-slate-400 line-clamp-1">
                  {book.author || 'Unknown'}
                </p>
                {book.formats && (
                  <p className="text-xs text-amber/80 mt-1">{book.formats}</p>
                )}
              </a>
            ))}
          </div>
        )}
      </section>

      {/* File path import section */}
      <section>
        <h2 className="text-xl font-semibold mb-3 text-slate-200">
          Import from file path
        </h2>
        <p className="text-slate-400 mb-6">
          Add a book from a file path. The path must be accessible from the
          server (e.g. a path on the machine running the backend).
        </p>
        <form onSubmit={handleSubmit} className="max-w-xl space-y-4">
          <div>
            <label
              htmlFor="path"
              className="block text-sm font-medium text-slate-300 mb-2"
            >
              File path
            </label>
            <input
              id="path"
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="C:\Books\mybook.epub or /path/to/book.epub"
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !path.trim()}
            className="px-6 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Importing...' : 'Import'}
          </button>
          {result && (
            <div
              className={`p-4 rounded-lg ${
                result.success
                  ? 'bg-emerald-500/20 text-emerald-300'
                  : 'bg-red-500/20 text-red-400'
              }`}
            >
              {result.success ? result.message : result.error}
            </div>
          )}
        </form>
      </section>
    </div>
  );
}
