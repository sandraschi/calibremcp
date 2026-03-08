/** Book list view component. */

'use client';

import { useState } from 'react';
import { Book, getBookCoverUrl } from '@/common/api';
import { AuthorLinks } from '@/components/authors/author-links';
import { Calendar, Hash, Star } from 'lucide-react';

interface BookListProps {
    books: Book[];
    onBookClick: (book: Book) => void;
}

export function BookList({ books, onBookClick }: BookListProps) {
    return (
        <div className="flex flex-col gap-3">
            {books.map((book) => (
                <BookItem key={book.id} book={book} onClick={() => onBookClick(book)} />
            ))}
        </div>
    );
}

function BookItem({ book, onClick }: { book: Book; onClick: () => void }) {
    const [coverError, setCoverError] = useState(false);
    const coverUrl = getBookCoverUrl(book.id);

    return (
        <div
            role="button"
            tabIndex={0}
            onClick={onClick}
            onKeyDown={(e) => e.key === 'Enter' && onClick()}
            className="flex gap-4 p-3 border border-slate-600 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors cursor-pointer text-left items-start"
        >
            <div className="w-16 h-24 shrink-0 bg-slate-700 rounded overflow-hidden">
                {!coverError ? (
                    <img
                        src={coverUrl}
                        alt={book.title}
                        className="w-full h-full object-cover"
                        onError={() => setCoverError(true)}
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center">
                        <Hash className="w-6 h-6 text-slate-500" />
                    </div>
                )}
            </div>

            <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start gap-2">
                    <h3 className="font-semibold text-slate-100 truncate flex-1">{book.title}</h3>
                    {book.rating && (
                        <div className="flex items-center gap-1 shrink-0 bg-slate-900/50 px-2 py-0.5 rounded border border-slate-600">
                            <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
                            <span className="text-xs font-bold text-slate-200">{book.rating}</span>
                        </div>
                    )}
                </div>

                <p className="text-sm text-slate-400 mb-2 truncate">
                    <AuthorLinks authors={book.authors ?? []} stopPropagation />
                </p>

                <div className="flex flex-wrap gap-2 items-center">
                    {book.series && (
                        <span className="text-xs text-slate-400 flex items-center gap-1 bg-slate-900/50 px-2 py-0.5 rounded border border-slate-700">
                            {typeof book.series === 'string' ? book.series : book.series.name}
                            {book.series_index !== undefined && (
                                <span className="text-slate-500">#{book.series_index}</span>
                            )}
                        </span>
                    )}
                    {book.pubdate && (
                        <span className="text-xs text-slate-400 flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(book.pubdate).getFullYear()}
                        </span>
                    )}
                    {book.tags && book.tags.slice(0, 5).map((tag, i) => {
                        const label = typeof tag === 'string' ? tag : (tag as { name?: string }).name ?? String(tag);
                        return (
                            <span key={`${book.id}-tag-${i}`} className="text-[10px] bg-slate-700/50 px-2 py-0.5 rounded text-slate-300 border border-slate-600/50">
                                {label}
                            </span>
                        );
                    })}
                </div>

                {book.snippet && (
                    <div
                        className="mt-2 text-xs text-slate-400 line-clamp-1 [&_mark]:bg-amber/30 [&_mark]:text-slate-200 italic"
                        dangerouslySetInnerHTML={{ __html: book.snippet }}
                    />
                )}
            </div>
        </div>
    );
}
