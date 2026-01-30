'use client';

import { useState, useEffect } from 'react';
import { Book, getBook, getBookCoverUrl, openBookViewer } from '@/lib/api';
import { AuthorLinks } from '@/components/authors/author-links';
import { BookOpen, X } from 'lucide-react';

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
        className="border border-slate-600 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        style={{ backgroundColor: '#1e293b' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-6 p-6 overflow-auto flex-1 min-h-0">
          <div className="shrink-0">
            {!coverError ? (
              <img
                src={getBookCoverUrl(book.id)}
                alt={book.title}
                className="w-40 h-56 object-cover rounded bg-slate-700"
                onError={() => setCoverError(true)}
              />
            ) : (
              <div className="w-40 h-56 rounded bg-slate-700 flex items-center justify-center text-slate-500 text-sm">
                No Cover
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h2 className="text-xl font-semibold text-slate-100">{displayBook.title}</h2>
              <button
                type="button"
                onClick={onClose}
                className="p-1 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-slate-300 mt-1">
              <AuthorLinks authors={displayBook.authors ?? []} className="text-slate-300" />
            </p>
            {loading ? (
              <p className="text-slate-500 text-sm mt-4">Loading...</p>
            ) : (
              <>
                <dl className="mt-3 space-y-1 text-sm">
                  {displayBook.rating != null && displayBook.rating > 0 && (
                    <div><dt className="inline font-medium text-slate-400">Rating: </dt><dd className="inline text-amber">{'*'.repeat(Math.min(5, Math.round(displayBook.rating)))}</dd></div>
                  )}
                  {seriesName && (
                    <div><dt className="inline font-medium text-slate-400">Series: </dt><dd className="inline text-slate-300">{seriesName}{displayBook.series_index != null ? ` #${displayBook.series_index}` : ''}</dd></div>
                  )}
                  {displayBook.publisher && (
                    <div><dt className="inline font-medium text-slate-400">Publisher: </dt><dd className="inline text-slate-300">{displayBook.publisher}</dd></div>
                  )}
                  {displayBook.pubdate && (
                    <div><dt className="inline font-medium text-slate-400">Published: </dt><dd className="inline text-slate-300">{String(displayBook.pubdate).slice(0, 10)}</dd></div>
                  )}
                  {displayBook.timestamp && (
                    <div><dt className="inline font-medium text-slate-400">Added: </dt><dd className="inline text-slate-300">{String(displayBook.timestamp).slice(0, 10)}</dd></div>
                  )}
                  {displayBook.identifiers && Object.keys(displayBook.identifiers).length > 0 && (
                    <div><dt className="font-medium text-slate-400">Identifiers: </dt><dd className="text-slate-300">{Object.entries(displayBook.identifiers).map(([k, v]) => `${k}: ${v}`).join(', ')}</dd></div>
                  )}
                </dl>
                {tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {tags.map((t, i) => (
                      <span key={i} className="text-xs bg-slate-600 px-2 py-1 rounded text-slate-300">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
                {formats.length > 0 && (
                  <p className="mt-2 text-sm text-slate-400">
                    Formats: {formats.join(', ')}
                  </p>
                )}
                {description && (
                  <div className="mt-4">
                    <h3 className="text-sm font-semibold text-slate-200 mb-1">Description</h3>
                    <div
                      className="text-sm text-slate-400 max-h-32 overflow-y-auto"
                      dangerouslySetInnerHTML={{ __html: description.replace(/\n/g, '<br />') }}
                    />
                  </div>
                )}
              </>
            )}
          </div>
        </div>
        <div className="px-6 pb-6 flex flex-col gap-2">
          <button
            type="button"
            onClick={handleRead}
            disabled={readLoading}
            className="inline-flex items-center justify-center gap-2 px-4 py-3 bg-amber text-slate-900 font-medium rounded-md hover:bg-amber/90 disabled:opacity-50"
          >
            <BookOpen className="w-5 h-5" />
            {readLoading ? 'Opening...' : 'Read book'}
          </button>
          {readError && <p className="text-sm text-red-400">{readError}</p>}
        </div>
      </div>
    </div>
  );
}
