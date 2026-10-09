'use client';

import {
  createTag,
  deleteTag,
  deleteUnusedTags,
  findDuplicateTags,
  getTagStatistics,
  getUnusedTags,
  listTags,
  mergeTags,
  organizeTags,
  renameTag,
} from '@/common/api';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useCallback, useEffect, useState } from 'react';

interface TagRow {
  id: number;
  name: string;
  book_count?: number;
}

function renderValue(v: unknown): string {
  if (v === null || v === undefined) return '—';
  if (typeof v === 'object') return JSON.stringify(v, null, 1).slice(0, 2000);
  return String(v);
}

function TagsPageInner() {
  const searchParams = useSearchParams();
  const search = searchParams?.get('search') ?? undefined;
  const page = Math.max(1, Number.parseInt(searchParams?.get('page') ?? '1', 10));
  const sortBy = searchParams?.get('sort_by') === 'book_count' ? 'book_count' : 'name';
  const sortOrder = searchParams?.get('sort_order') === 'desc' ? 'desc' : 'asc';
  const unusedOnly = searchParams?.get('unused_only') === '1';
  const limit = 50;
  const offset = (page - 1) * limit;

  const [data, setData] = useState<{ items: TagRow[]; total: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [toolsOpen, setToolsOpen] = useState(false);
  const [toolBusy, setToolBusy] = useState<string | null>(null);
  const [toolResult, setToolResult] = useState<{ title: string; body: string } | null>(null);
  const [toolError, setToolError] = useState<string | null>(null);

  // Tool form state
  const [newName, setNewName] = useState('');
  const [renameId, setRenameId] = useState('');
  const [renameTo, setRenameTo] = useState('');
  const [deleteId, setDeleteId] = useState('');
  const [deleteForce, setDeleteForce] = useState(false);
  const [mergeSources, setMergeSources] = useState('');
  const [mergeTarget, setMergeTarget] = useState('');
  const [dupThreshold, setDupThreshold] = useState('0.8');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listTags({
        search,
        limit,
        offset,
        sort_by: sortBy,
        sort_order: sortOrder,
        unused_only: unusedOnly || undefined,
      });
      setData({ items: res.items as TagRow[], total: res.total });
    } catch (e) {
      setError(String((e as Error).message));
    } finally {
      setLoading(false);
    }
  }, [search, limit, offset, sortBy, sortOrder, unusedOnly]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await listTags({
          search,
          limit,
          offset,
          sort_by: sortBy,
          sort_order: sortOrder,
          unused_only: unusedOnly || undefined,
        });
        if (!cancelled) setData({ items: res.items as TagRow[], total: res.total });
      } catch (e) {
        if (!cancelled) setError(String((e as Error).message));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [search, limit, offset, sortBy, sortOrder, unusedOnly]);

  const runTool = async (title: string, fn: () => Promise<unknown>) => {
    setToolBusy(title);
    setToolError(null);
    setToolResult(null);
    try {
      const res = await fn();
      setToolResult({ title, body: renderValue(res) });
      await load();
    } catch (e) {
      setToolError(e instanceof Error ? e.message : `${title} failed`);
    } finally {
      setToolBusy(null);
    }
  };

  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / limit);
  const hasPrev = page > 1;
  const hasNext = page < totalPages;

  const pageHref = (p: number) => {
    const sp = new URLSearchParams();
    if (p > 1) sp.set('page', String(p));
    if (search) sp.set('search', search);
    if (sortBy !== 'name') sp.set('sort_by', sortBy);
    if (sortOrder !== 'asc') sp.set('sort_order', sortOrder);
    if (unusedOnly) sp.set('unused_only', '1');
    const q = sp.toString();
    return q ? `/tags?${q}` : '/tags';
  };

  const inputCls =
    'px-3 py-1.5 bg-slate-700 border border-slate-600 rounded-md text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber';
  const btnCls =
    'px-3 py-1.5 text-sm rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600 disabled:opacity-50';

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Tags</h1>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <form className="flex-1 min-w-52" action="/tags" method="get">
          {sortBy !== 'name' && <input type="hidden" name="sort_by" value={sortBy} />}
          {sortOrder !== 'asc' && <input type="hidden" name="sort_order" value={sortOrder} />}
          {unusedOnly && <input type="hidden" name="unused_only" value="1" />}
          <input
            type="search"
            name="search"
            defaultValue={search}
            placeholder="Search tags..."
            className="w-full max-w-md px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </form>
        <form action="/tags" method="get" className="flex items-center gap-2">
          {search && <input type="hidden" name="search" value={search} />}
          {unusedOnly && <input type="hidden" name="unused_only" value="1" />}
          <select name="sort_by" defaultValue={sortBy} className={inputCls} title="Sort by">
            <option value="name">Name</option>
            <option value="book_count">Book count</option>
          </select>
          <select name="sort_order" defaultValue={sortOrder} className={inputCls} title="Order">
            <option value="asc">Asc</option>
            <option value="desc">Desc</option>
          </select>
          <button type="submit" className={btnCls}>
            Sort
          </button>
        </form>
        <Link
          href={
            unusedOnly
              ? pageHref(1)
              : `/tags?unused_only=1${search ? `&search=${encodeURIComponent(search)}` : ''}`
          }
          className={`px-3 py-1.5 text-sm rounded-md border ${
            unusedOnly
              ? 'bg-amber text-slate-900 border-amber font-medium'
              : 'bg-slate-800 border-slate-600 text-slate-300 hover:border-amber/50'
          }`}
        >
          Unused only
        </Link>
        <button
          type="button"
          onClick={() => setToolsOpen((o) => !o)}
          aria-expanded={toolsOpen}
          className="px-3 py-1.5 text-sm rounded-md bg-slate-800 border border-slate-600 text-slate-200 hover:border-amber/50"
        >
          {toolsOpen ? 'Hide tag tools' : 'Tag tools'}
        </button>
      </div>

      {toolsOpen && (
        <section
          data-testid="tag-tools"
          className="mb-6 rounded-lg bg-slate-800/60 border border-slate-700 p-4 grid grid-cols-1 lg:grid-cols-2 gap-4"
        >
          <div className="rounded-md bg-slate-900/50 border border-slate-700/60 p-3">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Create tag</h3>
            <div className="flex gap-2">
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="New tag name"
                className={`${inputCls} flex-1`}
              />
              <button
                type="button"
                disabled={toolBusy !== null || !newName.trim()}
                onClick={() =>
                  runTool('Create tag', () => createTag(newName.trim()).then(() => setNewName('')))
                }
                className={btnCls}
              >
                Create
              </button>
            </div>
          </div>
          <div className="rounded-md bg-slate-900/50 border border-slate-700/60 p-3">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Rename tag</h3>
            <div className="flex gap-2">
              <input
                value={renameId}
                onChange={(e) => setRenameId(e.target.value)}
                placeholder="Tag ID"
                className={`${inputCls} w-24`}
              />
              <input
                value={renameTo}
                onChange={(e) => setRenameTo(e.target.value)}
                placeholder="New name"
                className={`${inputCls} flex-1`}
              />
              <button
                type="button"
                disabled={toolBusy !== null || !renameId || !renameTo.trim()}
                onClick={() =>
                  runTool('Rename tag', () => renameTag(Number(renameId), renameTo.trim()))
                }
                className={btnCls}
              >
                Rename
              </button>
            </div>
          </div>
          <div className="rounded-md bg-slate-900/50 border border-slate-700/60 p-3">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Delete tag</h3>
            <div className="flex flex-wrap items-center gap-2">
              <input
                value={deleteId}
                onChange={(e) => setDeleteId(e.target.value)}
                placeholder="Tag ID"
                className={`${inputCls} w-24`}
              />
              <label className="flex items-center gap-1 text-xs text-slate-400">
                <input
                  type="checkbox"
                  checked={deleteForce}
                  onChange={(e) => setDeleteForce(e.target.checked)}
                  className="rounded bg-slate-700 border-slate-600"
                />
                force
              </label>
              <button
                type="button"
                disabled={toolBusy !== null || !deleteId}
                onClick={() =>
                  runTool('Delete tag', () => deleteTag(Number(deleteId), deleteForce))
                }
                className="px-3 py-1.5 text-sm rounded-md bg-red-900/60 text-red-200 hover:bg-red-900 disabled:opacity-50"
              >
                Delete
              </button>
            </div>
          </div>
          <div className="rounded-md bg-slate-900/50 border border-slate-700/60 p-3">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Merge tags</h3>
            <div className="flex gap-2">
              <input
                value={mergeSources}
                onChange={(e) => setMergeSources(e.target.value)}
                placeholder="Source IDs: 3, 7"
                className={`${inputCls} flex-1`}
              />
              <input
                value={mergeTarget}
                onChange={(e) => setMergeTarget(e.target.value)}
                placeholder="Target ID"
                className={`${inputCls} w-24`}
              />
              <button
                type="button"
                disabled={toolBusy !== null || !mergeSources || !mergeTarget}
                onClick={() =>
                  runTool('Merge tags', () =>
                    mergeTags(
                      mergeSources
                        .split(',')
                        .map((s) => Number(s.trim()))
                        .filter(Boolean),
                      Number(mergeTarget),
                    ),
                  )
                }
                className={btnCls}
              >
                Merge
              </button>
            </div>
          </div>
          <div className="rounded-md bg-slate-900/50 border border-slate-700/60 p-3 lg:col-span-2">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Cleanup & analysis</h3>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={toolBusy !== null}
                onClick={() => runTool('Tag statistics', getTagStatistics)}
                className={btnCls}
              >
                Statistics
              </button>
              <div className="flex items-center gap-1">
                <input
                  value={dupThreshold}
                  onChange={(e) => setDupThreshold(e.target.value)}
                  placeholder="0.8"
                  className={`${inputCls} w-16`}
                  title="Similarity threshold 0-1"
                />
                <button
                  type="button"
                  disabled={toolBusy !== null}
                  onClick={() =>
                    runTool('Duplicate tags', () => findDuplicateTags(Number(dupThreshold) || 0.8))
                  }
                  className={btnCls}
                >
                  Find duplicates
                </button>
              </div>
              <button
                type="button"
                disabled={toolBusy !== null}
                onClick={() => runTool('Unused tags', getUnusedTags)}
                className={btnCls}
              >
                List unused
              </button>
              <button
                type="button"
                disabled={toolBusy !== null}
                onClick={() => {
                  if (window.confirm('Delete ALL unused tags?'))
                    runTool('Delete unused tags', deleteUnusedTags);
                }}
                className="px-3 py-1.5 text-sm rounded-md bg-red-900/60 text-red-200 hover:bg-red-900 disabled:opacity-50"
              >
                Delete all unused
              </button>
              <button
                type="button"
                disabled={toolBusy !== null}
                onClick={() => runTool('Organize tags (AI suggestions)', organizeTags)}
                className={btnCls}
              >
                AI organize
              </button>
            </div>
          </div>
          <div className="lg:col-span-2">
            {toolBusy && <p className="text-sm text-slate-400">{toolBusy}…</p>}
            {toolError && <p className="text-sm text-red-400">{toolError}</p>}
            {toolResult && (
              <div className="rounded-md bg-slate-900 border border-slate-700 p-3">
                <p className="text-xs font-semibold text-amber mb-1">{toolResult.title}</p>
                <pre className="text-xs text-slate-300 whitespace-pre-wrap font-sans max-h-64 overflow-auto">
                  {toolResult.body}
                </pre>
              </div>
            )}
          </div>
        </section>
      )}

      {loading ? (
        <p className="text-slate-400">Loading tags…</p>
      ) : error || !data ? (
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load tags</p>
          <p className="mt-2 text-sm text-slate-400">{error ?? 'Unknown error'}</p>
        </div>
      ) : (
        <>
          <p className="mb-3 text-sm text-slate-400">
            {total} tag{total === 1 ? '' : 's'} — click a card to browse its books (IDs shown for
            rename / delete / merge).
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {data.items.map((t) => (
              <Link
                key={t.id}
                href={`/books?tag=${encodeURIComponent(t.name)}`}
                className="block p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 hover:bg-slate-700 transition-colors"
              >
                <span className="text-slate-200 font-medium">{t.name}</span>
                <span className="block text-xs text-slate-500 mt-1">
                  ID {t.id}
                  {t.book_count != null && ` · ${t.book_count} books`}
                </span>
              </Link>
            ))}
          </div>
          {total > limit && (
            <nav
              className="mt-6 flex flex-wrap items-center justify-center gap-2"
              aria-label="Pagination"
            >
              <p className="w-full text-center text-sm text-slate-400 mb-2">
                Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
              </p>
              <div className="flex items-center gap-2">
                {hasPrev ? (
                  <Link
                    href={pageHref(page - 1)}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
                  >
                    Previous
                  </Link>
                ) : (
                  <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">
                    Previous
                  </span>
                )}
                {hasNext ? (
                  <Link
                    href={pageHref(page + 1)}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
                  >
                    Next
                  </Link>
                ) : (
                  <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Next</span>
                )}
              </div>
            </nav>
          )}
        </>
      )}
    </div>
  );
}

export default function TagsPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <TagsPageInner />
    </Suspense>
  );
}
