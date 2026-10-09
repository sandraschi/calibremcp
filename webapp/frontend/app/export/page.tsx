'use client';

import { exportBooks } from '@/common/api';
import { useState } from 'react';

type ExportFormat = 'csv' | 'json' | 'html' | 'pandoc';

export default function ExportPage() {
  const [format, setFormat] = useState<ExportFormat>('csv');
  const [pandocType, setPandocType] = useState('docx');
  const [htmlStyle, setHtmlStyle] = useState('gallery');
  const [author, setAuthor] = useState('');
  const [tag, setTag] = useState('');
  const [limit, setLimit] = useState(1000);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    success?: boolean;
    message?: string;
    error?: string;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const data = await exportBooks(format, {
        author: author.trim() || undefined,
        tag: tag.trim() || undefined,
        limit,
        open_file: false,
        format_type: format === 'pandoc' ? pandocType : undefined,
        html_style: format === 'html' ? htmlStyle : undefined,
      });
      if ((data as { success?: boolean }).success === false) {
        setResult({ success: false, error: (data as { error?: string }).error ?? 'Export failed' });
      } else {
        const d = data as { message?: string; count?: number; output_path?: string; file?: string };
        setResult({
          success: true,
          message:
            d.message ??
            `Exported ${d.count ?? 'books'} to ${format.toUpperCase()}${d.output_path ? ` → ${d.output_path}` : ''}${d.file ? ` → ${d.file}` : ''}`,
        });
      }
    } catch (e) {
      setResult({
        success: false,
        error: e instanceof Error ? e.message : 'Request failed',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Export</h1>
      <p className="text-slate-400 mb-6">
        Export books to CSV, JSON, HTML catalog, or Pandoc documents. Filter by author or tag.
        Output is written server-side; the result shows the file path.
      </p>
      <form onSubmit={handleSubmit} className="max-w-xl space-y-4">
        <div>
          <label htmlFor="format" className="block text-sm font-medium text-slate-300 mb-2">
            Format
          </label>
          <select
            id="format"
            value={format}
            onChange={(e) => setFormat(e.target.value as ExportFormat)}
            className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
            <option value="html">HTML catalog</option>
            <option value="pandoc">Pandoc document</option>
          </select>
        </div>
        {format === 'pandoc' && (
          <div>
            <label htmlFor="pandocType" className="block text-sm font-medium text-slate-300 mb-2">
              Pandoc target type
            </label>
            <select
              id="pandocType"
              value={pandocType}
              onChange={(e) => setPandocType(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
            >
              <option value="docx">DOCX</option>
              <option value="pdf">PDF</option>
              <option value="epub">EPUB</option>
              <option value="rtf">RTF</option>
              <option value="md">Markdown</option>
            </select>
          </div>
        )}
        {format === 'html' && (
          <div>
            <label htmlFor="htmlStyle" className="block text-sm font-medium text-slate-300 mb-2">
              HTML style
            </label>
            <select
              id="htmlStyle"
              value={htmlStyle}
              onChange={(e) => setHtmlStyle(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
            >
              <option value="gallery">Gallery</option>
              <option value="catalog">Catalog</option>
              <option value="dashboard">Dashboard</option>
            </select>
          </div>
        )}
        <div>
          <label htmlFor="author" className="block text-sm font-medium text-slate-300 mb-2">
            Author filter (optional)
          </label>
          <input
            id="author"
            type="text"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            placeholder="Filter by author name"
            className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </div>
        <div>
          <label htmlFor="tag" className="block text-sm font-medium text-slate-300 mb-2">
            Tag filter (optional)
          </label>
          <input
            id="tag"
            type="text"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Filter by tag"
            className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </div>
        <div>
          <label htmlFor="limit" className="block text-sm font-medium text-slate-300 mb-2">
            Max books
          </label>
          <input
            id="limit"
            type="number"
            min={1}
            max={10000}
            value={limit}
            onChange={(e) => setLimit(Number.parseInt(e.target.value, 10) || 1000)}
            className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Exporting...' : 'Export'}
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
