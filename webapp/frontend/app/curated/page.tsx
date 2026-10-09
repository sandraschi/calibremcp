'use client';

import { getItCurator, getJapaneseOrganizer, getReadingRecommendations } from '@/common/api';
import { FlaskConical } from 'lucide-react';
import { useState } from 'react';

type Job = 'japanese' | 'it' | 'recommendations';

const JOBS: { id: Job; title: string; blurb: string }[] = [
  {
    id: 'japanese',
    title: 'Japanese organizer',
    blurb: 'Organize the Japanese library for maximum cultural efficiency.',
  },
  {
    id: 'it',
    title: 'IT curator',
    blurb: 'Curation pass over the programming and technology collection.',
  },
  {
    id: 'recommendations',
    title: 'Reading recommendations',
    blurb: 'Austrian-efficiency reading recommendations from your shelves.',
  },
];

export default function CuratedPage() {
  const [busy, setBusy] = useState<Job | null>(null);
  const [results, setResults] = useState<Partial<Record<Job, string>>>({});
  const [error, setError] = useState<string | null>(null);

  const run = async (job: Job) => {
    setBusy(job);
    setError(null);
    try {
      const res =
        job === 'japanese'
          ? await getJapaneseOrganizer()
          : job === 'it'
            ? await getItCurator()
            : await getReadingRecommendations();
      setResults((m) => ({ ...m, [job]: JSON.stringify(res, null, 1).slice(0, 6000) }));
    } catch (e) {
      setError(e instanceof Error ? e.message : `${job} failed`);
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2.5 rounded-lg bg-amber/10 border border-amber/20 text-amber">
          <FlaskConical className="w-6 h-6" />
        </div>
        <h1 className="text-3xl font-bold text-slate-100">Curated</h1>
      </div>
      <p className="text-slate-400 mb-6 text-sm">
        Specialized librarian passes backed by <code className="text-xs">manage_specialized</code> —
        previously only reachable via MCP.
      </p>
      {error && <div className="mb-4 p-3 rounded bg-red-500/20 text-red-300 text-sm">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {JOBS.map((j) => (
          <div
            key={j.id}
            className="rounded-xl bg-slate-800/80 border border-slate-700 p-5 flex flex-col"
          >
            <h2 className="text-lg font-bold text-slate-100">{j.title}</h2>
            <p className="text-sm text-slate-400 mt-1 flex-1">{j.blurb}</p>
            <button
              type="button"
              disabled={busy !== null}
              onClick={() => run(j.id)}
              className="mt-4 px-4 py-2 rounded-lg bg-amber text-slate-950 font-bold text-sm hover:bg-amber/90 disabled:opacity-50"
            >
              {busy === j.id ? 'Running…' : 'Run'}
            </button>
            {results[j.id] && (
              <pre className="mt-3 text-xs text-slate-300 whitespace-pre-wrap font-sans max-h-72 overflow-auto rounded bg-slate-900 p-3">
                {results[j.id]}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
