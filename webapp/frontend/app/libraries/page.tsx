'use client';

import { listLibraries, type Library } from '@/common/api';
import { LibraryList } from '@/components/libraries/library-list';
import { LibraryStatsPanel } from '@/components/libraries/library-stats-panel';
import { LibraryOperations } from '@/components/libraries/library-operations';
import { ErrorBanner } from '@/components/ui/error-banner';
import { Suspense, useEffect, useState } from 'react';

const BACKEND_HINT = 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721).';

function LibrariesPageInner() {
  const [librariesData, setLibrariesData] = useState<{
    libraries: Library[];
    current_library?: string;
    total_libraries: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    listLibraries()
      .then((res) => {
        if (!cancelled) setLibrariesData(res);
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
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Loading libraries…</p>
      </div>
    );
  }

  if (error || !librariesData) {
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

  const currentLibraryName = librariesData.current_library;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-slate-200">Available Libraries</h2>
          <LibraryList
            libraries={librariesData.libraries}
            currentLibrary={currentLibraryName}
          />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4 text-slate-200">Library Statistics</h2>
          <LibraryStatsPanel currentLibrary={currentLibraryName} />
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-2xl font-semibold mb-4 text-slate-200">Library Operations</h2>
        <LibraryOperations
          libraries={librariesData.libraries}
          currentLibrary={currentLibraryName}
        />
      </div>
    </div>
  );
}

export default function LibrariesPage() {
  return (
    <Suspense fallback={<div className="container mx-auto p-6"><p className="text-slate-400">Loading…</p></div>}>
      <LibrariesPageInner />
    </Suspense>
  );
}
