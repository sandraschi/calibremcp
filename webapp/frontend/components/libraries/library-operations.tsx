'use client';

import { Library, switchLibrary } from '@/lib/api';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface LibraryOperationsProps {
  libraries: Library[];
  currentLibrary?: string;
}

export function LibraryOperations({ libraries, currentLibrary }: LibraryOperationsProps) {
  const router = useRouter();
  const [selectedLibrary, setSelectedLibrary] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSwitchLibrary = async () => {
    if (!selectedLibrary) {
      setMessage({ type: 'error', text: 'Please select a library' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await switchLibrary(selectedLibrary);
      if (result.success) {
        setMessage({ type: 'success', text: `Switched to ${result.library_name}` });
        router.refresh();
      } else {
        setMessage({ type: 'error', text: result.message || 'Failed to switch library' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error instanceof Error ? error.message : 'Failed to switch library' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-600 p-4">
      <div className="space-y-4">
        <div>
          <h3 className="font-semibold mb-2 text-slate-200">Switch Active Library</h3>
          <div className="flex gap-2">
            <select
              value={selectedLibrary}
              onChange={(e) => setSelectedLibrary(e.target.value)}
              className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
            >
              <option value="">Select a library...</option>
              {libraries.map((lib) => (
                <option key={lib.name} value={lib.name}>
                  {lib.name} {lib.name === currentLibrary ? '(current)' : ''}
                </option>
              ))}
            </select>
            <button
              onClick={handleSwitchLibrary}
              disabled={loading || !selectedLibrary}
              className="px-4 py-2 bg-amber text-slate-900 rounded-md hover:bg-amber/90 disabled:bg-slate-600 disabled:cursor-not-allowed"
            >
              {loading ? 'Switching...' : 'Switch'}
            </button>
          </div>
        </div>

        {message && (
          <div
            className={`p-3 rounded ${
              message.type === 'success' ? 'bg-emerald-900/50 text-emerald-200' : 'bg-red-900/50 text-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="border-t border-slate-600 pt-4">
          <h3 className="font-semibold mb-2 text-slate-200">Available Operations</h3>
          <ul className="space-y-1 text-sm text-slate-400">
            <li>• Click a library card to switch (Browse and Search use active library)</li>
            <li>• View library statistics</li>
            <li>• Browse library contents</li>
            <li>• Search across libraries</li>
          </ul>
          <p className="text-xs text-slate-500 mt-2">
            Note: Library backup and CRUD operations will be available in a future update.
          </p>
        </div>
      </div>
    </div>
  );
}
