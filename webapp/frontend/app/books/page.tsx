import { getBooks } from '@/lib/api';
import { BookGrid } from '@/components/books/book-grid';

export default async function BooksPage({
  searchParams,
}: {
  searchParams: Promise<{ author?: string; tag?: string; page?: string }>;
}) {
  const params = await searchParams;
  const page = parseInt(params.page || '1');
  const limit = 50;
  const offset = (page - 1) * limit;

  const data = await getBooks({
    limit,
    offset,
    author: params.author,
    tag: params.tag,
  });

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Browse</h1>
      <BookGrid books={data.items || []} />
      {data.total && data.total > limit && (
        <div className="mt-6 text-center">
          <p>Showing {offset + 1}-{Math.min(offset + limit, data.total)} of {data.total} books</p>
        </div>
      )}
    </div>
  );
}
