import { listLibraries, Library } from '@/lib/api';
import { LibraryList } from '@/components/libraries/library-list';
import { LibraryStatsPanel } from '@/components/libraries/library-stats-panel';
import { LibraryOperations } from '@/components/libraries/library-operations';

export default async function LibrariesPage() {
  let librariesData: { libraries: Library[]; current_library?: string; total_libraries: number };
  try {
    librariesData = await listLibraries();
  } catch (e) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Could not load libraries</p>
          <p className="mt-2 text-sm text-slate-400">{String((e as Error).message)}</p>
          <p className="mt-2 text-sm text-slate-500">Start the backend: cd webapp/backend; python -m uvicorn app.main:app --reload --port 13000</p>
        </div>
      </div>
    );
  }
  const currentLibraryName = librariesData.current_library;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-semibold mb-4 text-slate-200">Available Libraries</h2>
          <LibraryList
            libraries={librariesData.libraries}
            currentLibrary={currentLibraryName}
          />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4 text-slate-200">Library Statistics</h2>
          <LibraryStatsPanel currentLibrary={currentLibraryName} />
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-2xl font-semibold mb-4 text-slate-200">Library Operations</h2>
        <LibraryOperations
          libraries={librariesData.libraries}
          currentLibrary={currentLibraryName}
        />
      </div>
    </div>
  );
}
