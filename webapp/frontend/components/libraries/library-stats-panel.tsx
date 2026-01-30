'use client';

import { useState, useEffect } from 'react';
import { getLibraryStats, LibraryStats } from '@/lib/api';
import { LibraryStatsDisplay } from './library-stats';

interface LibraryStatsPanelProps {
  currentLibrary?: string | null;
}

export function LibraryStatsPanel({ currentLibrary }: LibraryStatsPanelProps) {
  const [stats, setStats] = useState<LibraryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentLibrary) {
      setStats(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getLibraryStats(currentLibrary)
      .then(setStats)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [currentLibrary]);

  if (!currentLibrary) {
    return (
      <div className="bg-slate-800 border border-slate-600 p-4 rounded-lg">
        <p className="text-slate-400">No library selected.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-slate-800 border border-slate-600 p-4 rounded-lg animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-1/2 mb-4" />
        <div className="grid grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-16 bg-slate-700/50 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-800 border border-slate-600 p-4 rounded-lg">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-slate-800 border border-slate-600 p-4 rounded-lg">
        <p className="text-slate-400">Stats unavailable.</p>
      </div>
    );
  }

  return <LibraryStatsDisplay stats={stats} />;
}
