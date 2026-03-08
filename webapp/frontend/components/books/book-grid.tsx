/** Book grid component. */

'use client';

import { useState } from 'react';
import { Book } from '@/common/api';
import { LayoutGrid, List } from 'lucide-react';
import { BookCard } from './book-card';
import { BookList } from './book-list';
import { BookModal } from './book-modal';

interface BookGridProps {
  books: Book[];
}

type ViewMode = 'grid' | 'list';

export function BookGrid({ books }: BookGridProps) {
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  if (books.length === 0) {
    return <p className="text-slate-400">No books found.</p>;
  }

  return (
    <>
      <div className="flex justify-end mb-4 border-b border-slate-700 pb-4 gap-2">
        <button
          onClick={() => setViewMode('grid')}
          className={`p-2 rounded-md transition-colors ${viewMode === 'grid'
              ? 'bg-amber text-slate-900'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          title="Grid View"
        >
          <LayoutGrid className="w-5 h-5" />
        </button>
        <button
          onClick={() => setViewMode('list')}
          className={`p-2 rounded-md transition-colors ${viewMode === 'list'
              ? 'bg-amber text-slate-900'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          title="List View"
        >
          <List className="w-5 h-5" />
        </button>
      </div>

      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {books.map((book) => (
            <BookCard
              key={book.id}
              book={book}
              onClick={() => setSelectedBook(book)}
            />
          ))}
        </div>
      ) : (
        <BookList books={books} onBookClick={(book) => setSelectedBook(book)} />
      )}

      {selectedBook && (
        <BookModal
          book={selectedBook}
          onClose={() => setSelectedBook(null)}
        />
      )}
    </>
  );
}
