'use client';

import { Library } from '@/lib/api';
import { useState } from 'react';

interface LibraryListProps {
  libraries: Library[];
  currentLibrary?: string;
}

export function LibraryList({ libraries, currentLibrary }: LibraryListProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      {libraries.length === 0 ? (
        <p className="text-gray-500">No libraries found.</p>
      ) : (
        <div className="space-y-2">
          {libraries.map((library) => (
            <div
              key={library.name}
              className={`p-3 border rounded-lg ${
                library.is_active || library.name === currentLibrary
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg">
                    {library.name}
                    {(library.is_active || library.name === currentLibrary) && (
                      <span className="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded">
                        Active
                      </span>
                    )}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">{library.path}</p>
                  <div className="mt-2 flex gap-4 text-sm text-gray-500">
                    {library.book_count !== undefined && (
                      <span>{library.book_count} books</span>
                    )}
                    {library.size_mb !== undefined && (
                      <span>{library.size_mb.toFixed(2)} MB</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
