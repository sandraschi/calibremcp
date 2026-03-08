'use client';

import { useState, useEffect } from 'react';
import { Book, getBook, getBookCoverUrl, openBookViewer } from '@/common/api';
import { AuthorLinks } from '@/components/authors/author-links';
import { BookOpen, X, FileText } from 'lucide-react';

interface BookModalProps {
  book: Book;
  onClose: () => void;
}

export function BookModal({ book, onClose }: BookModalProps) {
  const [details, setDetails] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [readLoading, setReadLoading] = useState(false);
  const [readError, setReadError] = useState<string | null>(null);
  const [coverError, setCoverError] = useState(false);

  useEffect(() => {
    getBook(book.id)
      .then(setDetails)
      .catch(() => setDetails(book))
      .finally(() => setLoading(false));
  }, [book.id, book]);

  const handleRead = async () => {
    setReadLoading(true);
    setReadError(null);
    try {
      await openBookViewer(book.id);
      onClose();
    } catch (e) {
      setReadError(e instanceof Error ? e.message : 'Failed to open book');
    } finally {
      setReadLoading(false);
    }
  };

  const displayBook = details ?? book;
  const tags = displayBook.tags?.map((t) =>
    typeof t === 'string' ? t : (t as { name?: string }).name ?? String(t)
  ) ?? [];
  const description = displayBook.comments ?? displayBook.description ?? '';
  const seriesName = typeof displayBook.series === 'string'
    ? displayBook.series
    : (displayBook.series as { name?: string })?.name;
  const formats = displayBook.formats?.map((f) =>
    typeof f === 'string' ? f : (f as { format?: string }).format ?? ''
  ).filter(Boolean) ?? [];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950" onClick={onClose}>
      <div
        className="border border-slate-600 rounded-lg shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        style={{ backgroundColor: '#1e293b' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col md:flex-row p-0 overflow-auto flex-1 min-h-0">
          {/* Column 1: Cover */}
          <div className="w-full md:w-64 p-6 bg-slate-900/40 flex-shrink-0 border-b md:border-b-0 md:border-r border-slate-700">
            <div className="sticky top-0">
              {!coverError ? (
                <img
                  src={getBookCoverUrl(book.id)}
                  alt={book.title}
                  className="w-full aspect-[2/3] object-cover rounded shadow-lg bg-slate-700"
                  onError={() => setCoverError(true)}
                />
              ) : (
                <div className="w-full aspect-[2/3] rounded bg-slate-700 flex items-center justify-center text-slate-500 text-sm">
                  No Cover
                </div>
              )}

              <div className="mt-8 flex flex-col gap-3">
                <button
                  type="button"
                  onClick={handleRead}
                  disabled={readLoading}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-amber text-slate-900 font-bold rounded-md hover:bg-amber/90 disabled:opacity-50 transition-colors shadow-lg"
                >
                  <BookOpen className="w-5 h-5" />
                  {readLoading ? 'Opening...' : 'Read book'}
                </button>
                {readError && <p className="text-xs text-red-400 text-center">{readError}</p>}

                <button
                  type="button"
                  onClick={onClose}
                  className="w-full px-4 py-2 border border-slate-600 text-slate-300 rounded hover:bg-slate-700/50 transition-colors text-sm"
                >
                  Close
                </button>
              </div>
            </div>
          </div>

          {/* Column 2: Metadata */}
          <div className="flex-1 min-w-[300px] p-6 border-b md:border-b-0 md:border-r border-slate-700 bg-slate-800/20">
            <h2 className="text-2xl font-bold text-slate-100 leading-tight">{displayBook.title}</h2>
            <div className="text-lg text-amber/90 mt-2 font-medium">
              <AuthorLinks authors={displayBook.authors ?? []} className="text-amber/90" />
            </div>

            {loading ? (
              <div className="mt-8 flex items-center gap-2 text-slate-500">
                <div className="w-4 h-4 border-2 border-amber border-t-transparent rounded-full animate-spin" />
                <span className="text-sm italic">Retrieving advanced metadata...</span>
              </div>
            ) : (
              <div className="mt-6 space-y-6">
                <div>
                  <h3 className="text-xs font-uppercase tracking-wider text-slate-500 font-bold mb-2 uppercase">Core Details</h3>
                  <dl className="grid grid-cols-1 gap-x-4 gap-y-2 text-sm">
                    {displayBook.rating != null && displayBook.rating > 0 && (
                      <div className="flex justify-between border-b border-slate-700/50 pb-1">
                        <dt className="text-slate-400">Rating</dt>
                        <dd className="text-amber font-mono tracking-widest text-xs">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <span key={i} className={i < Math.round((displayBook.rating ?? 0) / 2) ? "text-amber" : "text-slate-600"}>★</span>
                          ))}
                        </dd>
                      </div>
                    )}
                    {seriesName && (
                      <div className="flex flex-col border-b border-slate-700/50 pb-1">
                        <dt className="text-slate-400 text-xs">Series</dt>
                        <dd className="text-slate-200">{seriesName}{displayBook.series_index != null ? ` [${displayBook.series_index}]` : ''}</dd>
                      </div>
                    )}
                    {displayBook.publisher && (
                      <div className="flex justify-between border-b border-slate-700/50 pb-1">
                        <dt className="text-slate-400">Publisher</dt>
                        <dd className="text-slate-200 text-right">{displayBook.publisher}</dd>
                      </div>
                    )}
                    {displayBook.pubdate && (
                      <div className="flex justify-between border-b border-slate-700/50 pb-1">
                        <dt className="text-slate-400">Published</dt>
                        <dd className="text-slate-200">{String(displayBook.pubdate).slice(0, 10)}</dd>
                      </div>
                    )}
                  </dl>
                </div>

                {tags.length > 0 && (
                  <div>
                    <h3 className="text-xs font-uppercase tracking-wider text-slate-500 font-bold mb-2 uppercase">Tags</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {tags.map((t, i) => (
                        <span key={i} className="text-[10px] uppercase font-bold bg-slate-700 border border-slate-600 px-2 py-0.5 rounded-sm text-slate-300">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {formats.length > 0 && (
                  <div>
                    <h3 className="text-xs font-uppercase tracking-wider text-slate-500 font-bold mb-2 uppercase">Available Formats</h3>
                    <div className="flex gap-2">
                      {formats.map(f => (
                        <span key={f} className="text-xs font-mono bg-amber/10 border border-amber/30 text-amber px-2 py-0.5 rounded">
                          {String(f).toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Column 3: Description */}
          <div className="flex-[1.5] min-w-[350px] p-8 bg-slate-900/20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
                <FileText className="w-4 h-4 text-amber" />
                Description & Comments
              </h3>
              {!loading && (
                <span className="text-[10px] text-slate-500 font-mono italic">
                  Source: Calibre Metadata
                </span>
              )}
            </div>

            {loading ? (
              <div className="space-y-3">
                <div className="h-4 bg-slate-700/50 rounded w-full animate-pulse" />
                <div className="h-4 bg-slate-700/50 rounded w-5/6 animate-pulse" />
                <div className="h-4 bg-slate-700/50 rounded w-4/6 animate-pulse" />
              </div>
            ) : description ? (
              <div
                className="text-sm leading-relaxed text-slate-300 prose prose-invert prose-slate max-w-none prose-p:my-2"
                dangerouslySetInnerHTML={{ __html: description.replace(/\n/g, '<br />') }}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-slate-500 italic py-12">
                <p>No description available for this volume.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
