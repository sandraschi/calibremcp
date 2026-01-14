'use client';

import { LibraryStats } from '@/lib/api';

interface LibraryStatsDisplayProps {
  stats: LibraryStats;
}

export function LibraryStatsDisplay({ stats }: LibraryStatsDisplayProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-xl font-semibold mb-4">{stats.library_name}</h3>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 p-3 rounded">
          <div className="text-sm text-gray-600">Total Books</div>
          <div className="text-2xl font-bold">{stats.total_books}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <div className="text-sm text-gray-600">Authors</div>
          <div className="text-2xl font-bold">{stats.total_authors}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <div className="text-sm text-gray-600">Series</div>
          <div className="text-2xl font-bold">{stats.total_series}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <div className="text-sm text-gray-600">Tags</div>
          <div className="text-2xl font-bold">{stats.total_tags}</div>
        </div>
      </div>

      {Object.keys(stats.format_distribution).length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold mb-2">Format Distribution</h4>
          <div className="space-y-1">
            {Object.entries(stats.format_distribution)
              .sort(([, a], [, b]) => b - a)
              .map(([format, count]) => (
                <div key={format} className="flex justify-between text-sm">
                  <span className="text-gray-700">{format.toUpperCase()}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {stats.last_modified && (
        <div className="text-sm text-gray-500 mt-4">
          Last modified: {new Date(stats.last_modified).toLocaleString()}
        </div>
      )}
    </div>
  );
}
