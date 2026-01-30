import { getHelp } from '@/lib/api';

export default async function HelpPage({
  searchParams,
}: {
  searchParams: Promise<{ level?: string; topic?: string }>;
}) {
  const params = await searchParams;
  const level = (params.level ?? 'basic') as 'basic' | 'intermediate' | 'advanced' | 'expert';

  let data: Record<string, unknown>;
  try {
    data = await getHelp(level, params.topic);
  } catch (e) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Help</h1>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load help</p>
          <p className="mt-2 text-sm text-slate-400">{String((e as Error).message)}</p>
        </div>
      </div>
    );
  }

  const content = typeof data.content === 'string'
    ? data.content
    : typeof data.help === 'string'
      ? data.help
      : JSON.stringify(data, null, 2);

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Help</h1>
      <div className="p-4 rounded-lg bg-slate-800 border border-slate-600 text-slate-300 text-sm overflow-auto whitespace-pre-wrap font-mono">
        {content}
      </div>
    </div>
  );
}
