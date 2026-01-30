'use client';

import { useRouter } from 'next/navigation';
import { Book } from '@/lib/api';
import { BookModal } from '@/components/books/book-modal';

export function BookModalWrapper({ book }: { book: Book }) {
  const router = useRouter();
  return (
    <BookModal
      book={book}
      onClose={() => router.back()}
    />
  );
}
