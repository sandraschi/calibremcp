'use client';

import { type SmartCollection, createSmartCollection, getSmartCollections } from '@/common/api';
import {
  AlertCircle,
  BookmarkCheck,
  CheckCircle2,
  FolderPlus,
  Layers,
  Library,
  Plus,
  RefreshCw,
  Sparkles,
  Tag,
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

const PRESET_TEMPLATES = [
  {
    name: '5-Star Masterpieces',
    description: 'All books rated 5 stars across any genre',
    criteria: { min_rating: 10 },
  },
  {
    name: 'Unread Sci-Fi',
    description: 'Science fiction novels pending in your reading backlog',
    criteria: { tag: 'Science Fiction', unread: true },
  },
  {
    name: 'Epic Series Starters',
    description: 'Volume 1 of any series with index = 1',
    criteria: { series_index: 1 },
  },
  {
    name: 'Quick Reads',
    description: 'Novellas and compact reads under 200 pages',
    criteria: { max_pages: 200 },
  },
];

export default function CollectionsPage() {
  const [collections, setCollections] = useState<SmartCollection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal / Form state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [tagFilter, setTagFilter] = useState('');
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  async function loadCollections() {
    setLoading(true);
    setError(null);
    try {
      const res = await getSmartCollections();
      setCollections(res.collections || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load smart collections');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCollections();
  }, []);

  async function handleCreate(template?: (typeof PRESET_TEMPLATES)[0]) {
    setCreating(true);
    setCreateError(null);
    try {
      const colName = template ? template.name : name;
      const colDesc = template ? template.description : description;
      const criteria = template ? template.criteria : tagFilter ? { tag: tagFilter } : {};

      await createSmartCollection({
        name: colName,
        description: colDesc,
        criteria,
      });

      setShowCreateModal(false);
      setName('');
      setDescription('');
      setTagFilter('');
      await loadCollections();
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create smart collection');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-700/60 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber/10 border border-amber/20 text-amber">
              <BookmarkCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-100">Smart Collections</h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Dynamic, rule-based virtual shelves and automated library groupings
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-amber hover:bg-amber/90 text-slate-950 font-bold rounded-lg text-sm transition-colors shadow"
          >
            <Plus className="w-4 h-4" />
            New Collection
          </button>
          <button
            type="button"
            onClick={loadCollections}
            disabled={loading}
            className="inline-flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded-lg text-sm transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Presets Bar */}
      <div className="p-5 rounded-xl bg-slate-800/50 border border-slate-700/80 space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <Sparkles className="w-4 h-4 text-amber" />
          <span>Quick Add Template Presets</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {PRESET_TEMPLATES.map((tmpl) => (
            <div
              key={tmpl.name}
              className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-700/60 hover:border-amber/50 transition-colors flex flex-col justify-between group"
            >
              <div>
                <h4 className="text-sm font-semibold text-slate-200 group-hover:text-amber transition-colors">
                  {tmpl.name}
                </h4>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">{tmpl.description}</p>
              </div>
              <button
                type="button"
                onClick={() => handleCreate(tmpl)}
                disabled={creating}
                className="mt-3 text-xs font-medium text-amber hover:underline text-left inline-flex items-center gap-1"
              >
                <Plus className="w-3 h-3" />
                Add Shelf
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Active Collections Grid */}
      {loading ? (
        <div className="py-24 text-center space-y-4">
          <div className="w-8 h-8 border-3 border-amber border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-slate-400">Loading smart collections…</p>
        </div>
      ) : collections.length === 0 ? (
        <div className="p-16 rounded-xl bg-slate-800/30 border border-slate-700 text-center space-y-4">
          <Layers className="w-12 h-12 text-slate-500 mx-auto" />
          <h3 className="text-lg font-semibold text-slate-200">No Smart Collections Created Yet</h3>
          <p className="text-sm text-slate-400 max-w-md mx-auto">
            Smart collections dynamically update based on search queries, tags, ratings, and series.
            Create your first shelf using a template above.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {collections.map((col) => (
            <div
              key={col.id}
              className="p-6 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-slate-600 transition-colors flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-lg font-bold text-slate-100 line-clamp-1">{col.name}</h3>
                  <span className="p-1.5 rounded bg-amber/10 text-amber">
                    <BookmarkCheck className="w-4 h-4" />
                  </span>
                </div>
                {col.description && (
                  <p className="text-xs text-slate-400 mt-2 line-clamp-2">{col.description}</p>
                )}
                {col.book_count != null && (
                  <div className="mt-4 flex items-center gap-2 text-xs text-slate-300">
                    <Library className="w-4 h-4 text-slate-500" />
                    <span>{col.book_count} volumes in shelf</span>
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-700/60 flex items-center justify-between">
                <Link
                  href={`/books?tag=${encodeURIComponent(col.name)}`}
                  className="text-xs font-semibold text-amber hover:underline"
                >
                  Browse Books →
                </Link>
                <span className="text-[10px] font-mono text-slate-500">Dynamic Rule</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Collection Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-md p-6 rounded-xl bg-slate-800 border border-slate-700 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-700 pb-3">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <FolderPlus className="w-5 h-5 text-amber" />
                New Smart Collection
              </h3>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-200 text-sm"
              >
                ✕
              </button>
            </div>

            {createError && (
              <div className="p-3 rounded bg-red-950/50 border border-red-800 text-xs text-red-300">
                {createError}
              </div>
            )}

            <div className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Shelf Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Cyberpunk Classics"
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-slate-100 focus:outline-none focus:border-amber"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Description (Optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief summary of what belongs here"
                  rows={2}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-slate-100 focus:outline-none focus:border-amber"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Match by Tag
                </label>
                <input
                  type="text"
                  value={tagFilter}
                  onChange={(e) => setTagFilter(e.target.value)}
                  placeholder="e.g. cyberpunk, sci-fi"
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-slate-100 focus:outline-none focus:border-amber"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-700">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 rounded bg-slate-700 text-slate-300 hover:bg-slate-600 text-xs font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleCreate()}
                disabled={creating || !name.trim()}
                className="px-4 py-2 rounded bg-amber text-slate-950 font-bold hover:bg-amber/90 text-xs disabled:opacity-50"
              >
                {creating ? 'Creating…' : 'Save Collection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
