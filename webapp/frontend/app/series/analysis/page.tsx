'use client';

import { useState } from 'react';
import Link from 'next/link';
import { getSeriesAnalysis, type SeriesAnalysisResult, type SeriesAnalysisBook } from '@/common/api';

function StatusBadge({ owned }: { owned: boolean }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
      owned
        ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700/50'
        : 'bg-slate-700 text-slate-400 border border-slate-600'
    }`}>
      {owned ? 'Owned' : 'Missing'}
    </span>
  );
}

function ProgressBar({ owned, total }: { owned: number; total: number }) {
  const pct = total > 0 ? Math.round((owned / total) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-slate-400">{owned} / {total} volumes owned</span>
        <span className="text-slate-400">{pct}%</span>
      </div>
      <div className="h-2 rounded-full bg-slate-700 overflow-hidden">
        <div
          className="h-full bg-amber/60 transition-[width] duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function SeriesAnalysisPage() {
  const [seriesName, setSeriesName] = useState('');
  const [result, setResult] = useState<SeriesAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyse() {
    if (!seriesName.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await getSeriesAnalysis(seriesName.trim());
      if (res.error) setError(res.error);
      else setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  const owned = result?.owned_count ?? result?.books?.filter((b) => b.owned).length ?? 0;
  const total = result?.total_volumes ?? result?.books?.length ?? 0;
  const missing = result?.missing ?? result?.books?.filter((b) => !b.owned).map((b) => b.title) ?? [];

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-2xl">
      <div className="flex items-center gap-3 mb-2">
        <Link href="/series" className="text-slate-400 hover:text-slate-200 text-sm">← Series</Link>
      </div>

      <div>
        <h1 className="text-3xl font-bold text-slate-100">Series Analysis</h1>
        <p className="text-slate-400 mt-1">
          Reading order, completion status, and missing volumes for any series in your library.
        </p>
      </div>

      {/* Query */}
      <div className="rounded-lg border border-slate-600 bg-slate-800/50 p-4 space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={seriesName}
            onChange={(e) => setSeriesName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAnalyse()}
            placeholder="e.g. Culture, Hyperion, The Expanse…"
            className="flex-1 rounded-lg border border-slate-600 bg-slate-900 text-slate-100 px-3 py-2 placeholder-slate-500"
          />
          <button
            type="button"
            onClick={handleAnalyse}
            disabled={loading || !seriesName.trim()}
            className="px-4 py-2 rounded-lg bg-amber/20 text-amber font-medium hover:bg-amber/30 disabled:opacity-50"
          >
            {loading ? 'Analysing…' : 'Analyse'}
          </button>
        </div>
        <p className="text-xs text-slate-500">
          Series name must match how it appears in Calibre (partial match may work depending on backend).
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-800 bg-red-900/30 p-3 text-red-200 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-5">
          {/* Header */}
          <div className="rounded-lg border border-slate-600 bg-slate-800/50 p-4 space-y-3">
            <h2 className="text-xl font-semibold text-slate-100">{result.series}</h2>
            <ProgressBar owned={owned} total={total} />
            {missing.length > 0 && (
              <div>
                <p className="text-sm text-slate-400 mb-1">
                  Missing {missing.length} volume{missing.length !== 1 ? 's' : ''}:
                </p>
                <ul className="space-y-0.5">
                  {missing.map((title, i) => (
                    <li key={i} className="text-sm text-slate-500 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-600 shrink-0" />
                      {title}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Book list */}
          {result.books && result.books.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide">
                Reading order
              </h3>
              <ol className="space-y-1.5">
                {result.books.map((book: SeriesAnalysisBook, i) => {
                  const idx = book.series_index ?? book.index ?? (i + 1);
                  return (
                    <li key={i}
                      className={`flex items-center gap-3 rounded-lg border p-3 ${
                        book.owned
                          ? 'border-slate-600 bg-slate-800/50'
                          : 'border-slate-700/50 bg-slate-800/20 opacity-60'
                      }`}>
                      <span className="text-slate-500 text-sm w-8 shrink-0 text-right">
                        {typeof idx === 'number' ? idx : i + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        {book.book_id && book.owned ? (
                          <Link href={`/book/${book.book_id}`}
                            className="text-amber hover:underline font-medium truncate block">
                            {book.title}
                          </Link>
                        ) : (
                          <span className="text-slate-300 font-medium truncate block">
                            {book.title}
                          </span>
                        )}
                      </div>
                      <StatusBadge owned={book.owned} />
                    </li>
                  );
                })}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
