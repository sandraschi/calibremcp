import Link from 'next/link';
import { getBooks, type BookListResponse } from '@/common/api';
import { BookGrid } from '@/components/books/book-grid';
import { ErrorBanner } from '@/components/ui/error-banner';

const BACKEND_HINT = 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721).';

function buildPageUrl(
  base: string,
  page: number,
  author?: string,
  tag?: string,
  publisher?: string
): string {
  const params = new URLSearchParams();
  if (page > 1) params.set('page', page.toString());
  if (author) params.set('author', author);
  if (tag) params.set('tag', tag);
  if (publisher) params.set('publisher', publisher);
  const q = params.toString();
  return q ? `${base}?${q}` : base;
}

export default async function BooksPage({
  searchParams,
}: {
  searchParams: Promise<{ author?: string; tag?: string; publisher?: string; page?: string }>;
}) {
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page || '1'));
  const limit = 50;
  const offset = (page - 1) * limit;

  let data: BookListResponse;
  try {
    data = await getBooks({
      limit,
      offset,
      author: params.author,
      tag: params.tag,
      publisher: params.publisher,
    });
  } catch (e) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Browse</h1>
        <ErrorBanner
          title="Could not load books"
          message={String((e as Error).message)}
          hint={BACKEND_HINT}
        />
      </div>
    );
  }

  const items = Array.isArray(data?.items) ? data.items : [];
  const total = typeof data?.total === 'number' ? data.total : 0;
  const totalPages = Math.ceil(total / limit);
  const base = '/books';

  // Pagination logic: show current page and a few around it
  const pageRange = 2; // Number of pages to show before/after current
  const pages: number[] = [];
  for (let i = Math.max(1, page - pageRange); i <= Math.min(totalPages, page + pageRange); i++) {
    pages.push(i);
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <h1 className="text-3xl font-bold text-slate-100">Browse</h1>
      </div>

      <BookGrid books={items} />

      {total > limit && (
        <nav className="mt-8 flex flex-col items-center gap-4" aria-label="Pagination Navigation">
          <p className="text-sm text-slate-400">
            Showing <span className="text-slate-200 font-medium">{offset + 1}</span>–
            <span className="text-slate-200 font-medium">{Math.min(offset + limit, total)}</span> of{' '}
            <span className="text-slate-200 font-medium">{total}</span> books
          </p>

          <div className="flex flex-wrap items-center justify-center gap-1">
            {/* First Page */}
            {page > 1 && (
              <Link
                href={buildPageUrl(base, 1, params.author, params.tag, params.publisher)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="First Page"
              >
                First
              </Link>
            )}

            {/* Previous */}
            {page > 1 ? (
              <Link
                href={buildPageUrl(base, page - 1, params.author, params.tag, params.publisher)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="Previous Page"
              >
                Prev
              </Link>
            ) : (
              <span className="px-3 py-2 text-sm text-slate-500 bg-slate-800/50 border border-slate-700/50 rounded-md cursor-not-allowed">
                Prev
              </span>
            )}

            {/* Page Numbers */}
            {pages[0] > 1 && <span className="px-2 text-slate-600">...</span>}
            {pages.map((p) => (
              <Link
                key={p}
                href={buildPageUrl(base, p, params.author, params.tag, params.publisher)}
                className={`w-10 h-10 flex items-center justify-center text-sm font-medium rounded-md transition-all ${p === page
                    ? 'bg-amber text-slate-900 border border-amber'
                    : 'bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300'
                  }`}
              >
                {p}
              </Link>
            ))}
            {pages[pages.length - 1] < totalPages && <span className="px-2 text-slate-600">...</span>}

            {/* Next */}
            {page < totalPages ? (
              <Link
                href={buildPageUrl(base, page + 1, params.author, params.tag, params.publisher)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="Next Page"
              >
                Next
              </Link>
            ) : (
              <span className="px-3 py-2 text-sm text-slate-500 bg-slate-800/50 border border-slate-700/50 rounded-md cursor-not-allowed">
                Next
              </span>
            )}

            {/* Last Page */}
            {page < totalPages && (
              <Link
                href={buildPageUrl(base, totalPages, params.author, params.tag, params.publisher)}
                className="px-3 py-2 text-sm font-medium rounded-md bg-slate-800 border border-slate-700 hover:border-amber/50 text-slate-300 transition-colors"
                title="Last Page"
              >
                Last
              </Link>
            )}
          </div>
        </nav>
      )}
    </div>
  );
}
