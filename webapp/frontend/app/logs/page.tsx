import { getSystemStatus } from '@/lib/api';

export default async function LogsPage() {
  let data: Record<string, unknown>;
  try {
    data = await getSystemStatus('diagnostic');
  } catch (e) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Logs</h1>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load system status</p>
          <p className="mt-2 text-sm text-slate-400">{String((e as Error).message)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Logs</h1>
      <pre className="p-4 rounded-lg bg-slate-800 border border-slate-600 text-slate-300 text-sm overflow-auto max-h-[70vh] whitespace-pre-wrap font-mono">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
