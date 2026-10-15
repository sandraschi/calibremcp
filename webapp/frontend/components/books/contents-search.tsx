'use client';

import { type ContentsSearchHit, searchContents } from '@/common/api';
import { Layers } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

/** "Inside collections" strip: works found within omnibus volumes. Second-class results. */
export function ContentsSearchStrip({ query }: { query: string }) {
  const [hits, setHits] = useState<ContentsSearchHit[] | null>(null);

  useEffect(() => {
    const q = query.trim();
    if (q.length < 3) {
      setHits(null);
      return;
    }
    let cancelled = false;
    searchContents(q, 10)
      .then((res) => {
        if (!cancelled) setHits(res.hits ?? []);
      })
      .catch(() => {
        if (!cancelled) setHits([]);
      });
    return () => {
      cancelled = true;
    };
  }, [query]);

  if (hits === null || hits.length === 0) return null;

  return (
    <div className="mt-6 rounded-lg border border-slate-700 bg-slate-800/40 p-4">
      <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 mb-2">
        <Layers className="w-4 h-4 text-amber" />
        Inside collections
        <span className="text-xs font-normal text-slate-500">
          stories within omnibus volumes — not library books
        </span>
      </h3>
      <ul className="space-y-1.5">
        {hits.map((h, i) => (
          <li key={`${h.book_id}-${i}`} className="text-sm">
            <span className="text-slate-200">“{h.work_title}”</span>
            {h.group && <span className="text-slate-500"> · {h.group}</span>}
            <span className="text-slate-500"> — inside </span>
            <Link
              href={`/search?query=${encodeURIComponent(h.book_title)}`}
              className="text-amber hover:underline"
            >
              {h.book_title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
