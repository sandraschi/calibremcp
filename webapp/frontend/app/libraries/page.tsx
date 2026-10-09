'use client';

import {
  type Library,
  crossLibrarySearch,
  discoverLibraries,
  listLibraries,
  testLibraryConnection,
} from '@/common/api';
import { LibrariesBrowser } from '@/components/libraries/libraries-browser';
import { LibraryOperations } from '@/components/libraries/library-operations';
import { LibraryStatsPanel } from '@/components/libraries/library-stats-panel';
import { ErrorBanner } from '@/components/ui/error-banner';
import { Suspense, useCallback, useEffect, useState } from 'react';

const BACKEND_HINT = 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721).';

function LibrariesPageInner() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [currentLibrary, setCurrentLibrary] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Cross-library search + discovery tools
  const [xQuery, setXQuery] = useState('');
  const [xBusy, setXBusy] = useState(false);
  const [xResult, setXResult] = useState<string | null>(null);
  const [xError, setXError] = useState<string | null>(null);
  const [opsOpen, setOpsOpen] = useState(false);

  const fetchLibraries = useCallback(async () => {
    const res = await listLibraries();
    setLibraries(res.libraries);
    setCurrentLibrary(res.current_library);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchLibraries()
      .catch((e) => {
        if (!cancelled) setError(String((e as Error).message));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [fetchLibraries]);

  const handleSwitch = useCallback(
    (name: string) => {
      setCurrentLibrary(name);
      // Refresh list so is_active flags settle to the new truth.
      fetchLibraries().catch(() => {});
    },
    [fetchLibraries],
  );

  const runLibOp = async (label: string, fn: () => Promise<unknown>) => {
    setXBusy(true);
    setXError(null);
    setXResult(null);
    try {
      const res = await fn();
      setXResult(JSON.stringify(res, null, 1).slice(0, 3000));
      await fetchLibraries().catch(() => {});
    } catch (e) {
      setXError(e instanceof Error ? e.message : `${label} failed`);
    } finally {
      setXBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Loading libraries…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>
        <ErrorBanner
          title="Could not load libraries"
          message={error ?? 'Unknown error'}
          hint={BACKEND_HINT}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>

      <div className="mb-6 rounded-lg bg-slate-800/60 border border-slate-700">
        <button
          type="button"
          onClick={() => setOpsOpen((o) => !o)}
          aria-expanded={opsOpen}
          className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-slate-200"
        >
          <span>Cross-library search, discovery & connection test</span>
          <span className="text-amber">{opsOpen ? '−' : '+'}</span>
        </button>
        {opsOpen && (
          <div className="px-4 pb-4 space-y-3">
            <form
              className="flex gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (xQuery.trim())
                  runLibOp('Cross-library search', () => crossLibrarySearch(xQuery.trim()));
              }}
            >
              <input
                type="search"
                value={xQuery}
                onChange={(e) => setXQuery(e.target.value)}
                placeholder="Search books across ALL libraries…"
                className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber"
              />
              <button
                type="submit"
                disabled={xBusy || !xQuery.trim()}
                className="px-4 py-2 text-sm rounded-md bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50"
              >
                Search all
              </button>
            </form>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={xBusy}
                onClick={() => runLibOp('Discover', () => discoverLibraries())}
                className="px-3 py-1.5 text-sm rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600 disabled:opacity-50"
              >
                Discover libraries
              </button>
              <button
                type="button"
                disabled={xBusy}
                onClick={() => runLibOp('Connection test', testLibraryConnection)}
                className="px-3 py-1.5 text-sm rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600 disabled:opacity-50"
              >
                Test connection
              </button>
            </div>
            {xBusy && <p className="text-sm text-slate-400">Working…</p>}
            {xError && <p className="text-sm text-red-400">{xError}</p>}
            {xResult && (
              <pre className="text-xs text-slate-300 whitespace-pre-wrap font-sans max-h-72 overflow-auto rounded bg-slate-900 p-3">
                {xResult}
              </pre>
            )}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-slate-200">Available Libraries</h2>
          <LibrariesBrowser
            libraries={libraries}
            currentLibrary={currentLibrary}
            onSwitch={handleSwitch}
          />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4 text-slate-200">Library Statistics</h2>
          <LibraryStatsPanel currentLibrary={currentLibrary} />
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-2xl font-semibold mb-4 text-slate-200">Library Operations</h2>
        <LibraryOperations
          libraries={libraries}
          currentLibrary={currentLibrary}
          onSwitched={handleSwitch}
        />
      </div>
    </div>
  );
}

export default function LibrariesPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <LibrariesPageInner />
    </Suspense>
  );
}
