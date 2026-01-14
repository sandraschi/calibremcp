/** Book card component. */

'use client';

import Link from 'next/link';
import { Book } from '@/lib/api';

interface BookCardProps {
  book: Book;
}

export function BookCard({ book }: BookCardProps) {
  return (
    <Link href={`/books/${book.id}`}>
      <div className="border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer">
        {book.cover_url ? (
          <img
            src={book.cover_url}
            alt={book.title}
            className="w-full h-64 object-cover mb-2 rounded"
          />
        ) : (
          <div className="w-full h-64 bg-gray-200 mb-2 rounded flex items-center justify-center">
            <span className="text-gray-400">No Cover</span>
          </div>
        )}
        <h3 className="font-semibold text-lg mb-1 line-clamp-2">{book.title}</h3>
        <p className="text-sm text-gray-600 mb-2">{book.authors.join(', ')}</p>
        {book.rating && (
          <div className="flex items-center">
            <span className="text-yellow-500">{'⭐'.repeat(book.rating)}</span>
          </div>
        )}
        {book.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {book.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="text-xs bg-gray-100 px-2 py-1 rounded">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}
