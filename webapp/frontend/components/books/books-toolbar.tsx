'use client';

import type { BookQueryParams, BookSortBy, SortOrder } from '@/common/api';
import { listAuthors, listPublishers, listSeries, listTags } from '@/common/api';
import {
  ArrowDownWideNarrow,
  ArrowUpNarrowWide,
  ChevronDown,
  RotateCcw,
  SlidersHorizontal,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

export interface BooksFilterValue extends Omit<BookQueryParams, 'limit' | 'offset'> {}

const EMPTY: BooksFilterValue = {};

const SORT_OPTIONS: { value: BookSortBy; label: string }[] = [
  { value: 'title', label: 'Title' },
  { value: 'author', label: 'Author' },
  { value: 'series', label: 'Series' },
  { value: 'rating', label: 'Rating' },
  { value: 'timestamp', label: 'Date added' },
  { value: 'pubdate', label: 'Publish date' },
];

const FORMAT_OPTIONS = ['EPUB', 'PDF', 'MOBI', 'AZW3', 'TXT', 'CBZ', 'CBR', 'FB2', 'DJVU'];

const COLLAPSE_KEY = 'calibre-books-toolbar-collapsed';

function countActive(v: BooksFilterValue): number {
  let n = 0;
  if (v.text?.trim()) n++;
  if (v.title?.trim()) n++;
  if (v.author?.trim()) n++;
  if (v.tag?.trim()) n++;
  if (v.series?.trim()) n++;
  if (v.publisher?.trim()) n++;
  if (v.rating) n++;
  if (v.min_rating) n++;
  if (v.max_rating) n++;
  if (v.unrated) n++;
  if (v.formats?.trim()) n++;
  if (v.pubdate_start) n++;
  if (v.pubdate_end) n++;
  if (v.added_after) n++;
  if (v.added_before) n++;
  if (v.has_publisher !== undefined) n++;
  if (v.sort_by && v.sort_by !== 'title') n++;
  if (v.sort_order && v.sort_order !== 'asc') n++;
  return n;
}

function sortSummary(v: BooksFilterValue): string {
  const opt = SORT_OPTIONS.find((o) => o.value === (v.sort_by ?? 'title'));
  const dir = v.sort_order === 'desc' ? 'desc' : 'asc';
  return `${opt?.label ?? 'Title'} ${dir === 'desc' ? '↓' : '↑'}`;
}

interface BooksToolbarProps {
  value: BooksFilterValue;
  onApply: (next: BooksFilterValue) => void;
  onReset: () => void;
}

const inputCls =
  'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber';
const labelCls = 'block text-xs font-medium text-slate-400 mb-1';

export function BooksToolbar({ value, onApply, onReset }: BooksToolbarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [draft, setDraft] = useState<BooksFilterValue>(value);

  const [authorOpts, setAuthorOpts] = useState<string[]>([]);
  const [tagOpts, setTagOpts] = useState<string[]>([]);
  const [seriesOpts, setSeriesOpts] = useState<string[]>([]);
  const [publisherOpts, setPublisherOpts] = useState<string[]>([]);

  // Restore collapsed state once on mount (localStorage, client only).
  useEffect(() => {
    try {
      setCollapsed(window.localStorage.getItem(COLLAPSE_KEY) === '1');
    } catch {
      /* ignore */
    }
  }, []);

  // Keep draft in sync when URL-driven value changes (deep links, back/forward).
  useEffect(() => {
    setDraft(value);
  }, [value]);

  // Lazy-load suggestion lists only while the panel is open.
  useEffect(() => {
    if (collapsed) return;
    let cancelled = false;
    listAuthors({ limit: 500 })
      .then((r) => {
        if (!cancelled) setAuthorOpts((r.items ?? []).map((a) => a.name).filter(Boolean));
      })
      .catch(() => {});
    listTags({ limit: 500 })
      .then((r) => {
        if (!cancelled) setTagOpts((r.items ?? []).map((t) => t.name).filter(Boolean));
      })
      .catch(() => {});
    listSeries({ limit: 500 })
      .then((r) => {
        if (!cancelled) setSeriesOpts((r.items ?? []).map((s) => s.name).filter(Boolean));
      })
      .catch(() => {});
    listPublishers({ limit: 500 })
      .then((r) => {
        if (!cancelled) setPublisherOpts((r.items ?? []).map((p) => p.name).filter(Boolean));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [collapsed]);

  const activeCount = useMemo(() => countActive(value), [value]);
  const dirty = useMemo(() => JSON.stringify(draft) !== JSON.stringify(value), [draft, value]);

  const toggle = () => {
    setCollapsed((c) => {
      try {
        window.localStorage.setItem(COLLAPSE_KEY, c ? '0' : '1');
      } catch {
        /* ignore */
      }
      return !c;
    });
  };

  const set = <K extends keyof BooksFilterValue>(key: K, val: BooksFilterValue[K]) => {
    setDraft((d) => {
      const next = { ...d };
      if (val === undefined || val === '' || val === null) {
        delete next[key];
      } else {
        next[key] = val;
      }
      return next;
    });
  };

  const handleClear = () => {
    setDraft(EMPTY);
    onReset();
  };

  const sortBy: BookSortBy = draft.sort_by ?? 'title';
  const sortOrder: SortOrder = draft.sort_order ?? 'asc';

  return (
    <section
      data-testid="books-toolbar"
      className="mb-6 rounded-lg bg-slate-800/60 border border-slate-700 overflow-hidden"
    >
      <div className="flex flex-wrap items-center gap-2 px-4 py-3">
        <button
          type="button"
          data-testid="books-toolbar-toggle"
          onClick={toggle}
          aria-expanded={!collapsed}
          className="flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-600 hover:border-amber/50 text-slate-200 transition-colors"
        >
          <SlidersHorizontal className="w-4 h-4 text-amber" />
          {collapsed ? 'Show filters & sort' : 'Hide filters & sort'}
          <ChevronDown
            className={`w-4 h-4 text-slate-400 transition-transform ${collapsed ? '' : 'rotate-180'}`}
          />
        </button>

        {activeCount > 0 && (
          <span
            data-testid="books-toolbar-active-count"
            className="px-2 py-1 text-xs font-semibold rounded-full bg-amber text-slate-900"
            title={`${activeCount} active filter${activeCount === 1 ? '' : 's'}`}
          >
            {activeCount} active
          </span>
        )}

        {collapsed && (
          <span className="text-xs text-slate-400" data-testid="books-toolbar-sort-summary">
            Sorted by {sortSummary(value)}
          </span>
        )}

        <div className="ml-auto flex items-center gap-2">
          {(activeCount > 0 || dirty) && (
            <button
              type="button"
              data-testid="books-toolbar-clear"
              onClick={handleClear}
              className="flex items-center gap-1 px-3 py-2 text-sm rounded-md bg-slate-800 border border-slate-600 hover:border-amber/50 text-slate-300 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Clear all
            </button>
          )}
        </div>
      </div>

      {!collapsed && (
        <div className="px-4 pb-4 pt-1 border-t border-slate-700/60">
          {/* Sorting row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
            <div>
              <label htmlFor="books-sort-by" className={labelCls}>
                Sort by
              </label>
              <select
                id="books-sort-by"
                data-testid="books-sort-by"
                value={sortBy}
                onChange={(e) => set('sort_by', e.target.value as BookSortBy)}
                className={inputCls}
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="books-sort-order" className={labelCls}>
                Order
              </label>
              <button
                type="button"
                id="books-sort-order"
                data-testid="books-sort-order"
                onClick={() => set('sort_order', sortOrder === 'asc' ? 'desc' : 'asc')}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 text-sm hover:border-amber/50 transition-colors"
                title={
                  sortOrder === 'asc'
                    ? 'Ascending — click for descending'
                    : 'Descending — click for ascending'
                }
              >
                {sortOrder === 'asc' ? (
                  <>
                    <ArrowUpNarrowWide className="w-4 h-4 text-amber" /> Ascending
                  </>
                ) : (
                  <>
                    <ArrowDownWideNarrow className="w-4 h-4 text-amber" /> Descending
                  </>
                )}
              </button>
            </div>
            <div>
              <label htmlFor="books-format" className={labelCls}>
                Format
              </label>
              <select
                id="books-format"
                data-testid="books-format"
                value={draft.formats ?? ''}
                onChange={(e) => set('formats', e.target.value || undefined)}
                className={inputCls}
              >
                <option value="">Any format</option>
                {FORMAT_OPTIONS.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Text filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-3">
            <div>
              <label htmlFor="books-text" className={labelCls}>
                Search text
              </label>
              <input
                id="books-text"
                data-testid="books-text"
                type="search"
                value={draft.text ?? ''}
                onChange={(e) => set('text', e.target.value || undefined)}
                placeholder="Anywhere: title, author, tags…"
                className={inputCls}
              />
            </div>
            <div>
              <label htmlFor="books-title" className={labelCls}>
                Title
              </label>
              <input
                id="books-title"
                data-testid="books-title"
                type="search"
                value={draft.title ?? ''}
                onChange={(e) => set('title', e.target.value || undefined)}
                placeholder="Title contains…"
                className={inputCls}
              />
            </div>
            <div>
              <label htmlFor="books-author" className={labelCls}>
                Author
              </label>
              <input
                id="books-author"
                data-testid="books-author"
                type="search"
                list="books-author-opts"
                value={draft.author ?? ''}
                onChange={(e) => set('author', e.target.value || undefined)}
                placeholder="Author name…"
                className={inputCls}
              />
              <datalist id="books-author-opts">
                {authorOpts.map((a) => (
                  <option key={a} value={a} />
                ))}
              </datalist>
            </div>
            <div>
              <label htmlFor="books-tag" className={labelCls}>
                Tag
              </label>
              <input
                id="books-tag"
                data-testid="books-tag"
                type="search"
                list="books-tag-opts"
                value={draft.tag ?? ''}
                onChange={(e) => set('tag', e.target.value || undefined)}
                placeholder="Tag…"
                className={inputCls}
              />
              <datalist id="books-tag-opts">
                {tagOpts.map((t) => (
                  <option key={t} value={t} />
                ))}
              </datalist>
            </div>
            <div>
              <label htmlFor="books-series" className={labelCls}>
                Series
              </label>
              <input
                id="books-series"
                data-testid="books-series"
                type="search"
                list="books-series-opts"
                value={draft.series ?? ''}
                onChange={(e) => set('series', e.target.value || undefined)}
                placeholder="Series name…"
                className={inputCls}
              />
              <datalist id="books-series-opts">
                {seriesOpts.map((s) => (
                  <option key={s} value={s} />
                ))}
              </datalist>
            </div>
            <div>
              <label htmlFor="books-publisher" className={labelCls}>
                Publisher
              </label>
              <input
                id="books-publisher"
                data-testid="books-publisher"
                type="search"
                list="books-publisher-opts"
                value={draft.publisher ?? ''}
                onChange={(e) => set('publisher', e.target.value || undefined)}
                placeholder="Publisher…"
                className={inputCls}
              />
              <datalist id="books-publisher-opts">
                {publisherOpts.map((p) => (
                  <option key={p} value={p} />
                ))}
              </datalist>
            </div>
          </div>

          {/* Rating */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 mt-3">
            <div>
              <label htmlFor="books-min-rating" className={labelCls}>
                Min rating
              </label>
              <select
                id="books-min-rating"
                data-testid="books-min-rating"
                value={draft.min_rating?.toString() ?? ''}
                onChange={(e) =>
                  set('min_rating', e.target.value ? Number(e.target.value) : undefined)
                }
                className={inputCls}
              >
                <option value="">Any</option>
                <option value="5">5 stars</option>
                <option value="4">4+ stars</option>
                <option value="3">3+ stars</option>
                <option value="2">2+ stars</option>
                <option value="1">1+ stars</option>
              </select>
            </div>
            <div>
              <label htmlFor="books-max-rating" className={labelCls}>
                Max rating
              </label>
              <select
                id="books-max-rating"
                data-testid="books-max-rating"
                value={draft.max_rating?.toString() ?? ''}
                onChange={(e) =>
                  set('max_rating', e.target.value ? Number(e.target.value) : undefined)
                }
                className={inputCls}
              >
                <option value="">Any</option>
                <option value="1">1 star</option>
                <option value="2">up to 2</option>
                <option value="3">up to 3</option>
                <option value="4">up to 4</option>
                <option value="5">up to 5</option>
              </select>
            </div>
            <div>
              <label htmlFor="books-rating" className={labelCls}>
                Exact rating
              </label>
              <select
                id="books-rating"
                data-testid="books-rating"
                value={draft.rating?.toString() ?? ''}
                onChange={(e) => set('rating', e.target.value ? Number(e.target.value) : undefined)}
                className={inputCls}
              >
                <option value="">Any</option>
                <option value="5">5 stars</option>
                <option value="4">4 stars</option>
                <option value="3">3 stars</option>
                <option value="2">2 stars</option>
                <option value="1">1 star</option>
              </select>
            </div>
            <div className="flex items-end gap-4 pb-2">
              <label className="flex items-center gap-2 cursor-pointer text-slate-300 text-sm">
                <input
                  type="checkbox"
                  data-testid="books-unrated"
                  checked={Boolean(draft.unrated)}
                  onChange={(e) => set('unrated', e.target.checked || undefined)}
                  className="rounded bg-slate-700 border-slate-600 text-amber focus:ring-amber"
                />
                Unrated only
              </label>
            </div>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-3">
            <div>
              <label htmlFor="books-pubdate-start" className={labelCls}>
                Published after
              </label>
              <input
                id="books-pubdate-start"
                data-testid="books-pubdate-start"
                type="date"
                value={draft.pubdate_start ?? ''}
                onChange={(e) => set('pubdate_start', e.target.value || undefined)}
                className={`${inputCls} [color-scheme:dark]`}
              />
            </div>
            <div>
              <label htmlFor="books-pubdate-end" className={labelCls}>
                Published before
              </label>
              <input
                id="books-pubdate-end"
                data-testid="books-pubdate-end"
                type="date"
                value={draft.pubdate_end ?? ''}
                onChange={(e) => set('pubdate_end', e.target.value || undefined)}
                className={`${inputCls} [color-scheme:dark]`}
              />
            </div>
            <div>
              <label htmlFor="books-added-after" className={labelCls}>
                Added after
              </label>
              <input
                id="books-added-after"
                data-testid="books-added-after"
                type="date"
                value={draft.added_after ?? ''}
                onChange={(e) => set('added_after', e.target.value || undefined)}
                className={`${inputCls} [color-scheme:dark]`}
              />
            </div>
            <div>
              <label htmlFor="books-added-before" className={labelCls}>
                Added before
              </label>
              <input
                id="books-added-before"
                data-testid="books-added-before"
                type="date"
                value={draft.added_before ?? ''}
                onChange={(e) => set('added_before', e.target.value || undefined)}
                className={`${inputCls} [color-scheme:dark]`}
              />
            </div>
          </div>

          {/* Publisher presence + actions */}
          <div className="flex flex-wrap items-end gap-3 mt-3">
            <div className="w-full sm:w-56">
              <label htmlFor="books-has-publisher" className={labelCls}>
                Publisher set?
              </label>
              <select
                id="books-has-publisher"
                data-testid="books-has-publisher"
                value={draft.has_publisher === undefined ? '' : draft.has_publisher ? 'yes' : 'no'}
                onChange={(e) =>
                  set('has_publisher', e.target.value === '' ? undefined : e.target.value === 'yes')
                }
                className={inputCls}
              >
                <option value="">Either</option>
                <option value="yes">Has publisher</option>
                <option value="no">No publisher</option>
              </select>
            </div>
            <div className="ml-auto flex gap-2">
              <button
                type="button"
                data-testid="books-apply"
                disabled={!dirty}
                onClick={() => onApply(draft)}
                className="px-4 py-2 bg-amber text-slate-900 rounded-md hover:bg-amber/90 font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Apply
              </button>
              <button
                type="button"
                data-testid="books-reset"
                onClick={handleClear}
                className="px-4 py-2 bg-slate-700 text-slate-200 rounded-md hover:bg-slate-600 text-sm"
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
