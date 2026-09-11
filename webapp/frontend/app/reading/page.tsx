'use client';

import {
  type Book,
  type PrioritizedBook,
  type ReadingStatisticsResult,
  type UnreadPriorityResult,
  getBookCoverUrl,
  getBookReaderUrl,
  getReadingStatistics,
  getUnreadPriority,
  ratingToFiveStarCount,
} from '@/common/api';
import { AuthorLinks } from '@/components/authors/author-links';
import { BookModal } from '@/components/books/book-modal';
import {
  AlertCircle,
  BookCheck,
  BookOpen,
  CheckCircle2,
  Clock,
  Flame,
  ListOrdered,
  PieChart,
  RefreshCw,
  Sparkles,
  Star,
  TrendingUp,
} from 'lucide-react';
import { useEffect, useState } from 'react';

export default function ReadingPage() {
  const [activeTab, setActiveTab] = useState<'priorities' | 'stats'>('priorities');

  // Priority state
  const [priorityData, setPriorityData] = useState<UnreadPriorityResult | null>(null);
  const [priorityLoading, setPriorityLoading] = useState(true);
  const [priorityError, setPriorityError] = useState<string | null>(null);

  // Stats state
  const [statsData, setStatsData] = useState<ReadingStatisticsResult | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState<string | null>(null);

  // Modal
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);

  async function loadPriorities() {
    setPriorityLoading(true);
    setPriorityError(null);
    try {
      const res = await getUnreadPriority();
      setPriorityData(res);
    } catch (err) {
      setPriorityError(err instanceof Error ? err.message : 'Failed to load unread priority list');
    } finally {
      setPriorityLoading(false);
    }
  }

  async function loadStats() {
    setStatsLoading(true);
    setStatsError(null);
    try {
      const res = await getReadingStatistics();
      setStatsData(res);
    } catch (err) {
      setStatsError(err instanceof Error ? err.message : 'Failed to load reading statistics');
    } finally {
      setStatsLoading(false);
    }
  }

  useEffect(() => {
    loadPriorities();
  }, []);

  useEffect(() => {
    if (activeTab === 'stats' && !statsData && !statsLoading) {
      loadStats();
    }
  }, [activeTab, statsData, statsLoading]);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-700/60 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber/10 border border-amber/20 text-amber">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-100">Reading Queue & Analytics</h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Smart unread book recommendations, reading velocity & library trends
              </p>
            </div>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center bg-slate-800 p-1 rounded-lg border border-slate-700">
          <button
            type="button"
            onClick={() => setActiveTab('priorities')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'priorities'
                ? 'bg-amber text-slate-950 shadow font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ListOrdered className="w-4 h-4" />
            Unread Priorities
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('stats')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'stats'
                ? 'bg-amber text-slate-950 shadow font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <PieChart className="w-4 h-4" />
            Reading Analytics
          </button>
        </div>
      </div>

      {/* Tab 1: Unread Priority Queue */}
      {activeTab === 'priorities' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Sparkles className="w-4 h-4 text-amber" />
              <span>Prioritized by ratings, series continuation, and author weight</span>
            </div>
            <button
              type="button"
              onClick={loadPriorities}
              disabled={priorityLoading}
              className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 rounded text-xs font-medium transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${priorityLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {priorityError && (
            <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span className="text-sm">{priorityError}</span>
            </div>
          )}

          {priorityLoading ? (
            <div className="py-20 text-center space-y-3">
              <div className="w-8 h-8 border-3 border-amber border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-slate-400">
                Calculating reading priorities across unread volumes…
              </p>
            </div>
          ) : priorityData?.prioritized_books.length === 0 ? (
            <div className="p-12 rounded-xl bg-slate-800/40 border border-slate-700 text-center space-y-3">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <h3 className="text-lg font-semibold text-slate-200">All Caught Up!</h3>
              <p className="text-sm text-slate-400 max-w-md mx-auto">
                No pending books identified in your unread queue.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {priorityData?.prioritized_books.map((book, index) => {
                const reason = book.reason || priorityData.priority_reasons?.[String(book.id)];
                return (
                  <div
                    key={`prio-book-${book.id}`}
                    className="p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-slate-600 transition-colors flex items-center justify-between gap-4"
                  >
                    <div className="flex items-center gap-4 min-w-0">
                      {/* Rank Number */}
                      <span className="w-7 text-center font-mono font-bold text-base text-slate-500">
                        #{index + 1}
                      </span>

                      {/* Cover */}
                      <img
                        src={getBookCoverUrl(book.id)}
                        alt={book.title}
                        className="w-12 h-16 object-cover rounded bg-slate-900 shrink-0 cursor-pointer shadow"
                        onClick={() => setSelectedBook(book as Book)}
                      />

                      {/* Info */}
                      <div className="min-w-0">
                        <h3
                          className="text-base font-semibold text-slate-100 hover:text-amber cursor-pointer truncate"
                          onClick={() => setSelectedBook(book as Book)}
                        >
                          {book.title}
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">
                          <AuthorLinks authors={book.authors ?? []} stopPropagation />
                        </p>
                        <div className="mt-1 flex items-center gap-2">
                          {book.rating != null && book.rating > 0 && (
                            <span className="text-yellow-500 text-xs">
                              {'⭐'.repeat(ratingToFiveStarCount(book.rating))}
                            </span>
                          )}
                          {reason && (
                            <span className="text-[10px] font-medium uppercase px-2 py-0.5 rounded bg-amber/15 text-amber border border-amber/30">
                              {reason}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Action Links */}
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={() => setSelectedBook(book as Book)}
                        className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded text-xs font-medium transition-colors"
                      >
                        Details
                      </button>
                      <a
                        href={getBookReaderUrl(book.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber text-slate-950 font-semibold rounded text-xs hover:bg-amber/90 transition-colors shadow"
                        title="Open in Calibre Content Server Web Reader (:8099)"
                      >
                        <BookOpen className="w-3.5 h-3.5" />
                        <span>Read Web</span>
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Reading Analytics */}
      {activeTab === 'stats' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-400">
              Library consumption overview and reading habits
            </span>
            <button
              type="button"
              onClick={loadStats}
              disabled={statsLoading}
              className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 rounded text-xs font-medium transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${statsLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {statsError && (
            <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 text-red-300 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span className="text-sm">{statsError}</span>
            </div>
          )}

          {statsLoading ? (
            <div className="py-20 text-center space-y-3">
              <div className="w-8 h-8 border-3 border-amber border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-slate-400">
                Compiling reading statistics and rating trends…
              </p>
            </div>
          ) : statsData ? (
            <div className="space-y-6">
              {/* Top Metrics Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700">
                  <div className="flex items-center justify-between text-slate-400 text-sm">
                    <span>Books Completed</span>
                    <BookCheck className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div className="mt-3">
                    <span className="text-4xl font-extrabold text-slate-100">
                      {statsData.total_books_read}
                    </span>
                    <span className="text-xs text-slate-400 ml-2">read</span>
                  </div>
                </div>

                <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700">
                  <div className="flex items-center justify-between text-slate-400 text-sm">
                    <span>Average Rating</span>
                    <Star className="w-5 h-5 text-amber" />
                  </div>
                  <div className="mt-3">
                    <span className="text-4xl font-extrabold text-amber">
                      {statsData.average_rating ? statsData.average_rating.toFixed(1) : 'N/A'}
                    </span>
                    <span className="text-xs text-slate-400 ml-2">/ 10 stars</span>
                  </div>
                </div>

                <div className="p-6 rounded-xl bg-slate-800/80 border border-slate-700">
                  <div className="flex items-center justify-between text-slate-400 text-sm">
                    <span>Top Genres Count</span>
                    <Flame className="w-5 h-5 text-rose-400" />
                  </div>
                  <div className="mt-3">
                    <span className="text-4xl font-extrabold text-slate-100">
                      {statsData.favorite_genres?.length || 0}
                    </span>
                    <span className="text-xs text-slate-400 ml-2">tracked genres</span>
                  </div>
                </div>
              </div>

              {/* Favorite Genres List */}
              {statsData.favorite_genres && statsData.favorite_genres.length > 0 && (
                <div className="p-6 rounded-xl bg-slate-800/60 border border-slate-700 space-y-4">
                  <h3 className="text-base font-semibold text-slate-100">
                    Most Read Categories & Genres
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {statsData.favorite_genres.map((genre, i) => {
                      const name = typeof genre === 'string' ? genre : genre.name;
                      const count = typeof genre === 'object' ? genre.count : undefined;
                      return (
                        <span
                          key={`genre-${i}-${name}`}
                          className="px-3 py-1.5 rounded-lg bg-slate-700/80 border border-slate-600 text-slate-200 text-xs font-medium flex items-center gap-1.5"
                        >
                          <span>{name}</span>
                          {count != null && (
                            <span className="text-amber font-mono font-bold">({count})</span>
                          )}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}

      {selectedBook && <BookModal book={selectedBook} onClose={() => setSelectedBook(null)} />}
    </div>
  );
}
