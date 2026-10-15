import Link from 'next/link';

export type TaxonomyView = 'card' | 'list';

export function parseTaxonomyView(raw: string | null | undefined): TaxonomyView {
  return raw === 'list' ? 'list' : 'card';
}

/** Card/List toggle. Pages pass prebuilt hrefs so all existing filters stay intact. */
export function ViewToggle({
  cardHref,
  listHref,
  view,
}: {
  cardHref: string;
  listHref: string;
  view: TaxonomyView;
}) {
  const base = 'px-3 py-1.5 text-sm rounded-md font-medium transition-colors';
  const active = 'bg-amber text-slate-900';
  const idle = 'text-slate-300 hover:text-slate-100';
  return (
    <div
      className="flex items-center gap-1 p-1 rounded-md bg-slate-800 border border-slate-700"
      role="group"
      aria-label="View"
    >
      <Link
        href={cardHref}
        aria-pressed={view === 'card'}
        className={`${base} ${view === 'card' ? active : idle}`}
      >
        Cards
      </Link>
      <Link
        href={listHref}
        aria-pressed={view === 'list'}
        className={`${base} ${view === 'list' ? active : idle}`}
      >
        List
      </Link>
    </div>
  );
}

export interface TaxonomyListItem {
  key: string;
  name: string;
  meta?: string | null;
}

/** Compact row list — the space-efficient alternative to the card grid. */
export function TaxonomyList({
  items,
  getHref,
}: {
  items: TaxonomyListItem[];
  getHref: (item: TaxonomyListItem) => string;
}) {
  return (
    <ul className="divide-y divide-slate-700/60 rounded-lg border border-slate-700 bg-slate-800/40 overflow-hidden">
      {items.map((it) => (
        <li key={it.key}>
          <Link
            href={getHref(it)}
            className="flex items-center justify-between gap-3 px-4 py-2.5 hover:bg-slate-700/60 transition-colors"
          >
            <span className="text-slate-200 text-sm truncate">{it.name}</span>
            {it.meta != null && it.meta !== '' && (
              <span className="text-xs text-slate-500 shrink-0">{it.meta}</span>
            )}
          </Link>
        </li>
      ))}
    </ul>
  );
}
