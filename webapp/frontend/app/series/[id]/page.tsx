import Link from 'next/link';
import { getSeriesBooks } from '@/lib/api';

export default async function SeriesDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const seriesId = parseInt(id, 10);
  if (isNaN(seriesId)) {
    return (
      <div className="container mx-auto p-6">
        <p className="text-slate-400">Invalid series ID</p>
      </div>
    );
  }

  let data: { items?: { id: number; title: string; authors?: { name?: string }[] }[]; series?: { name?: string } };
  try {
    data = await getSeriesBooks(seriesId, { limit: 100 });
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

  const seriesName = data.series?.name ?? `Series #${seriesId}`;
  const books = data.items ?? [];

  return (
    <div className="container mx-auto p-6">
      <Link href="/series" className="text-sm text-amber-400 hover:text-amber-300 mb-4 inline-block">
        Back to Series
      </Link>
      <h1 className="text-3xl font-bold mb-6 text-slate-100">{seriesName}</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {books.map((b: { id: number; title: string; authors?: { name?: string }[] }) => (
          <Link
            key={b.id}
            href={`/book/${b.id}`}
            className="block p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 hover:bg-slate-700 transition-colors"
          >
            <span className="text-slate-200 font-medium">{b.title}</span>
            {b.authors?.length ? (
              <span className="block text-sm text-slate-500 mt-1">
                {b.authors.map((a: { name?: string }) => a.name).filter(Boolean).join(', ')}
              </span>
            ) : null}
          </Link>
        ))}
      </div>
    </div>
  );
}
