import { searchBooks } from '@/lib/api';
import { BookGrid } from '@/components/books/book-grid';
import { SearchBar } from '@/components/search/search-bar';

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
  const page = parseInt(params.page || '1');
  const limit = 50;
  const offset = (page - 1) * limit;

  const hasSearchParams = params.query || params.author || params.tag || params.min_rating;

  let data;
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
    // Show empty state if no search params
    data = { items: [], total: 0 };
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Search Books</h1>
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
              {data.total && data.total > limit && (
                <div className="mt-6 text-center">
                  <p className="text-gray-600">
                    Showing {offset + 1}-{Math.min(offset + limit, data.total)} of {data.total} books
                  </p>
                </div>
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
        <div className="mt-6 text-center text-gray-500">
          <p>Enter search criteria above to find books.</p>
        </div>
      )}
    </div>
  );
}
