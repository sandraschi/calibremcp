'use client';

import { ExternalLink, X } from 'lucide-react';
import { useEffect, useState } from 'react';

interface Bio {
  title: string;
  extract: string;
  pageUrl: string;
  thumbnail?: string;
}

/** "Who is that?" — live Wikipedia bio for an unfamiliar author. No invented facts. */
export function DelphiAuthorModal({
  author,
  shopUrl,
  onClose,
}: {
  author: string;
  shopUrl?: string;
  onClose: () => void;
}) {
  const [bio, setBio] = useState<Bio | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setBio(null);
    setError(null);
    (async () => {
      try {
        const op = await fetch(
          `https://en.wikipedia.org/w/api.php?action=opensearch&search=${encodeURIComponent(author)}&limit=1&namespace=0&format=json&origin=*`,
        );
        if (!op.ok) throw new Error('Wikipedia search failed');
        const found = (await op.json()) as unknown[];
        const title =
          Array.isArray(found) && Array.isArray(found[1]) ? String(found[1][0] ?? '') : '';
        if (!title) throw new Error('No Wikipedia article found');
        const rs = await fetch(
          `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`,
        );
        if (!rs.ok) throw new Error('Wikipedia summary failed');
        const sum = (await rs.json()) as {
          title?: string;
          extract?: string;
          content_urls?: { desktop?: { page?: string } };
          thumbnail?: { source?: string };
        };
        if (!cancelled) {
          setBio({
            title: sum.title ?? title,
            extract: sum.extract ?? '',
            pageUrl:
              sum.content_urls?.desktop?.page ??
              `https://en.wikipedia.org/wiki/${encodeURIComponent(title)}`,
            thumbnail: sum.thumbnail?.source,
          });
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [author]);

  return (
    <div
      className="fixed inset-0 z-[120] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`Who is ${author}`}
    >
      <div
        className="bg-slate-900 border border-slate-700 rounded-lg shadow-2xl max-w-lg w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 mb-3">
          <h3 className="text-lg font-semibold text-slate-100">{author}</h3>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="p-1 rounded-md text-slate-400 hover:text-slate-100 hover:bg-slate-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        {!bio && !error && <p className="text-sm text-slate-400">Asking Wikipedia…</p>}
        {error && <p className="text-sm text-slate-400">No bio found ({error}).</p>}
        {bio && (
          <>
            {bio.thumbnail && (
              <img
                src={bio.thumbnail}
                alt=""
                className="float-right ml-3 mb-2 w-24 rounded-md border border-slate-700"
              />
            )}
            <p className="text-sm leading-relaxed text-slate-300">{bio.extract}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <a
                href={bio.pageUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-md bg-slate-700 text-slate-200 hover:bg-slate-600"
              >
                Wikipedia <ExternalLink className="w-3 h-3" />
              </a>
              {shopUrl && (
                <a
                  href={shopUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-md bg-amber text-slate-900 font-medium hover:bg-amber/90"
                >
                  Delphi shop <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
