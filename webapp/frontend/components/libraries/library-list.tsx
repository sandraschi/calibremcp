'use client';

import { useState } from 'react';
import { Library, switchLibrary } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface LibraryListProps {
  libraries: Library[];
  currentLibrary?: string;
}

export function LibraryList({ libraries, currentLibrary }: LibraryListProps) {
  const router = useRouter();
  const [switching, setSwitching] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleClick = async (library: Library) => {
    if (library.name === currentLibrary) return;
    setError(null);
    setSwitching(library.name);
    try {
      await switchLibrary(library.name);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to switch library');
    } finally {
      setSwitching(null);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-600 p-4">
      {error && (
        <div className="mb-4 p-3 rounded bg-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}
      {libraries.length === 0 ? (
        <p className="text-slate-400">No libraries found.</p>
      ) : (
        <div className="space-y-2">
          {libraries.map((library) => (
            <button
              type="button"
              key={library.name}
              onClick={() => handleClick(library)}
              disabled={!!switching}
              className={`w-full text-left p-3 border rounded-lg transition-colors ${
                library.is_active || library.name === currentLibrary
                  ? 'border-amber bg-amber/10'
                  : 'border-slate-600 bg-slate-700/50 hover:bg-slate-700'
              } ${switching ? 'opacity-70 cursor-wait' : 'cursor-pointer'}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg text-slate-100">
                    {library.name}
                    {switching === library.name && (
                      <span className="ml-2 text-xs text-slate-400">Switching...</span>
                    )}
                    {(library.is_active || library.name === currentLibrary) && switching !== library.name && (
                      <span className="ml-2 text-xs bg-amber text-slate-900 px-2 py-1 rounded">
                        Active
                      </span>
                    )}
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">{library.path}</p>
                  <div className="mt-2 flex gap-4 text-sm text-slate-500">
                    {library.book_count !== undefined && (
                      <span>{library.book_count} books</span>
                    )}
                    {library.size_mb !== undefined && (
                      <span>{library.size_mb.toFixed(2)} MB</span>
                    )}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
