'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import Link from 'next/link';
import {
  ragMetadataBuild,
  ragMetadataBuildStatus,
  ragContentBuild,
  ragMetadataSearch,
  ragRetrieve,
  ragSynopsis,
  ragResearchBook,
  type RagMetadataSearchHit,
  type RagPassageHit,
  type RagResearchResult,
  type RagMetadataBuildStatus as BuildStatusType,
} from '@/common/api';

const POLL_INTERVAL_MS = 1500;

type SearchMode = 'metadata' | 'passages' | 'synopsis' | 'research';

// ── Small reusable components ─────────────────────────────────────────────────

function SectionBox({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-600 bg-slate-800/50 p-4">
      <h2 className="text-lg font-semibold text-slate-200 mb-3">{title}</h2>
      {children}
    </section>
  );
}

function ErrorBanner({ msg }: { msg: string }) {
  return (
    <div className="rounded-lg border border-red-800 bg-red-900/30 p-3 text-red-200 text-sm">
      {msg}
    </div>
  );
}

function BuildProgress({ status }: { status: BuildStatusType }) {
  return (
    <div className="mt-3 space-y-1">
      <div className="flex justify-between text-sm text-slate-400">
        <span>{status.message || 'Building…'}</span>
        {status.total > 0 && (
          <span>{status.current} / {status.total} ({status.percentage}%)</span>
        )}
      </div>
      <div className="h-2 rounded-full bg-slate-700 overflow-hidden">
        <div
          className="h-full bg-amber/60 transition-[width] duration-300"
          style={{ width: `${status.percentage}%` }}
        />
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function RagPage() {
  const [mode, setMode] = useState<SearchMode>('metadata');
  const [query, setQuery] = useState('');
  const [bookId, setBookId] = useState('');
  const [spoilers, setSpoilers] = useState(false);
  const [topK, setTopK] = useState(10);

  const [metaResults, setMetaResults] = useState<RagMetadataSearchHit[]>([]);
  const [passageResults, setPassageResults] = useState<RagPassageHit[]>([]);
  const [synopsis, setSynopsis] = useState<string | null>(null);
  const [synopsisTitle, setSynopsisTitle] = useState<string | null>(null);
  const [researchResult, setResearchResult] = useState<RagResearchResult | null>(null);

  const [searching, setSearching] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Index build state
  const [buildingMeta, setBuildingMeta] = useState(false);
  const [buildingContent, setBuildingContent] = useState(false);
  const [buildStatus, setBuildStatus] = useState<BuildStatusType | null>(null);
  const [buildMessage, setBuildMessage] = useState<string | null>(null);
  const [buildError, setBuildError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current); }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    setBuildingMeta(false);
    setBuildingContent(false);
  }, []);

  // ── Index build ─────────────────────────────────────────────────────────────

  async function handleBuild(type: 'metadata' | 'content', force: boolean) {
    setBuildError(null);
    setBuildMessage(null);
    setBuildStatus(null);
    if (type === 'metadata') setBuildingMeta(true);
    else setBuildingContent(true);

    try {
      const res = type === 'metadata'
        ? await ragMetadataBuild(force)
        : await ragContentBuild(force);

      if (res.error || res.success === false) {
        setBuildError(res.error ?? res.message ?? 'Build failed');
        stopPolling();
        return;
      }
      if (res.status === 'started') {
        const poll = async () => {
          try {
            const status = await ragMetadataBuildStatus();
            setBuildStatus(status);
            if (status.status === 'done') {
              stopPolling();
              setBuildMessage(status.total ? `Indexed ${status.total} books.` : (status.message || 'Done.'));
            } else if (status.status === 'error') {
              stopPolling();
              setBuildError(status.message || 'Build failed');
            }
          } catch { /* keep polling on transient errors */ }
        };
        await poll();
        pollRef.current = setInterval(poll, POLL_INTERVAL_MS);
      } else {
        setBuildMessage(res.message ?? `Done.`);
        stopPolling();
      }
    } catch (e) {
      setBuildError(e instanceof Error ? e.message : 'Build failed');
      stopPolling();
    }
  }

  // ── Search / synopsis ───────────────────────────────────────────────────────

  async function handleSearch() {
    setError(null);
    setMessage(null);
    setMetaResults([]);
    setPassageResults([]);
    setSynopsis(null);
    setSynopsisTitle(null);
    setResearchResult(null);
    setSearching(true);

    try {
      if (mode === 'metadata') {
        if (!query.trim()) return;
        const res = await ragMetadataSearch(query.trim(), topK);
        setMetaResults(res.results ?? []);
        if (res.error) setError(res.error);
        else if ((res.results ?? []).length === 0) setMessage('No results — is the metadata index built?');

      } else if (mode === 'passages') {
        if (!query.trim()) return;
        const res = await ragRetrieve(query.trim(), topK);
        setPassageResults(res.hits ?? []);
        if (res.error) setError(res.error);
        else if ((res.hits ?? []).length === 0) setMessage('No results — is the content index built?');

      } else if (mode === 'synopsis') {
        const id = parseInt(bookId.trim());
        if (!id || isNaN(id)) { setError('Enter a numeric book ID.'); return; }
        const res = await ragSynopsis(id, spoilers);
        if (res.error) setError(res.error);
        else {
          setSynopsis(res.synopsis);
          setSynopsisTitle(res.title ?? null);
        }

      } else if (mode === 'research') {
        const id = parseInt(bookId.trim());
        if (!id || isNaN(id)) { setError('Enter a numeric book ID.'); return; }
        const res = await ragResearchBook(id, spoilers);
        if (!res.success) setError(res.error ?? 'Research failed');
        else setResearchResult(res);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Request failed');
    } finally {
      setSearching(false);
    }
  }

  const canSearch =
    mode === 'synopsis' || mode === 'research'
      ? bookId.trim().length > 0
      : query.trim().length > 0;

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">RAG Search</h1>
        <p className="text-slate-400 mt-1">
          Semantic search over your library using LanceDB. Metadata search works on titles,
          authors, tags and comments. Passage search works on full book text.
          Build the relevant index before first use.
        </p>
      </div>

      {/* ── Index build ── */}
      <SectionBox title="Indexes">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-slate-400 mb-2">
              <span className="text-slate-200 font-medium">Metadata index</span> — titles, authors,
              tags, comments. Fast to build (~seconds).
            </p>
            <div className="flex gap-2">
              <button type="button" onClick={() => handleBuild('metadata', false)}
                disabled={buildingMeta || buildingContent}
                className="px-3 py-1.5 rounded-lg bg-amber/20 text-amber text-sm font-medium hover:bg-amber/30 disabled:opacity-50">
                {buildingMeta ? 'Building…' : 'Build'}
              </button>
              <button type="button" onClick={() => handleBuild('metadata', true)}
                disabled={buildingMeta || buildingContent}
                className="px-3 py-1.5 rounded-lg bg-slate-600 text-slate-300 text-sm hover:bg-slate-500 disabled:opacity-50">
                Rebuild
              </button>
            </div>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-2">
              <span className="text-slate-200 font-medium">Content index</span> — full book text.
              Slow to build (minutes for large libraries).
            </p>
            <div className="flex gap-2">
              <button type="button" onClick={() => handleBuild('content', false)}
                disabled={buildingMeta || buildingContent}
                className="px-3 py-1.5 rounded-lg bg-amber/20 text-amber text-sm font-medium hover:bg-amber/30 disabled:opacity-50">
                {buildingContent ? 'Building…' : 'Build'}
              </button>
              <button type="button" onClick={() => handleBuild('content', true)}
                disabled={buildingMeta || buildingContent}
                className="px-3 py-1.5 rounded-lg bg-slate-600 text-slate-300 text-sm hover:bg-slate-500 disabled:opacity-50">
                Rebuild
              </button>
            </div>
          </div>
        </div>
        {(buildingMeta || buildingContent) && buildStatus && <BuildProgress status={buildStatus} />}
        {buildMessage && <p className="mt-2 text-sm text-slate-300">{buildMessage}</p>}
        {buildError && <p className="mt-2 text-sm text-red-300">{buildError}</p>}
      </SectionBox>

      {/* ── Mode tabs ── */}
      <div className="flex gap-1 border border-slate-600 rounded-lg p-1 bg-slate-800/50 w-fit">
        {(['metadata', 'passages', 'synopsis', 'research'] as SearchMode[]).map((m) => (
          <button key={m} type="button" onClick={() => { setMode(m); setError(null); setMessage(null); }}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors capitalize ${
              mode === m
                ? 'bg-amber/20 text-amber'
                : 'text-slate-400 hover:text-slate-200'
            }`}>
            {m === 'metadata' ? 'Metadata' : m === 'passages' ? 'Passages' : m === 'synopsis' ? 'Synopsis' : 'Research'}
          </button>
        ))}
      </div>

      {/* ── Query input ── */}
      <SectionBox title={
        mode === 'metadata' ? 'Semantic metadata search'
        : mode === 'passages' ? 'Passage retrieval'
        : mode === 'synopsis' ? 'Book synopsis'
        : 'Deep book research'
      }>
        {(mode === 'synopsis' || mode === 'research') ? (
          <div className="space-y-3">
            <div>
              <label className="text-sm text-slate-400 block mb-1">Book ID</label>
              <input
                type="number"
                value={bookId}
                onChange={(e) => setBookId(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="e.g. 1234"
                className="w-48 rounded-lg border border-slate-600 bg-slate-900 text-slate-100 px-3 py-2 placeholder-slate-500"
              />
              <p className="text-xs text-slate-500 mt-1">
                Find the ID in the book URL: /book/1234
              </p>
            </div>
            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
              <input type="checkbox" checked={spoilers}
                onChange={(e) => setSpoilers(e.target.checked)}
                className="rounded border-slate-600 bg-slate-800 text-amber" />
              Include spoilers
            </label>
            {mode === 'research' && (
              <p className="text-xs text-slate-500">
                Fetches Wikipedia, SF Encyclopedia, TVTropes, Open Library + your Calibre data.
                Takes 10–30 seconds. Requires Claude Desktop / Cursor (LLM sampling).
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-slate-400">
              {mode === 'metadata'
                ? 'e.g. "orbital megastructures with melancholy tone", "Japanese mystery light novels"'
                : 'e.g. "Zakalwe manipulated into accepting a mission", "the ship minds discussing ethics"'}
            </p>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Describe what you're looking for…"
              className="w-full rounded-lg border border-slate-600 bg-slate-900 text-slate-100 px-3 py-2 placeholder-slate-500"
            />
          </div>
        )}

        <div className="flex items-center gap-3 mt-3">
          <button
            type="button"
            onClick={handleSearch}
            disabled={searching || !canSearch}
            className="px-4 py-2 rounded-lg bg-amber/20 text-amber font-medium hover:bg-amber/30 disabled:opacity-50"
          >
            {searching ? 'Working…' : mode === 'synopsis' ? 'Generate synopsis' : mode === 'research' ? 'Research book' : 'Search'}
          </button>
          {mode !== 'synopsis' && mode !== 'research' && (
            <label className="flex items-center gap-2 text-sm text-slate-400">
              <span>Results</span>
              <select value={topK} onChange={(e) => setTopK(parseInt(e.target.value))}
                className="rounded border border-slate-600 bg-slate-900 text-slate-200 px-2 py-1 text-sm">
                {[5, 10, 20, 50].map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </label>
          )}
        </div>
      </SectionBox>

      {/* ── Feedback ── */}
      {error && <ErrorBanner msg={error} />}
      {message && !error && <p className="text-slate-400 text-sm">{message}</p>}

      {/* ── Metadata results ── */}
      {mode === 'metadata' && metaResults.length > 0 && (
        <ul className="space-y-2">
          {metaResults.map((hit, i) => (
            <li key={`${hit.book_id}-${i}`}
              className="rounded-lg border border-slate-600 bg-slate-800/50 p-3 flex items-start gap-3">
              <span className="text-xs text-slate-500 mt-0.5 w-5 shrink-0 text-right">{i + 1}</span>
              <div className="min-w-0">
                <Link href={`/book/${hit.book_id}`}
                  className="font-medium text-amber hover:underline truncate block">
                  {hit.title}
                </Link>
                {hit.text && (
                  <p className="text-sm text-slate-400 mt-1 line-clamp-2">{hit.text}</p>
                )}
                {hit.score !== undefined && (
                  <span className="text-xs text-slate-600 mt-1 block">
                    score {hit.score.toFixed(3)}
                  </span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* ── Passage results ── */}
      {mode === 'passages' && passageResults.length > 0 && (
        <ul className="space-y-3">
          {passageResults.map((hit, i) => (
            <li key={`${hit.book_id ?? hit.arxiv_id}-${hit.chunk_idx}-${i}`}
              className="rounded-lg border border-slate-600 bg-slate-800/50 p-3">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  {hit.book_id ? (
                    <Link href={`/book/${hit.book_id}`}
                      className="font-medium text-amber hover:underline">
                      {hit.title}
                    </Link>
                  ) : (
                    <span className="font-medium text-slate-200">{hit.title}</span>
                  )}
                  {hit.published && (
                    <span className="text-xs text-slate-500 ml-2">{hit.published}</span>
                  )}
                </div>
                <span className="text-xs text-slate-500 shrink-0">#{i + 1}</span>
              </div>
              <p
                className="text-sm text-slate-300 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: hit.snippet }}
              />
              {hit.chunk_idx !== undefined && (
                <span className="text-xs text-slate-600 mt-1 block">chunk {hit.chunk_idx}</span>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* ── Synopsis ── */}
      {mode === 'synopsis' && synopsis && (
        <div className="rounded-lg border border-slate-600 bg-slate-800/50 p-4">
          {synopsisTitle && (
            <h3 className="font-semibold text-slate-100 mb-3">{synopsisTitle}</h3>
          )}
          <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">{synopsis}</p>
          {spoilers && (
            <p className="text-xs text-amber/60 mt-3">⚠ Synopsis includes spoilers</p>
          )}
        </div>
      )}

      {/* ── Research report ── */}
      {mode === 'research' && researchResult?.report && (
        <div className="space-y-3">
          {/* Source attribution bar */}
          <div className="flex flex-wrap gap-2 text-xs">
            {researchResult.sources_fetched.map((s) => (
              <span key={s}
                className="px-2 py-0.5 rounded-full bg-emerald-900/40 text-emerald-300 border border-emerald-700/40">
                ✓ {s.replace(/_/g, ' ')}
              </span>
            ))}
            {researchResult.sources_failed.map((s) => (
              <span key={s}
                className="px-2 py-0.5 rounded-full bg-slate-700/60 text-slate-500 border border-slate-600/40">
                ✗ {s.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
          {/* Local data badges */}
          {researchResult.local_data && (
            <div className="flex flex-wrap gap-2 text-xs text-slate-400">
              {researchResult.local_data.rating && (
                <span>Your rating: {'★'.repeat(researchResult.local_data.rating)}{'☆'.repeat(5 - researchResult.local_data.rating)}</span>
              )}
              {researchResult.local_data.series && (
                <span>Series: {researchResult.local_data.series}</span>
              )}
              {researchResult.local_data.personal_notes && (
                <span className="text-amber/70">✎ personal notes included</span>
              )}
              {(researchResult.local_data.rag_passages ?? 0) > 0 && (
                <span>{researchResult.local_data.rag_passages} RAG passages included</span>
              )}
            </div>
          )}
          {/* The report itself — rendered as preformatted markdown */}
          <div className="rounded-lg border border-slate-600 bg-slate-800/50 p-5">
            <pre className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-sans">
              {researchResult.report}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
