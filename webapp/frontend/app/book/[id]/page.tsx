import { getBook } from '@/lib/api';
import { BookModalWrapper } from './book-modal-wrapper';

export default async function BookDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const bookId = parseInt(id, 10);
  if (isNaN(bookId)) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Invalid book ID</p>
      </div>
    );
  }

  let book;
  try {
    book = await getBook(bookId);
  } catch {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Book not found</p>
      </div>
    );
  }

  return <BookModalWrapper book={book} />;
}
