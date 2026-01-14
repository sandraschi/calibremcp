import { listLibraries, getLibraryStats, switchLibrary, Library, LibraryStats } from '@/lib/api';
import { LibraryList } from '@/components/libraries/library-list';
import { LibraryStatsDisplay } from '@/components/libraries/library-stats';
import { LibraryOperations } from '@/components/libraries/library-operations';

export default async function LibrariesPage() {
  const librariesData = await listLibraries();
  const currentLibraryName = librariesData.current_library;
  
  let currentStats: LibraryStats | null = null;
  if (currentLibraryName) {
    try {
      currentStats = await getLibraryStats(currentLibraryName);
    } catch (error) {
      console.error('Failed to load current library stats:', error);
    }
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Libraries</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Library List */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Available Libraries</h2>
          <LibraryList 
            libraries={librariesData.libraries} 
            currentLibrary={currentLibraryName}
          />
        </div>

        {/* Library Stats */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Library Statistics</h2>
          {currentStats ? (
            <LibraryStatsDisplay stats={currentStats} />
          ) : (
            <div className="bg-gray-100 p-4 rounded-lg">
              <p className="text-gray-600">No library selected or stats unavailable.</p>
            </div>
          )}
        </div>
      </div>

      {/* Library Operations */}
      <div className="mt-6">
        <h2 className="text-2xl font-semibold mb-4">Library Operations</h2>
        <LibraryOperations 
          libraries={librariesData.libraries}
          currentLibrary={currentLibraryName}
        />
      </div>
    </div>
  );
}
