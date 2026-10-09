'use client';

import {
  appendBookComment,
  createBookComment,
  deleteBook,
  deleteBookComment,
  downloadBookFile,
  getBookComment,
  getBookDetails,
  getBookFilePath,
  replaceBookComment,
  updateBook,
} from '@/common/api';
import { useEffect, useState } from 'react';

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
        {label}
      </span>
      {children}
    </div>
  );
}

const inputCls =
  'w-full px-2.5 py-1.5 text-sm bg-slate-900 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber';
const btnCls =
  'px-3 py-1.5 text-xs font-medium rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600 disabled:opacity-50';

export function BookManagePanel({
  bookId,
  onChanged,
  onDeleted,
}: {
  bookId: number;
  onChanged: () => void;
  onDeleted: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  // Edit form
  const [title, setTitle] = useState('');
  const [rating, setRating] = useState('');
  const [publisher, setPublisher] = useState('');
  const [tags, setTags] = useState('');

  // Comments
  const [comment, setComment] = useState<string | null>(null);
  const [commentDraft, setCommentDraft] = useState('');
  const [commentLoaded, setCommentLoaded] = useState(false);

  // File + details
  const [fileInfo, setFileInfo] = useState<string | null>(null);
  const [detailsJson, setDetailsJson] = useState<string | null>(null);

  useEffect(() => {
    if (!open || commentLoaded) return;
    getBookComment(bookId)
      .then((r) => {
        const text =
          (r as { text?: string }).text ??
          (r as { comment?: string }).comment ??
          (r as { result?: string }).result ??
          null;
        setComment(typeof text === 'string' ? text : null);
        setCommentDraft(typeof text === 'string' ? text : '');
        setCommentLoaded(true);
      })
      .catch(() => setCommentLoaded(true));
  }, [open, commentLoaded, bookId]);

  const run = async (label: string, fn: () => Promise<unknown>, after?: () => void) => {
    setBusy(label);
    setMsg(null);
    setErr(null);
    try {
      await fn();
      setMsg(`${label} done.`);
      after?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : `${label} failed`);
    } finally {
      setBusy(null);
    }
  };

  const handleSave = () =>
    run(
      'Save',
      async () => {
        const metadata: Record<string, unknown> = {};
        if (title.trim()) metadata.title = title.trim();
        if (publisher.trim()) metadata.publisher = publisher.trim();
        if (rating) metadata.rating = Number(rating);
        if (tags.trim())
          metadata.tags = tags
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean);
        if (Object.keys(metadata).length === 0)
          throw new Error('Nothing to save — fill a field first');
        await updateBook(bookId, { metadata });
        setTitle('');
        setRating('');
        setPublisher('');
        setTags('');
      },
      onChanged,
    );

  const handleDelete = () => {
    if (!window.confirm(`Delete book ${bookId} from the library (files too)?`)) return;
    run('Delete', () => deleteBook(bookId, true), onDeleted);
  };

  const handleCommentSave = (mode: 'create' | 'replace' | 'append') =>
    run(
      mode === 'create' ? 'Create comment' : mode === 'replace' ? 'Replace comment' : 'Append',
      async () => {
        if (!commentDraft.trim()) throw new Error('Comment is empty');
        if (mode === 'create') await createBookComment(bookId, commentDraft);
        else if (mode === 'replace') await replaceBookComment(bookId, commentDraft);
        else await appendBookComment(bookId, commentDraft);
        const r = await getBookComment(bookId);
        const text =
          (r as { text?: string }).text ?? (r as { comment?: string }).comment ?? commentDraft;
        setComment(typeof text === 'string' ? text : commentDraft);
      },
      onChanged,
    );

  const handleFileInfo = () =>
    run('File info', async () => {
      const [fp, dl] = await Promise.all([
        getBookFilePath(bookId).catch((e) => ({ error: String(e) })),
        downloadBookFile(bookId).catch((e) => ({ error: String(e) })),
      ]);
      setFileInfo(JSON.stringify({ file_path: fp, download: dl }, null, 1).slice(0, 1500));
    });

  const handleDetails = () =>
    run('Details', async () => {
      const d = await getBookDetails(bookId);
      setDetailsJson(JSON.stringify(d, null, 1).slice(0, 4000));
    });

  return (
    <div className="mt-4 rounded-lg border border-slate-600 bg-slate-900/40">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        data-testid="book-manage-toggle"
        className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400 hover:text-slate-200"
      >
        <span>Manage book</span>
        <span className="text-amber">{open ? '−' : '+'}</span>
      </button>
      {open && (
        <div className="px-3 pb-3 space-y-3" data-testid="book-manage-panel">
          <Row label="Edit metadata">
            <div className="grid grid-cols-2 gap-2">
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="New title"
                className={inputCls}
              />
              <input
                value={publisher}
                onChange={(e) => setPublisher(e.target.value)}
                placeholder="Publisher"
                className={inputCls}
              />
              <select
                value={rating}
                onChange={(e) => setRating(e.target.value)}
                className={inputCls}
              >
                <option value="">Rating…</option>
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>
                    {n} stars
                  </option>
                ))}
              </select>
              <input
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="Tags, comma separated"
                className={inputCls}
              />
            </div>
            <div>
              <button
                type="button"
                disabled={busy !== null}
                onClick={handleSave}
                className="px-3 py-1.5 text-xs font-medium rounded-md bg-amber text-slate-900 hover:bg-amber/90 disabled:opacity-50"
              >
                {busy === 'Save' ? 'Saving…' : 'Save changes'}
              </button>
            </div>
          </Row>
          <Row label="Review comment">
            {comment ? (
              <p className="text-xs text-slate-400 max-h-20 overflow-auto rounded bg-slate-900 p-2">
                {comment.slice(0, 500)}
              </p>
            ) : (
              <p className="text-xs text-slate-600 italic">No review comment stored.</p>
            )}
            <textarea
              value={commentDraft}
              onChange={(e) => setCommentDraft(e.target.value)}
              rows={2}
              placeholder="Write a review note…"
              className={inputCls}
            />
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                disabled={busy !== null}
                onClick={() => handleCommentSave('create')}
                className={btnCls}
              >
                Create
              </button>
              <button
                type="button"
                disabled={busy !== null}
                onClick={() => handleCommentSave('replace')}
                className={btnCls}
              >
                Replace
              </button>
              <button
                type="button"
                disabled={busy !== null}
                onClick={() => handleCommentSave('append')}
                className={btnCls}
              >
                Append
              </button>
              <button
                type="button"
                disabled={busy !== null}
                onClick={() =>
                  run('Delete comment', () =>
                    deleteBookComment(bookId).then(() => {
                      setComment(null);
                      setCommentDraft('');
                    }),
                  )
                }
                className="px-3 py-1.5 text-xs rounded-md bg-red-900/60 text-red-200 hover:bg-red-900 disabled:opacity-50"
              >
                Delete
              </button>
            </div>
          </Row>
          <Row label="File & full details">
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                disabled={busy !== null}
                onClick={handleFileInfo}
                className={btnCls}
              >
                File info
              </button>
              <button
                type="button"
                disabled={busy !== null}
                onClick={handleDetails}
                className={btnCls}
              >
                Full details
              </button>
              <button
                type="button"
                disabled={busy !== null}
                onClick={handleDelete}
                className="px-3 py-1.5 text-xs rounded-md bg-red-900/60 text-red-200 hover:bg-red-900 disabled:opacity-50"
              >
                {busy === 'Delete' ? 'Deleting…' : 'Delete book'}
              </button>
            </div>
            {fileInfo && (
              <pre className="text-[11px] text-slate-400 whitespace-pre-wrap font-sans max-h-32 overflow-auto rounded bg-slate-900 p-2">
                {fileInfo}
              </pre>
            )}
            {detailsJson && (
              <pre className="text-[11px] text-slate-400 whitespace-pre-wrap font-sans max-h-48 overflow-auto rounded bg-slate-900 p-2">
                {detailsJson}
              </pre>
            )}
          </Row>
          {msg && <p className="text-xs text-emerald-400">{msg}</p>}
          {err && <p className="text-xs text-red-400">{err}</p>}
        </div>
      )}
    </div>
  );
}
