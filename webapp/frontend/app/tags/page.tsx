import Link from 'next/link';
import { listTags } from '@/lib/api';

export default async function TagsPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; page?: string }>;
}) {
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page || '1'));
  const limit = 50;
  const offset = (page - 1) * limit;

  let data: { items: { id: number; name: string; book_count?: number }[]; total: number };
  try {
    data = await listTags({ search: params.search, limit, offset });
  } catch (e) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Tags</h1>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load tags</p>
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
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Tags</h1>
      <form className="mb-6" action="/tags" method="get">
        <input
          type="search"
          name="search"
          defaultValue={params.search}
          placeholder="Search tags..."
          className="w-full max-w-md px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
        />
      </form>
      <div className="flex flex-wrap gap-2">
        {data.items.map((t) => (
          <Link
            key={t.id}
            href={`/books?tag=${encodeURIComponent(t.name)}`}
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 hover:bg-slate-700 text-slate-200 transition-colors"
          >
            {t.name}
            {t.book_count != null && (
              <span className="ml-2 text-slate-500 text-sm">({t.book_count})</span>
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
                href={`/tags?page=${page - 1}${params.search ? `&search=${encodeURIComponent(params.search)}` : ''}`}
                className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
              >
                Previous
              </Link>
            ) : (
              <span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">Previous</span>
            )}
            {hasNext ? (
              <Link
                href={`/tags?page=${page + 1}${params.search ? `&search=${encodeURIComponent(params.search)}` : ''}`}
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
