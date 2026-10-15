'use client';

import {
  type CanonEntry,
  type CanonResult,
  canonCheckList,
  canonGutenbergTop100,
  canonNobelLaureates,
} from '@/common/api';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useCallback, useEffect, useState } from 'react';

type CanonId = 'gutenberg' | 'nobel' | 'paste';

function parseCanon(raw: string | null | undefined): CanonId {
  return raw === 'nobel' || raw === 'paste' ? raw : 'gutenberg';
}

function entryTitle(e: CanonEntry): string {
  return e.title ?? e.name ?? 'Untitled';
}

function entrySub(e: CanonEntry): string {
  const bits: string[] = [];
  if (e.author) bits.push(e.author);
  if (e.year != null) bits.push(String(e.year));
  if (e.rank != null) bits.push(`#${e.rank}`);
  if (e.downloads != null) bits.push(`${e.downloads.toLocaleString()} downloads`);
  return bits.join(' · ');
}

function CanonTabs({ canon }: { canon: CanonId }) {
  const tabs: { id: CanonId; label: string; hint: string }[] = [
    { id: 'gutenberg', label: 'Gutenberg Top 100', hint: 'Live downloads, title-level' },
    { id: 'nobel', label: 'Nobel Laureates', hint: 'Live API, author-level' },
    { id: 'paste', label: 'Paste a list', hint: 'Your own canon, e.g. Mustich slice' },
  ];
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
      {tabs.map((t) => (
        <Link
          key={t.id}
          href={t.id === 'gutenberg' ? '/canon' : `/canon?canon=${t.id}`}
          className={`block p-4 rounded-lg border transition-colors ${
            canon === t.id
              ? 'bg-amber/10 border-amber/60'
              : 'bg-slate-800 border-slate-600 hover:border-amber/50'
          }`}
        >
          <span className={`font-medium ${canon === t.id ? 'text-amber' : 'text-slate-200'}`}>
            {t.label}
          </span>
          <span className="block text-xs text-slate-500 mt-1">{t.hint}</span>
        </Link>
      ))}
    </div>
  );
}

function CoverageBar({ result }: { result: CanonResult }) {
  return (
    <div className="mb-6 rounded-lg bg-slate-800/60 border border-slate-700 p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2 mb-2">
        <p className="text-2xl font-bold text-slate-100">
          {result.coverage_pct}
          <span className="text-base text-slate-400">%</span>
        </p>
        <p className="text-sm text-slate-400">
          {result.owned_count} owned · {result.missing_count} missing · {result.total} total
        </p>
      </div>
      <div className="h-2.5 rounded-full bg-slate-900 overflow-hidden">
        <div
          className="h-full rounded-full bg-amber"
          style={{ width: `${result.coverage_pct}%` }}
        />
      </div>
    </div>
  );
}

