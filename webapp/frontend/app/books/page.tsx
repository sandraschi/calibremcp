import Link from 'next/link';
import { getBooks } from '@/lib/api';
import { BookGrid } from '@/components/books/book-grid';

function buildPageUrl(base: string, page: number, author?: string, tag?: string): string {
  const params = new URLSearchParams();
  if (page > 1) params.set('page', page.toString());
  if (author) params.set('author', author);
  if (tag) params.set('tag', tag);
  const q = params.toString();
  return q ? `${base}?${q}` : base;
}

export default async function BooksPage({
  searchParams,
}: {
  searchParams: Promise<{ author?: string; tag?: string; page?: string }>;
}) {
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page || '1'));
  const limit = 50;
  const offset = (page - 1) * limit;

  let data: { items?: unknown[]; total?: number };
  try {
    data = await getBooks({
      limit,
      offset,
      author: params.author,
      tag: params.tag,
    });
  } catch (e) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Browse</h1>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load books</p>
          <p className="mt-2 text-sm text-slate-400">{String((e as Error).message)}</p>
          <p className="mt-2 text-sm text-slate-500">Start the backend with: cd webapp/backend; python -m uvicorn app.main:app --reload --port 13000</p>
        </div>
      </div>
    );
  }

  const total = data.total ?? 0;
  const totalPages = Math.ceil(total / limit);
  const hasPrev = page > 1;
  const hasNext = page < totalPages;
  const base = '/books';

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Browse</h1>
      <BookGrid books={data.items || []} />
      {total > limit && (
        <nav className="mt-6 flex flex-wrap items-center justify-center gap-2" aria-label="Pagination">
          <p className="w-full text-center text-sm text-slate-400 mb-2">
            Showing {offset + 1}-{Math.min(offset + limit, total)} of {total} books
          </p>
          <div className="flex items-center gap-2">
            {hasPrev ? (
              <Link
                href={buildPageUrl(base, page - 1, params.author, params.tag)}
                className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
              >
                Previous
              </Link>
            ) : (
              <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Previous</span>
            )}
            <span className="px-3 py-2 text-sm text-slate-400">
              Page {page} of {totalPages}
            </span>
            {hasNext ? (
              <Link
                href={buildPageUrl(base, page + 1, params.author, params.tag)}
                className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
              >
                Next
              </Link>
            ) : (
              <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Next</span>
            )}
          </div>
        </nav>
      )}
    </div>
  );
}
