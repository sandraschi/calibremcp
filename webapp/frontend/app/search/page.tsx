import Link from 'next/link';
import { searchBooks } from '@/lib/api';
import { BookGrid } from '@/components/books/book-grid';
import { SearchBar } from '@/components/search/search-bar';

function buildSearchPageUrl(
  base: string,
  page: number,
  p: { query?: string; author?: string; tag?: string; min_rating?: string }
): string {
  const params = new URLSearchParams();
  if (page > 1) params.set('page', page.toString());
  if (p.query) params.set('query', p.query);
  if (p.author) params.set('author', p.author);
  if (p.tag) params.set('tag', p.tag);
  if (p.min_rating) params.set('min_rating', p.min_rating);
  const q = params.toString();
  return q ? `${base}?${q}` : base;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ 
    query?: string; 
    author?: string; 
    tag?: string; 
    min_rating?: string;
    page?: string;
  }>;
}) {
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page || '1'));
  const limit = 50;
  const offset = (page - 1) * limit;

  const hasSearchParams = params.query || params.author || params.tag || params.min_rating;

  let data: { items?: unknown[]; total?: number };
  if (hasSearchParams) {
    data = await searchBooks({
      query: params.query,
      author: params.author,
      tag: params.tag,
      min_rating: params.min_rating ? parseInt(params.min_rating) : undefined,
      limit,
      offset,
    });
  } else {
    data = { items: [], total: 0 };
  }

  const total = data.total ?? 0;
  const totalPages = Math.ceil(total / limit);
  const hasPrev = page > 1;
  const hasNext = page < totalPages;
  const base = '/search';

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Search Books</h1>
      <SearchBar 
        initialQuery={params.query}
        initialAuthor={params.author}
        initialTag={params.tag}
        initialMinRating={params.min_rating}
      />
      
      {hasSearchParams && (
        <>
          {data.items && data.items.length > 0 ? (
            <>
              <div className="mt-6">
                <BookGrid books={data.items} />
              </div>
              {total > limit && (
                <nav className="mt-6 flex flex-wrap items-center justify-center gap-2" aria-label="Pagination">
                  <p className="w-full text-center text-sm text-slate-400 mb-2">
                    Showing {offset + 1}-{Math.min(offset + limit, total)} of {total} books
                  </p>
                  <div className="flex items-center gap-2">
                    {hasPrev ? (
                      <Link
                        href={buildSearchPageUrl(base, page - 1, params)}
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
                        href={buildSearchPageUrl(base, page + 1, params)}
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
            </>
          ) : (
            <div className="mt-6 text-center text-gray-500">
              <p>No books found matching your search criteria.</p>
            </div>
          )}
        </>
      )}
      
      {!hasSearchParams && (
        <div className="mt-6 text-center text-slate-400">
          <p>Enter search criteria above to find books.</p>
        </div>
      )}
    </div>
  );
}
