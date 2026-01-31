import Link from 'next/link';
import { listSeries } from '@/lib/api';

export default async function SeriesPage({
  searchParams,
}: {
  searchParams: Promise<{ query?: string; page?: string }>;
}) {
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page || '1'));
  const limit = 50;
  const offset = (page - 1) * limit;

  let data: { items: { id: number; name: string; book_count?: number }[]; total: number };
  try {
    data = await listSeries({ query: params.query, limit, offset });
  } catch (e) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Series</h1>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load series</p>
          <p className="mt-2 text-sm text-slate-400">{String((e as Error).message)}</p>
        </div>
      </div>
    );
  }

  const total = data.total;
  const totalPages = Math.ceil(total / limit);
  const hasPrev = page > 1;
  const hasNext = page < totalPages;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Series</h1>
      <form className="mb-6" action="/series" method="get">
        <input
          type="search"
          name="query"
          defaultValue={params.query}
          placeholder="Search series..."
          className="w-full max-w-md px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
        />
      </form>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {data.items.map((s) => (
          <Link
            key={s.id}
            href={`/series/${s.id}`}
            className="block p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 hover:bg-slate-700 transition-colors"
          >
            <span className="text-slate-200 font-medium">{s.name}</span>
            {s.book_count != null && (
              <span className="block text-sm text-slate-500 mt-1">{s.book_count} books</span>
            )}
          </Link>
        ))}
      </div>
      {total > limit && (
        <nav className="mt-6 flex flex-wrap items-center justify-center gap-2" aria-label="Pagination">
          <p className="w-full text-center text-sm text-slate-400 mb-2">
            Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            {hasPrev ? (
              <Link
                href={`/series?page=${page - 1}${params.query ? `&query=${encodeURIComponent(params.query)}` : ''}`}
                className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
              >
                Previous
              </Link>
            ) : (
              <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Previous</span>
            )}
            {hasNext ? (
              <Link
                href={`/series?page=${page + 1}${params.query ? `&query=${encodeURIComponent(params.query)}` : ''}`}
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