function MissingTable({ rows, showGutenberg }: { rows: CanonEntry[]; showGutenberg: boolean }) {
  if (rows.length === 0) {
    return <p className="text-sm text-slate-400">Nothing missing. Impressive shelf.</p>;
  }
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700">
      <table className="w-full text-sm">
        <thead className="bg-slate-800">
          <tr>
            <th className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-amber">
              Missing
            </th>
            <th className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-amber">
              Get it
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700/60">
          {rows.map((e, i) => (
            <tr key={`${entryTitle(e)}-${i}`}>
              <td className="px-3 py-2 align-top">
                <span className="text-slate-200">{entryTitle(e)}</span>
                {entrySub(e) && <span className="block text-xs text-slate-500">{entrySub(e)}</span>}
                {e.motivation && (
                  <span className="block text-xs text-slate-500 italic mt-0.5 line-clamp-2">
                    {e.motivation}
                  </span>
                )}
              </td>
              <td className="px-3 py-2 align-top whitespace-nowrap">
                {showGutenberg && e.gutenberg_id != null ? (
                  <Link
                    href="/import"
                    title={`Import Gutenberg #${e.gutenberg_id} via the Import page`}
                    className="px-3 py-1.5 text-xs rounded-md bg-amber text-slate-900 font-medium hover:bg-amber/90"
                  >
                    Import #{e.gutenberg_id}
                  </Link>
                ) : (
                  <span className="text-xs text-slate-500">Buy / source</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CanonPageInner() {
  const searchParams = useSearchParams();
  const canon = parseCanon(searchParams?.get('canon'));
  const [result, setResult] = useState<CanonResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(canon !== 'paste');
  const [paste, setPaste] = useState('');
  const [checking, setChecking] = useState(false);

  const load = useCallback(async () => {
    if (canon === 'paste') return;
    setLoading(true);
    setError(null);
    try {
      const res = canon === 'nobel' ? await canonNobelLaureates() : await canonGutenbergTop100(100);
      if (!res.success) throw new Error(res.error ?? 'Coverage check failed');
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [canon]);

  useEffect(() => {
    setResult(null);
    setError(null);
    setLoading(canon !== 'paste');
    if (canon === 'paste') return;
    let cancelled = false;
    (async () => {
      try {
        const res =
          canon === 'nobel' ? await canonNobelLaureates() : await canonGutenbergTop100(100);
        if (!cancelled) {
          if (!res.success) throw new Error(res.error ?? 'Coverage check failed');
          setResult(res);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [canon]);

  const runPasteCheck = async () => {
    const parsed = paste
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean)
      .map((line) => {
        const m = /^(.*?)\s+[—–-]\s+(.+)$/.exec(line) ?? /^(.*?)\s+by\s+(.+)$/i.exec(line);
        return m ? { title: m[1].trim(), author: m[2].trim() } : { title: line };
      });
    if (parsed.length === 0) {
      setError('Paste at least one "Title — Author" line.');
      return;
    }
    setChecking(true);
    setError(null);
    try {
      const res = await canonCheckList(parsed.slice(0, 200));
      if (!res.success) throw new Error(res.error ?? 'Coverage check failed');
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-5xl">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Canon Coverage</h1>
      <p className="text-sm text-slate-400 mb-4">
        What the canon holds that your shelves don&apos;t — the gap finder. Lists are fetched live
        or pasted by you; nothing is invented.
      </p>
      <div className="mb-6 rounded-lg border border-amber/50 bg-amber-500/10 p-4">
        <p className="text-sm text-slate-200">
          <span className="font-semibold text-amber">Building on a budget?</span>{' '}
          <a
            href="https://www.delphiclassics.com"
            target="_blank"
            rel="noreferrer"
            className="text-amber hover:underline font-medium"
          >
            Delphi Classics Complete Works
          </a>{' '}
          — entire oeuvres in single illustrated files for a few dollars each (Gaskell: 69 works in
          one file). Indexed Delphi volumes count toward your coverage automatically, work by work.
        </p>
      </div>
      <CanonTabs canon={canon} />

      {canon === 'paste' && (
        <div className="mb-6 rounded-lg bg-slate-800/60 border border-slate-700 p-4">
          <p className="text-sm text-slate-300 mb-2">
            One per line: <span className="font-mono text-amber-200">Title — Author</span> (author
            optional). Ask your LLM for a Mustich slice, paste it here.
          </p>
          <textarea
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
            rows={6}
            placeholder={
              'The Scarlet Pimpernel — Baroness Orczy\nThe Left Hand of Darkness — Ursula K. Le Guin'
            }
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-600 text-slate-200 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-amber"
          />
          <button
            type="button"
            onClick={runPasteCheck}
            disabled={checking || !paste.trim()}
            className="mt-2 px-4 py-2 text-sm font-medium rounded-md bg-amber text-slate-900 hover:bg-amber/90 disabled:opacity-50"
          >
            {checking ? 'Checking…' : 'Check coverage'}
          </button>
        </div>
      )}

      {loading ? (
        <p className="text-slate-400">
          Checking {result?.total ?? '…'} titles against your library…
        </p>
      ) : error || !result ? (
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
          <p className="font-medium">Coverage check failed</p>
          <p className="mt-2 text-sm text-slate-400">{error ?? 'Unknown error'}</p>
          <button
            type="button"
            onClick={load}
            className="mt-3 px-3 py-1.5 text-sm rounded-md bg-slate-700 hover:bg-slate-600"
          >
            Retry
          </button>
        </div>
      ) : (
        <>
          <CoverageBar result={result} />
          <h2 className="text-lg font-semibold text-slate-200 mb-2">
            Missing ({result.missing_count})
          </h2>
          <MissingTable rows={result.missing} showGutenberg={canon === 'gutenberg'} />
          {result.owned.length > 0 && (
            <details className="mt-6">
              <summary className="text-sm text-slate-400 hover:text-amber cursor-pointer">
                Owned ({result.owned_count}) — show
              </summary>
              <ul className="mt-2 space-y-1">
                {result.owned.map((e, i) => (
                  <li key={`${entryTitle(e)}-${i}`} className="text-sm text-slate-400">
                    {entryTitle(e)}
                    {entrySub(e) && <span className="text-slate-600"> · {entrySub(e)}</span>}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
    </div>
  );
}

export default function CanonPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading…</p>
        </div>
      }
    >
      <CanonPageInner />
    </Suspense>
  );
}
