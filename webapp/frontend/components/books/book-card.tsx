/** Book card component. */

'use client';

import { useState } from 'react';
import { Book, getBookCoverUrl } from '@/lib/api';
import { AuthorLinks } from '@/components/authors/author-links';

interface BookCardProps {
  book: Book;
  onClick?: () => void;
}

export function BookCard({ book, onClick }: BookCardProps) {
  const [coverError, setCoverError] = useState(false);
  const coverUrl = book.cover_url ?? getBookCoverUrl(book.id);

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
      className="border border-slate-600 rounded-lg p-4 bg-slate-800 hover:bg-slate-700 transition-colors cursor-pointer"
    >
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
        {book.rating && (
          <div className="flex items-center">
            <span className="text-yellow-500">{'⭐'.repeat(book.rating)}</span>
          </div>
        )}
        {book.tags && book.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {book.tags.slice(0, 3).map((tag, i) => {
              const label = typeof tag === 'string' ? tag : (tag as { name?: string }).name ?? String(tag);
              return (
                <span key={`${book.id}-tag-${i}-${label}`} className="text-xs bg-slate-600 px-2 py-1 rounded text-slate-300">
                  {label}
                </span>
              );
            })}
          </div>
        )}
    </div>
  );
}
