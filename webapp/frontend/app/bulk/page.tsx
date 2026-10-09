'use client';

import {
  bulkConvertBooks,
  bulkDeleteBooks,
  bulkExportBooks,
  bulkFileOperation,
  bulkUpdateBooksMetadata,
  convertBookFile,
  downloadBookFile,
} from '@/common/api';
import { Layers } from 'lucide-react';
import { useState } from 'react';

type Op = 'meta' | 'export' | 'delete' | 'convert' | 'file-convert' | 'file-download' | 'file-bulk';

function parseIds(raw: string): number[] {
  return raw
    .split(/[\s,]+/)
    .map((s) => Number.parseInt(s.trim(), 10))
    .filter((n) => Number.isFinite(n));
}

export default function BulkPage() {
  const [ids, setIds] = useState('');
  const [busy, setBusy] = useState<Op | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Op-specific inputs
  const [metaField, setMetaField] = useState('tags');
  const [metaValue, setMetaValue] = useState('');
  const [exportPath, setExportPath] = useState('');
  const [exportFormat, setExportFormat] = useState<'directory' | 'zip'>('directory');
  const [targetFormat, setTargetFormat] = useState('EPUB');
  const [fileOp, setFileOp] = useState<'convert' | 'validate' | 'cleanup'>('validate');

  const idList = parseIds(ids);

  const run = async (op: Op, fn: () => Promise<unknown>) => {
    setBusy(op);
    setError(null);
    setResult(null);
    try {
      if (
        ['meta', 'export', 'delete', 'convert', 'file-convert'].includes(op) &&
        idList.length === 0
      ) {
        throw new Error('Enter at least one book ID');
      }
      const res = await fn();
      setResult(JSON.stringify(res, null, 1).slice(0, 4000));
    } catch (e) {
      setError(e instanceof Error ? e.message : `${op} failed`);
    } finally {
      setBusy(null);
    }
  };

  const inputCls =
    'px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber';
  const cardCls = 'rounded-xl bg-slate-800/80 border border-slate-700 p-5 space-y-3';

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2.5 rounded-lg bg-amber/10 border border-amber/20 text-amber">
          <Layers className="w-6 h-6" />
        </div>
        <h1 className="text-3xl font-bold text-slate-100">Bulk Ops</h1>
      </div>
      <p className="text-slate-400 mb-6 text-sm">
        Batch operations on explicit book-ID lists — backed by{' '}
        <code className="text-xs">manage_bulk_operations</code> and{' '}
        <code className="text-xs">manage_files</code>. Find IDs in book URLs (
        <code className="text-xs">/book/1234</code>).
      </p>

      <div className="mb-6">
        <label htmlFor="bulk-ids" className="block text-sm font-medium text-slate-300 mb-1">
          Book IDs (comma or space separated)
        </label>
        <textarea
          id="bulk-ids"
          data-testid="bulk-ids"
          value={ids}
          onChange={(e) => setIds(e.target.value)}
          rows={2}
          placeholder="e.g. 12, 34, 56"
          className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber"
        />
        <p className="text-xs text-slate-500 mt-1">{idList.length} IDs parsed</p>
      </div>

      {error && <div className="mb-4 p-3 rounded bg-red-500/20 text-red-300 text-sm">{error}</div>}
      {result && (
        <pre className="mb-6 text-xs text-slate-300 whitespace-pre-wrap font-sans max-h-72 overflow-auto rounded bg-slate-900 border border-slate-700 p-3">
          {result}
        </pre>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className={cardCls}>
          <h2 className="font-bold text-slate-100">Update metadata</h2>
          <div className="flex gap-2">
            <input
              value={metaField}
              onChange={(e) => setMetaField(e.target.value)}
              placeholder="field (tags, rating…)"
              className={`${inputCls} w-36`}
            />
            <input
              value={metaValue}
              onChange={(e) => setMetaValue(e.target.value)}
              placeholder="value"
              className={`${inputCls} flex-1`}
            />
          </div>
          <button
            type="button"
            disabled={busy !== null}
            onClick={() =>
              run('meta', () => bulkUpdateBooksMetadata(idList, { [metaField]: metaValue }))
            }
            className="px-4 py-2 rounded-lg bg-amber text-slate-950 font-bold text-sm hover:bg-amber/90 disabled:opacity-50"
          >
            {busy === 'meta' ? '…' : 'Apply to all'}
          </button>
        </div>

        <div className={cardCls}>
          <h2 className="font-bold text-slate-100">Export books</h2>
          <div className="flex gap-2">
            <input
              value={exportPath}
              onChange={(e) => setExportPath(e.target.value)}
              placeholder="Export folder path"
              className={`${inputCls} flex-1`}
            />
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as 'directory' | 'zip')}
              className={inputCls}
            >
              <option value="directory">directory</option>
              <option value="zip">zip</option>
            </select>
          </div>
          <button
            type="button"
            disabled={busy !== null}
            onClick={() => {
              if (!exportPath.trim()) {
                setError('Export path required');
                return;
              }
              run('export', () => bulkExportBooks(idList, exportPath.trim(), exportFormat));
            }}
            className="px-4 py-2 rounded-lg bg-amber text-slate-950 font-bold text-sm hover:bg-amber/90 disabled:opacity-50"
          >
            {busy === 'export' ? '…' : 'Export'}
          </button>
        </div>

        <div className={cardCls}>
          <h2 className="font-bold text-slate-100">Convert formats</h2>
          <select
            value={targetFormat}
            onChange={(e) => setTargetFormat(e.target.value)}
            className={inputCls}
          >
            {['EPUB', 'PDF', 'MOBI', 'AZW3', 'TXT'].map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={busy !== null}
              onClick={() => run('convert', () => bulkConvertBooks(idList, targetFormat))}
              className="px-4 py-2 rounded-lg bg-amber text-slate-950 font-bold text-sm hover:bg-amber/90 disabled:opacity-50"
            >
              {busy === 'convert' ? '…' : 'Bulk convert'}
            </button>
            <button
              type="button"
              disabled={busy !== null}
              onClick={() =>
                run('file-convert', () =>
                  convertBookFile(
                    idList.map((id) => ({ book_id: id, target_format: targetFormat })),
                  ),
                )
              }
              className="px-4 py-2 rounded-lg bg-slate-700 text-slate-200 text-sm hover:bg-slate-600 disabled:opacity-50"
            >
              {busy === 'file-convert' ? '…' : 'Files convert'}
            </button>
          </div>
        </div>

        <div className={cardCls}>
          <h2 className="font-bold text-slate-100">Delete books</h2>
          <p className="text-xs text-slate-500">
            Deletes library entries and their files. No undo.
          </p>
          <button
            type="button"
            disabled={busy !== null}
            onClick={() => {
              if (window.confirm(`Delete ${idList.length} book(s) including files?`))
                run('delete', () => bulkDeleteBooks(idList, true));
            }}
            className="px-4 py-2 rounded-lg bg-red-900/70 text-red-100 font-bold text-sm hover:bg-red-900 disabled:opacity-50"
          >
            {busy === 'delete' ? '…' : 'Delete all'}
          </button>
        </div>

        <div className={cardCls}>
          <h2 className="font-bold text-slate-100">File utilities</h2>
          <div className="flex gap-2">
            <select
              value={fileOp}
              onChange={(e) => setFileOp(e.target.value as 'convert' | 'validate' | 'cleanup')}
              className={inputCls}
            >
              <option value="validate">validate</option>
              <option value="cleanup">cleanup</option>
              <option value="convert">convert</option>
            </select>
            <button
              type="button"
              disabled={busy !== null}
              onClick={() =>
                run('file-bulk', () =>
                  bulkFileOperation(
                    fileOp,
                    fileOp === 'convert'
                      ? {
                          target_format: targetFormat,
                          book_ids: idList.length ? idList : undefined,
                        }
                      : { book_ids: idList.length ? idList : undefined },
                  ),
                )
              }
              className="px-4 py-2 rounded-lg bg-slate-700 text-slate-200 text-sm hover:bg-slate-600 disabled:opacity-50"
            >
              {busy === 'file-bulk' ? '…' : 'Run'}
            </button>
          </div>
          <button
            type="button"
            disabled={busy !== null}
            onClick={() => run('file-download', () => downloadBookFile(idList[0], targetFormat))}
            className="px-4 py-2 rounded-lg bg-slate-700 text-slate-200 text-sm hover:bg-slate-600 disabled:opacity-50"
          >
            {busy === 'file-download' ? '…' : 'Download first ID as file'}
          </button>
        </div>
      </div>
    </div>
  );
}
