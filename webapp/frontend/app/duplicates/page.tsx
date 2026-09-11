'use client';

import {
  type Book,
  type DuplicateGroup,
  getBookCoverUrl,
  getBookReaderUrl,
  getDuplicateBooks,
  ratingToFiveStarCount,
} from '@/common/api';
import { AuthorLinks } from '@/components/authors/author-links';
import { BookModal } from '@/components/books/book-modal';
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  CopyCheck,
  ExternalLink,
  Files,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { useEffect, useState } from 'react';

export default function DuplicatesPage() {
  const [groups, setGroups] = useState<DuplicateGroup[]>([]);
  const [totalDuplicates, setTotalDuplicates] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);

  async function loadDuplicates() {
    setLoading(true);
    setError(null);
    try {
      const res = await getDuplicateBooks();
      setGroups(res.duplicate_groups || []);
      setTotalDuplicates(res.total_duplicates || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load duplicate books');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDuplicates();
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-700/60 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber/10 border border-amber/20 text-amber">
              <CopyCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-100">Duplicate Book Manager</h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Detect and resolve duplicate titles, editions, and format collisions
              </p>
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={loadDuplicates}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Re-scan Duplicates
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Metrics Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl bg-slate-800/80 border border-slate-700">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Duplicate Clusters
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100">{groups.length}</span>
            <span className="text-xs text-slate-400">matching groups</span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-800/80 border border-slate-700">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Total Flagged Volumes
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-amber">{totalDuplicates}</span>
            <span className="text-xs text-slate-400">books across all clusters</span>
          </div>
        </div>
      </div>

      {/* List of Groups */}
      {loading ? (
        <div className="py-24 text-center space-y-4">
          <div className="w-8 h-8 border-3 border-amber border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-slate-400">
            Scanning title similarities, author records & ISBN identifiers…
          </p>
        </div>
      ) : groups.length === 0 ? (
        <div className="p-12 rounded-xl bg-slate-800/40 border border-slate-700 text-center space-y-3">
          <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
          <h3 className="text-lg font-semibold text-slate-200">No Duplicate Books Found</h3>
          <p className="text-sm text-slate-400 max-w-md mx-auto">
            Your library catalog has unique records for each title and edition.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {groups.map((group, gIdx) => (
            <div
              key={`group-${gIdx}-${group.title || group.key}`}
              className="p-6 rounded-xl bg-slate-800/70 border border-slate-700 space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-700/60 pb-3">
                <div className="flex items-center gap-2">
                  <Files className="w-5 h-5 text-amber" />
                  <h2 className="text-base font-bold text-slate-100">
                    {group.title || group.key || `Group #${gIdx + 1}`}
                  </h2>
                </div>
                {group.reason && (
                  <span className="text-xs px-2.5 py-1 rounded bg-slate-700 text-slate-300 font-mono">
                    Match: {group.reason}
                  </span>
                )}
              </div>

              {/* Side-by-Side Candidates Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {group.books.map((book) => (
                  <div
                    key={`dup-book-${book.id}`}
                    className="p-4 rounded-lg bg-slate-900/60 border border-slate-700 hover:border-slate-600 transition-colors flex gap-4"
                  >
                    {/* Cover Thumbnail */}
                    <img
                      src={getBookCoverUrl(book.id)}
                      alt={book.title}
                      className="w-16 h-24 object-cover rounded bg-slate-800 shrink-0 cursor-pointer shadow"
                      onClick={() => setSelectedBook(book)}
                    />

                    {/* Details */}
                    <div className="flex-1 min-w-0 flex flex-col justify-between">
                      <div>
                        <h4
                          className="text-sm font-semibold text-slate-200 line-clamp-2 hover:text-amber cursor-pointer"
                          onClick={() => setSelectedBook(book)}
                        >
                          {book.title}
                        </h4>
                        <p className="text-xs text-slate-400 mt-0.5">
                          <AuthorLinks authors={book.authors ?? []} stopPropagation />
                        </p>
                        {book.rating != null && book.rating > 0 && (
                          <span className="text-yellow-500 text-xs">
                            {'⭐'.repeat(ratingToFiveStarCount(book.rating))}
                          </span>
                        )}
                      </div>

                      {/* Action Links */}
                      <div className="mt-2 flex items-center justify-between text-xs pt-2 border-t border-slate-800">
                        <button
                          type="button"
                          onClick={() => setSelectedBook(book)}
                          className="text-slate-300 hover:text-white"
                        >
                          Details
                        </button>
                        <a
                          href={getBookReaderUrl(book.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-amber hover:underline"
                          title="Read in Calibre Content Server"
                        >
                          <BookOpen className="w-3 h-3" />
                          <span>Web Reader</span>
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedBook && <BookModal book={selectedBook} onClose={() => setSelectedBook(null)} />}
    </div>
  );
}
