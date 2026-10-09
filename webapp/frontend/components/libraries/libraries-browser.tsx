'use client';

import { type Library, type LibraryStats, getLibraryStats, switchLibrary } from '@/common/api';
import {
  ArrowDownWideNarrow,
  ArrowUpNarrowWide,
  BookOpen,
  Check,
  Database,
  HardDrive,
  Layers,
  LayoutGrid,
  List,
  Pencil,
  Search,
  Tags,
  Users,
  X,
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

type ViewMode = 'card' | 'list';
type SortBy = 'name' | 'books' | 'size';

const VIEW_KEY = 'calibre-libraries-view';
const DESC_KEY = 'calibre-library-descriptions';
const PAGE_SIZE = 9;

const SORT_OPTIONS: { value: SortBy; label: string }[] = [
  { value: 'name', label: 'Name' },
  { value: 'books', label: 'Book count' },
  { value: 'size', label: 'Size on disk' },
];

function loadDescriptions(): Record<string, string> {
  try {
    const raw = window.localStorage.getItem(DESC_KEY);
    return raw ? (JSON.parse(raw) as Record<string, string>) : {};
  } catch {
    return {};
  }
}

function formatSize(mb?: number): string {
  if (mb === undefined || mb === null || Number.isNaN(mb)) return '—';
  if (mb >= 1024) return `${(mb / 1024).toFixed(2)} GB`;
  return `${mb.toFixed(mb < 10 ? 2 : 0)} MB`;
}

function bookCountOf(lib: Library, stats?: LibraryStats): number {
  if (stats?.total_books) return stats.total_books;
  return lib.book_count ?? 0;
}

interface LibrariesBrowserProps {
  libraries: Library[];
  currentLibrary?: string;
  onSwitch: (name: string) => void;
}

export function LibrariesBrowser({ libraries, currentLibrary, onSwitch }: LibrariesBrowserProps) {
  const [query, setQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [view, setView] = useState<ViewMode>('card');
  const [page, setPage] = useState(1);
  const [stats, setStats] = useState<Record<string, LibraryStats>>({});
  const [descriptions, setDescriptions] = useState<Record<string, string>>({});
  const [editingPath, setEditingPath] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [switching, setSwitching] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const v = window.localStorage.getItem(VIEW_KEY);
      if (v === 'card' || v === 'list') setView(v);
      setDescriptions(loadDescriptions());
    } catch {
      /* ignore */
    }
  }, []);

  // Per-library detailed stats, fetched in parallel (backend caches 60s).
  useEffect(() => {
    let cancelled = false;
    setStats({});
    if (libraries.length === 0) return;
    Promise.all(
      libraries.map((lib) =>
        getLibraryStats(lib.name)
          .then((s) => ({ name: lib.name, stats: s }))
          .catch(() => null),
      ),
    ).then((results) => {
      if (cancelled) return;
      const next: Record<string, LibraryStats> = {};
      for (const r of results) {
        if (r) next[r.name] = r.stats;
      }
      setStats(next);
    });
    return () => {
      cancelled = true;
    };
  }, [libraries]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const rows = q
      ? libraries.filter(
          (lib) =>
            lib.name.toLowerCase().includes(q) ||
            lib.path.toLowerCase().includes(q) ||
            (descriptions[lib.path] ?? '').toLowerCase().includes(q),
        )
      : [...libraries];
    const dir = sortOrder === 'asc' ? 1 : -1;
    rows.sort((a, b) => {
      if (sortBy === 'books')
        return (bookCountOf(a, stats[a.name]) - bookCountOf(b, stats[b.name])) * dir;
      if (sortBy === 'size') return ((a.size_mb ?? 0) - (b.size_mb ?? 0)) * dir;
      return a.name.localeCompare(b.name) * dir;
    });
    return rows;
  }, [libraries, query, sortBy, sortOrder, stats, descriptions]);

  useEffect(() => {
    setPage(1);
  }, [query, sortBy, sortOrder, libraries.length]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const pageItems = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  const setViewMode = (mode: ViewMode) => {
    setView(mode);
    try {
      window.localStorage.setItem(VIEW_KEY, mode);
    } catch {
      /* ignore */
    }
  };

  const handleSwitch = async (lib: Library) => {
    if (lib.name === currentLibrary || switching) return;
    setError(null);
    setSwitching(lib.name);
    try {
      const res = await switchLibrary(lib.name);
      if (res.success) {
        onSwitch(res.library_name || lib.name);
      } else {
        setError(res.message || 'Failed to switch library');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to switch library');
    } finally {
      setSwitching(null);
    }
  };

  const startEdit = (lib: Library) => {
    setEditingPath(lib.path);
    setEditText(descriptions[lib.path] ?? '');
  };

  const saveDescription = (lib: Library) => {
    const text = editText.trim();
    setDescriptions((prev) => {
      const next = { ...prev };
      if (text) {
        next[lib.path] = text;
      } else {
        delete next[lib.path];
      }
      try {
        window.localStorage.setItem(DESC_KEY, JSON.stringify(next));
      } catch {
        /* ignore */
      }
      return next;
    });
    setEditingPath(null);
  };

  const isActive = (lib: Library) =>
    currentLibrary ? lib.name === currentLibrary : !!lib.is_active;

  const renderDescription = (lib: Library, compact = false) => {
    if (editingPath === lib.path) {
      return (
        <div className="mt-2" onClick={(e) => e.stopPropagation()}>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            rows={compact ? 2 : 3}
            placeholder="What lives in this library? e.g. scifi novels, tech ebooks…"
            className="w-full px-2 py-1.5 text-sm bg-slate-900 border border-amber/50 rounded-md text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
          <div className="mt-1 flex gap-1">
            <button
              type="button"
              onClick={() => saveDescription(lib)}
              className="flex items-center gap-1 px-2 py-1 text-xs rounded bg-amber text-slate-900 font-medium"
            >
              <Check className="w-3 h-3" /> Save
            </button>
            <button
              type="button"
              onClick={() => setEditingPath(null)}
              className="flex items-center gap-1 px-2 py-1 text-xs rounded bg-slate-700 text-slate-300"
            >
              <X className="w-3 h-3" /> Cancel
            </button>
          </div>
        </div>
      );
    }
    const desc = descriptions[lib.path];
    return (
      <div className="mt-2 flex items-start gap-1 group/desc">
        <p className={`flex-1 text-sm ${desc ? 'text-slate-300' : 'text-slate-500 italic'}`}>
          {desc || 'No description yet.'}
        </p>
        <button
          type="button"
          title={desc ? 'Edit description' : 'Add description'}
          onClick={(e) => {
            e.stopPropagation();
            startEdit(lib);
          }}
          className="p-1 rounded text-slate-500 hover:text-amber hover:bg-slate-700/50 opacity-60 hover:opacity-100 transition-opacity"
        >
          <Pencil className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  };

  const renderStats = (lib: Library) => {
    const s = stats[lib.name];
    const cells = [
      {
        icon: BookOpen,
        label: 'Books',
        value: s ? String(s.total_books) : String(lib.book_count ?? '—'),
      },
      { icon: Users, label: 'Authors', value: s ? String(s.total_authors) : '…' },
      { icon: Layers, label: 'Series', value: s ? String(s.total_series) : '…' },
      { icon: Tags, label: 'Tags', value: s ? String(s.total_tags) : '…' },
    ];
    return (
      <div className="mt-3 grid grid-cols-4 gap-2">
        {cells.map(({ icon: Icon, label, value }) => (
          <div
            key={label}
            className="rounded-md bg-slate-900/60 border border-slate-700/60 px-2 py-1.5 text-center"
          >
            <Icon className="w-3.5 h-3.5 mx-auto text-amber/80" />
            <p className="text-sm font-semibold text-slate-200 leading-tight">{value}</p>
            <p className="text-[11px] text-slate-500 leading-tight">{label}</p>
          </div>
        ))}
      </div>
    );
  };

  const renderAction = (lib: Library) => {
    const active = isActive(lib);
    if (active) {
      return (
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 text-xs font-semibold bg-amber text-slate-900 rounded">
            Active
          </span>
          <Link
            href="/books"
            className="px-3 py-1.5 text-xs font-medium rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600"
          >
            Browse
          </Link>
        </div>
      );
    }
    return (
      <button
        type="button"
        disabled={!!switching}
        onClick={() => handleSwitch(lib)}
        className="px-3 py-1.5 text-xs font-medium rounded-md bg-slate-700 border border-slate-600 text-slate-200 hover:border-amber/50 disabled:opacity-50"
      >
        {switching === lib.name ? 'Switching…' : 'Switch'}
      </button>
    );
  };

  return (
    <div data-testid="libraries-browser">
      {/* Toolbar: search + sort + view switch */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <div className="relative flex-1 min-w-52">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="search"
            data-testid="libraries-search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter by name, path, description…"
            className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </div>
        <select
          data-testid="libraries-sort"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortBy)}
          className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber"
          title="Sort libraries"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          data-testid="libraries-sort-order"
          onClick={() => setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'))}
          className="p-2 rounded-md bg-slate-800 border border-slate-600 text-slate-300 hover:border-amber/50"
          title={
            sortOrder === 'asc'
              ? 'Ascending — click for descending'
              : 'Descending — click for ascending'
          }
        >
          {sortOrder === 'asc' ? (
            <ArrowUpNarrowWide className="w-4 h-4" />
          ) : (
            <ArrowDownWideNarrow className="w-4 h-4" />
          )}
        </button>
        <div className="flex gap-1 p-1 rounded-md bg-slate-800 border border-slate-700">
          <button
            type="button"
            data-testid="libraries-view-card"
            onClick={() => setViewMode('card')}
            title="Card view"
            className={`p-1.5 rounded transition-colors ${view === 'card' ? 'bg-amber text-slate-900' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
          <button
            type="button"
            data-testid="libraries-view-list"
            onClick={() => setViewMode('list')}
            title="List view"
            className={`p-1.5 rounded transition-colors ${view === 'list' ? 'bg-amber text-slate-900' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && <div className="mb-4 p-3 rounded bg-red-500/20 text-red-400 text-sm">{error}</div>}

      <p className="mb-3 text-sm text-slate-400">
        Showing <span className="text-slate-200 font-medium">{pageItems.length}</span> of{' '}
        <span className="text-slate-200 font-medium">{filtered.length}</span>{' '}
        {filtered.length === 1 ? 'library' : 'libraries'}
        {query.trim() && (
          <>
            {' '}
            matching <span className="text-amber">“{query.trim()}”</span>
          </>
        )}
      </p>

      {filtered.length === 0 ? (
        <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-8 text-center">
          <Database className="w-8 h-8 mx-auto text-slate-600 mb-2" />
          <p className="text-slate-300 font-medium">No libraries match this filter.</p>
          <button
            type="button"
            onClick={() => setQuery('')}
            className="mt-4 px-4 py-2 text-sm rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600"
          >
            Clear filter
          </button>
        </div>
      ) : view === 'card' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {pageItems.map((lib) => (
            <article
              key={lib.path}
              data-testid={`library-card-${lib.name}`}
              className={`rounded-lg border p-4 transition-colors ${
                isActive(lib)
                  ? 'border-amber bg-amber/5'
                  : 'border-slate-600 bg-slate-800 hover:border-slate-500'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-semibold text-lg text-slate-100 leading-tight break-words">
                  {lib.name}
                </h3>
                {renderAction(lib)}
              </div>
              {renderDescription(lib)}
              {renderStats(lib)}
              <div className="mt-3 pt-3 border-t border-slate-700/60 flex items-center gap-4 text-xs text-slate-500">
                <span className="flex items-center gap-1 min-w-0">
                  <HardDrive className="w-3.5 h-3.5 shrink-0" />
                  {formatSize(lib.size_mb)}
                </span>
                <span className="truncate" title={lib.path}>
                  {lib.path}
                </span>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-slate-600 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-800 text-left text-xs uppercase tracking-wide text-slate-400">
                <th className="px-4 py-3 font-medium">Library</th>
                <th className="px-3 py-3 font-medium text-right">Books</th>
                <th className="px-3 py-3 font-medium text-right hidden sm:table-cell">Authors</th>
                <th className="px-3 py-3 font-medium text-right hidden md:table-cell">Series</th>
                <th className="px-3 py-3 font-medium text-right hidden md:table-cell">Tags</th>
                <th className="px-3 py-3 font-medium text-right hidden lg:table-cell">Size</th>
                <th className="px-4 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {pageItems.map((lib) => {
                const s = stats[lib.name];
                const desc = descriptions[lib.path];
                return (
                  <tr
                    key={lib.path}
                    className={`border-t border-slate-700/60 ${isActive(lib) ? 'bg-amber/5' : 'bg-slate-800/40'}`}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-100">{lib.name}</p>
                      <p className="text-xs text-slate-500 truncate max-w-64" title={lib.path}>
                        {lib.path}
                      </p>
                      {editingPath === lib.path ? (
                        renderDescription(lib, true)
                      ) : desc ? (
                        <p className="text-xs text-slate-400 mt-1 line-clamp-2">{desc}</p>
                      ) : (
                        <button
                          type="button"
                          onClick={() => startEdit(lib)}
                          className="text-xs text-slate-600 hover:text-amber mt-1 italic"
                        >
                          + add description
                        </button>
                      )}
                    </td>
                    <td className="px-3 py-3 text-right text-slate-200 font-medium">
                      {s ? s.total_books : (lib.book_count ?? '—')}
                    </td>
                    <td className="px-3 py-3 text-right text-slate-400 hidden sm:table-cell">
                      {s ? s.total_authors : '…'}
                    </td>
                    <td className="px-3 py-3 text-right text-slate-400 hidden md:table-cell">
                      {s ? s.total_series : '…'}
                    </td>
                    <td className="px-3 py-3 text-right text-slate-400 hidden md:table-cell">
                      {s ? s.total_tags : '…'}
                    </td>
                    <td className="px-3 py-3 text-right text-slate-400 hidden lg:table-cell">
                      {formatSize(lib.size_mb)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="inline-flex justify-end">{renderAction(lib)}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <nav
          className="mt-6 flex items-center justify-center gap-2"
          aria-label="Libraries pagination"
        >
          <button
            type="button"
            disabled={safePage <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="px-4 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 text-slate-300 disabled:opacity-40 hover:border-amber/50"
          >
            Previous
          </button>
          <span className="px-3 py-2 text-sm text-slate-400">
            Page {safePage} of {totalPages}
          </span>
          <button
            type="button"
            disabled={safePage >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            className="px-4 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 text-slate-300 disabled:opacity-40 hover:border-amber/50"
          >
            Next
          </button>
        </nav>
      )}
    </div>
  );
}
