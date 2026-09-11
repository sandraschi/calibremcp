'use client';

import { type LibraryHealthResult, getLibraryHealth } from '@/common/api';
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Database,
  FileQuestion,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function LibraryHealthPage() {
  const [health, setHealth] = useState<LibraryHealthResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadHealth() {
    setLoading(true);
    setError(null);
    try {
      const res = await getLibraryHealth();
      setHealth(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load library health');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  const score = health ? Math.round(health.health_score || 0) : 0;
  const isScoreHealthy = score >= 80;
  const isScoreModerate = score >= 50 && score < 80;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-700/60 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber/10 border border-amber/20 text-amber">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-100">Library Health & Quality</h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Comprehensive database audit, missing covers, empty records & integrity checks
              </p>
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={loadHealth}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Re-scan Library
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {loading && !health ? (
        <div className="py-24 text-center space-y-4">
          <div className="w-8 h-8 border-3 border-amber border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-slate-400">Auditing Calibre SQLite database and book files…</p>
        </div>
      ) : health ? (
        <div className="space-y-8">
          {/* Top Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Health Score Card */}
            <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-400">Overall Health Score</span>
                <Sparkles className="w-5 h-5 text-amber" />
              </div>
              <div className="my-4 flex items-baseline gap-2">
                <span
                  className={`text-5xl font-extrabold ${
                    isScoreHealthy
                      ? 'text-emerald-400'
                      : isScoreModerate
                        ? 'text-amber'
                        : 'text-red-400'
                  }`}
                >
                  {score}%
                </span>
                <span className="text-xs text-slate-400">
                  {isScoreHealthy
                    ? 'Excellent condition'
                    : isScoreModerate
                      ? 'Minor cleanup needed'
                      : 'Attention required'}
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isScoreHealthy ? 'bg-emerald-500' : isScoreModerate ? 'bg-amber' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(5, score))}%` }}
                />
              </div>
            </div>

            {/* Database Integrity */}
            <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-400">Database Integrity</span>
                <Database className="w-5 h-5 text-slate-400" />
              </div>
              <div className="my-4 flex items-center gap-3">
                {health.database_integrity ? (
                  <>
                    <ShieldCheck className="w-8 h-8 text-emerald-400" />
                    <div>
                      <p className="text-lg font-bold text-slate-100">Passed</p>
                      <p className="text-xs text-slate-400">SQLite PRAGMA check clean</p>
                    </div>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-8 h-8 text-amber" />
                    <div>
                      <p className="text-lg font-bold text-slate-100">Warnings Detected</p>
                      <p className="text-xs text-slate-400">Review SQLite integrity</p>
                    </div>
                  </>
                )}
              </div>
              <p className="text-xs text-slate-500">Checks `metadata.db` schema & indexes</p>
            </div>

            {/* Issues Count */}
            <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-400">Flagged Issues</span>
                <AlertCircle className="w-5 h-5 text-slate-400" />
              </div>
              <div className="my-4">
                <span className="text-4xl font-extrabold text-slate-100">
                  {health.issues_found.length}
                </span>
                <span className="text-xs text-slate-400 ml-2">items found</span>
              </div>
              <p className="text-xs text-slate-500">Categories: missing covers, formats, tags</p>
            </div>
          </div>

          {/* Issues Found Section */}
          <div className="p-6 rounded-xl bg-slate-800/60 border border-slate-700 space-y-4">
            <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <FileQuestion className="w-5 h-5 text-amber" />
              Audit Findings
            </h2>
            {health.issues_found.length === 0 ? (
              <div className="p-6 rounded-lg bg-slate-900/50 border border-slate-800 text-center text-slate-400 space-y-2">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
                <p className="text-sm font-medium text-slate-200">No issues detected!</p>
                <p className="text-xs">
                  All books have covers, formats, and valid metadata records.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-slate-700/60">
                {health.issues_found.map((issue, idx) => {
                  const isObj = typeof issue === 'object' && issue !== null;
                  const desc = isObj ? issue.description || issue.type : String(issue);
                  const count = isObj ? issue.count : undefined;
                  return (
                    <div
                      key={`issue-${idx}-${desc}`}
                      className="py-3.5 flex items-start justify-between gap-4"
                    >
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="w-4 h-4 text-amber shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm text-slate-200 font-medium">{desc}</p>
                          {count != null && (
                            <p className="text-xs text-slate-400 mt-0.5">
                              Affects {count} book{count === 1 ? '' : 's'}
                            </p>
                          )}
                        </div>
                      </div>
                      <Link
                        href="/books"
                        className="text-xs text-amber/90 hover:text-amber underline shrink-0"
                      >
                        View books →
                      </Link>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Recommendations Section */}
          {health.recommendations && health.recommendations.length > 0 && (
            <div className="p-6 rounded-xl bg-slate-800/60 border border-slate-700 space-y-4">
              <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                Recommendations & Action Items
              </h2>
              <ul className="space-y-2.5">
                {health.recommendations.map((rec, i) => (
                  <li key={`rec-${i}`} className="text-sm text-slate-300 flex items-start gap-2.5">
                    <span className="text-amber font-mono font-bold">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
