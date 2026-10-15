'use client';

import { type ContentsResult, getBookContents } from '@/common/api';
import { Layers } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

/** Contained-works browser for omnibus/collection ebooks. Renders nothing for normal books. */
export function CollectionWorks({ bookId }: { bookId: number }) {
  const [data, setData] = useState<ContentsResult | null>(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    let cancelled = false;
    setData(null);
    getBookContents(bookId)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch(() => {
        if (!cancelled) setData(null);
      });
    return () => {
      cancelled = true;
    };
  }, [bookId]);

  const rows = useMemo(() => {
    const works = data?.works ?? [];
    const q = filter.trim().toLowerCase();
    if (!q) return works;
    return works.filter((w) => w.title.toLowerCase().includes(q));
  }, [data, filter]);

  if (!data || !data.success || !data.is_collection || !data.works?.length) return null;

  return (
    <div className="border-t border-slate-700/60 px-8 py-6 bg-slate-900/20">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
          <Layers className="w-4 h-4 text-amber" />
          Contained works
          <span className="text-xs font-normal text-slate-500">
            {data.work_count} in this volume · from TOC, not library books
          </span>
        </h3>
        <input
          type="search"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter works…"
          className="px-3 py-1.5 text-sm rounded-md bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
        />
      </div>
      <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-6 max-h-72 overflow-auto pr-1">
        {rows.map((w, i) =>
          w.is_group ? (
            <li
              key={`g-${i}`}
              className="md:col-span-2 text-xs font-semibold uppercase tracking-wide text-amber mt-3 first:mt-0"
            >
              {w.title}
            </li>
          ) : (
            <li
              key={`w-${i}`}
              className="text-sm text-slate-300 py-1 border-b border-slate-800 truncate"
              title={w.group ? `${w.group} — ${w.title}` : w.title}
            >
              {w.title}
              {w.group && <span className="text-slate-600"> · {w.group}</span>}
            </li>
          ),
        )}
      </ul>
      {filter.trim() && rows.length === 0 && (
        <p className="text-sm text-slate-500 mt-2">No works match “{filter.trim()}”.</p>
      )}
    </div>
  );
}
