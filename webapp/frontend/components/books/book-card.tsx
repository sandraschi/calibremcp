/** Book card component. */

'use client';

import { type Book, getBookCoverUrl, getBookReaderUrl, ratingToFiveStarCount } from '@/common/api';
import { AuthorLinks } from '@/components/authors/author-links';
import { BookOpen } from 'lucide-react';
import { useState } from 'react';

interface BookCardProps {
  book: Book;
  onClick?: () => void;
}

export function BookCard({ book, onClick }: BookCardProps) {
  const [coverError, setCoverError] = useState(false);
  const coverUrl = getBookCoverUrl(book.id);

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
      className="border border-slate-600 rounded-lg p-4 bg-slate-800 hover:bg-slate-700 transition-colors cursor-pointer flex flex-col justify-between"
    >
      <div>
        {!coverError ? (
          <img
            src={coverUrl}
            alt={book.title}
            className="w-full h-64 object-cover mb-2 rounded"
            onError={() => setCoverError(true)}
          />
        ) : (
          <div className="w-full h-64 bg-slate-700 mb-2 rounded flex items-center justify-center">
            <span className="text-slate-500">No Cover</span>
          </div>
        )}
        <h3 className="font-semibold text-lg mb-1 line-clamp-2 text-slate-100">{book.title}</h3>
        <p className="text-sm text-slate-400 mb-2">
          <AuthorLinks authors={book.authors ?? []} stopPropagation />
        </p>
        <div className="flex items-center justify-between">
          {book.rating != null && book.rating > 0 ? (
            <span className="text-yellow-500 text-sm">
              {'⭐'.repeat(ratingToFiveStarCount(book.rating))}
            </span>
          ) : (
            <span />
          )}
          <a
            href={getBookReaderUrl(book.id)}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            title="Read in Calibre Content Server"
            className="inline-flex items-center gap-1 text-xs text-amber/90 hover:text-amber bg-slate-900/60 border border-slate-700 hover:border-amber/40 rounded px-2 py-0.5 transition-colors"
          >
            <BookOpen className="w-3 h-3 text-amber" />
            <span>Read</span>
          </a>
        </div>
      </div>
      {book.tags && book.tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {book.tags.slice(0, 3).map((tag, i) => {
            const label =
              typeof tag === 'string' ? tag : ((tag as { name?: string }).name ?? String(tag));
            return (
              <span
                key={`${book.id}-tag-${i}-${label}`}
                className="text-xs bg-slate-600 px-2 py-1 rounded text-slate-300"
              >
                {label}
              </span>
            );
          })}
        </div>
      )}
      {book.snippet && (
        <div
          className="mt-2 text-xs text-slate-400 line-clamp-2 [&_mark]:bg-amber/30 [&_mark]:text-slate-200"
          dangerouslySetInnerHTML={{ __html: book.snippet }}
        />
      )}
    </div>
  );
}
