'use client';

import { useState } from 'react';

export default function ImportPage() {
  const [path, setPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success?: boolean; message?: string; error?: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!path.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: path.trim(), fetch_metadata: true }),
      });
      const data = await res.json();
      if (res.ok) {
        setResult({ success: true, message: `Added book: ${data.title ?? 'OK'}` });
        setPath('');
      } else {
        setResult({ success: false, error: data.detail ?? data.error ?? 'Import failed' });
      }
    } catch (e) {
      setResult({ success: false, error: e instanceof Error ? e.message : 'Request failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Import</h1>
      <p className="text-slate-400 mb-6">
        Add a book from a file path. The path must be accessible from the server (e.g. a path on the machine running the backend).
      </p>
      <form onSubmit={handleSubmit} className="max-w-xl space-y-4">
        <div>
          <label htmlFor="path" className="block text-sm font-medium text-slate-300 mb-2">
            File path
          </label>
          <input
            id="path"
            type="text"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder="C:\Books\mybook.epub or /path/to/book.epub"
            className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !path.trim()}
          className="px-6 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Importing...' : 'Import'}
        </button>
        {result && (
          <div
            className={`p-4 rounded-lg ${
              result.success ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-400'
            }`}
          >
            {result.success ? result.message : result.error}
          </div>
        )}
      </form>
    </div>
  );
}
