'use client';

import { useState, useCallback } from 'react';
import {
  searchAnnas,
  getAnnasMirrors,
  downloadAnnas,
  searchGutenberg,
  importGutenberg,
  searchArxiv,
  importArxiv,
  listLibraries,
  type AnnasSearchResult,
  type GutenbergSearchResult,
  type ArxivSearchResult,
  type Library,
} from '@/common/api';
import { useEffect } from 'react';

type Tab = 'annas' | 'gutenberg' | 'arxiv' | 'local';

export default function ImportPage() {
  const [activeTab, setActiveTab] = useState<Tab>('annas');
  
  // Anna's Archive State
  const [annasQuery, setAnnasQuery] = useState('');
  const [annasLoading, setAnnasLoading] = useState(false);
  const [annasResults, setAnnasResults] = useState<AnnasSearchResult[]>([]);
  const [annasError, setAnnasError] = useState<string | null>(null);
  const [importingMd5, setImportingMd5] = useState<string | null>(null);
  const [restrictedMd5s, setRestrictedMd5s] = useState<Record<string, boolean>>({});

  // Gutenberg State
  const [gutenQuery, setGutenQuery] = useState('');
  const [gutenLoading, setGutenLoading] = useState(false);
  const [gutenResults, setGutenResults] = useState<GutenbergSearchResult[]>([]);
  const [gutenError, setGutenError] = useState<string | null>(null);
  const [importingGutenId, setImportingGutenId] = useState<number | null>(null);

  // arXiv State
  const [arxivQuery, setArxivQuery] = useState('');
  const [arxivLoading, setArxivLoading] = useState(false);
  const [arxivResults, setArxivResults] = useState<ArxivSearchResult[]>([]);
  const [arxivError, setArxivError] = useState<string | null>(null);
  const [importingArxivId, setImportingArxivId] = useState<string | null>(null);

  // Local Import State
  const [localPath, setLocalPath] = useState('');
  const [localLoading, setLocalLoading] = useState(false);
  
  // Global Import Settings
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [selectedLibraryPath, setSelectedLibraryPath] = useState<string>('');
  const [globalTags, setGlobalTags] = useState('');
  const [globalSeries, setGlobalSeries] = useState('');
  const [showOptions, setShowOptions] = useState(false);

  // Shared Result
  const [globalResult, setGlobalResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    listLibraries().then(res => {
      setLibraries(res.libraries);
      const active = res.libraries.find(l => l.is_active);
      if (active) setSelectedLibraryPath(active.path);
    }).catch(console.error);
  }, []);

  const getImportOptions = () => ({
    tags: globalTags ? globalTags.split(',').map(t => t.trim()).filter(Boolean) : undefined,
    series: globalSeries.trim() || undefined,
    library_path: selectedLibraryPath || undefined,
  });

  const showGlobalResult = (success: boolean, message: string) => {
    setGlobalResult({ success, message });
    setTimeout(() => setGlobalResult(null), 5000);
  };

  const handleAnnasSearch = useCallback(async () => {
    if (!annasQuery.trim()) return;
    setAnnasLoading(true);
    setAnnasError(null);
    setAnnasResults([]);
    setRestrictedMd5s({});
    try {
      const mirrors = await getAnnasMirrors();
      const resp = await searchAnnas({
        query: annasQuery.trim(),
        max_results: 24,
        mirrors: mirrors.length > 0 ? mirrors : undefined,
      });
      if (resp.success) {
        setAnnasResults(resp.results);
        if (resp.results.length === 0 && !resp.error) {
          setAnnasError('No results found. Try a different search.');
        }
      } else {
        setAnnasError(resp.error ?? 'Search failed');
      }
    } catch (e) {
      setAnnasError(e instanceof Error ? e.message : 'Search failed');
    } finally {
      setAnnasLoading(false);
    }
  }, [annasQuery]);

  const handleAnnasImport = async (md5: string, title: string) => {
    setImportingMd5(md5);
    setRestrictedMd5s(prev => ({ ...prev, [md5]: false }));
    try {
      const res = await downloadAnnas(md5, getImportOptions());
      if (res.success) {
        showGlobalResult(true, `Successfully imported: ${title}`);
      } else if (res.error_code === 'MANUAL_INTERACTION_REQUIRED') {
        setRestrictedMd5s(prev => ({ ...prev, [md5]: true }));
        showGlobalResult(false, 'Mirror restricted: This library requires manual download (e.g. CAPTCHA).');
      } else {
        showGlobalResult(false, res.message || 'Import failed');
      }
    } catch (e) {
      showGlobalResult(false, e instanceof Error ? e.message : 'Import failed');
    } finally {
      setImportingMd5(null);
    }
  };

  const handleGutenSearch = useCallback(async () => {
    if (!gutenQuery.trim()) return;
    setGutenLoading(true);
    setGutenError(null);
    setGutenResults([]);
    try {
      const resp = await searchGutenberg(gutenQuery.trim());
      if (resp.success) {
        setGutenResults(resp.results);
        if (resp.results.length === 0) {
          setGutenError('No results found.');
        }
      } else {
        setGutenError(resp.error ?? 'Search failed');
      }
    } catch (e) {
      setGutenError(e instanceof Error ? e.message : 'Search failed');
    } finally {
      setGutenLoading(false);
    }
  }, [gutenQuery]);

  const handleGutenImport = async (id: number, title: string) => {
    setImportingGutenId(id);
    try {
      const res = await importGutenberg(id, getImportOptions());
      if (res.success) {
        showGlobalResult(true, `Successfully imported: ${title}`);
      }
    } catch (e) {
      showGlobalResult(false, e instanceof Error ? e.message : 'Import failed');
    } finally {
      setImportingGutenId(null);
    }
  };

  const handleArxivSearch = useCallback(async () => {
    if (!arxivQuery.trim()) return;
    setArxivLoading(true);
    setArxivError(null);
    setArxivResults([]);
    try {
      const resp = await searchArxiv(arxivQuery.trim(), 24);
      if (resp.success) {
        setArxivResults(resp.results);
        if (resp.results.length === 0) {
          setArxivError('No results found.');
        }
      } else {
        setArxivError(resp.error ?? 'Search failed');
      }
    } catch (e) {
      setArxivError(e instanceof Error ? e.message : 'Search failed');
    } finally {
      setArxivLoading(false);
    }
  }, [arxivQuery]);

  const handleArxivImport = async (id: string, title: string) => {
    setImportingArxivId(id);
    try {
      const res = await importArxiv(id, getImportOptions());
      if (res.success) {
        showGlobalResult(true, `Successfully imported: ${title}`);
      }
    } catch (e) {
      showGlobalResult(false, e instanceof Error ? e.message : 'Import failed');
    } finally {
      setImportingArxivId(null);
    }
  };

  const handleLocalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!localPath.trim()) return;
    setLocalLoading(true);
    try {
      const opts = getImportOptions();
      const res = await fetch('/api/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          file_path: localPath.trim(), 
          fetch_metadata: true,
          tags: opts.tags,
          library_path: opts.library_path
        }),
      });
      const data = await res.json();
      if (res.ok) {
        showGlobalResult(true, `Imported: ${data.title ?? 'Book'}`);
        setLocalPath('');
      } else {
        showGlobalResult(false, data.detail ?? data.error ?? 'Import failed');
      }
    } catch (e) {
      showGlobalResult(false, e instanceof Error ? e.message : 'Request failed');
    } finally {
      setLocalLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-100 italic tracking-tight">
          IMPORT<span className="text-amber">HUB</span>
        </h1>
        {globalResult && (
          <div className={`px-4 py-2 rounded-lg text-sm font-bold shadow-lg animate-in fade-in slide-in-from-top-4 duration-300 ${
            globalResult.success ? 'bg-emerald-500 text-slate-900' : 'bg-red-500 text-white'
          }`}>
            {globalResult.message}
          </div>
        )}
      </div>

      <div className="flex gap-2 mb-8 bg-slate-800/50 p-1 rounded-xl w-fit border border-slate-700/50">
        <button
          onClick={() => setActiveTab('annas')}
          className={`px-6 py-2 rounded-lg font-bold transition-all ${activeTab === 'annas' ? 'bg-amber text-slate-900 shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
        >
          Anna&apos;s Archive
        </button>
        <button
          onClick={() => setActiveTab('gutenberg')}
          className={`px-6 py-2 rounded-lg font-bold transition-all ${activeTab === 'gutenberg' ? 'bg-amber text-slate-900 shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
        >
          Gutenberg
        </button>
        <button
          onClick={() => setActiveTab('arxiv')}
          className={`px-6 py-2 rounded-lg font-bold transition-all ${activeTab === 'arxiv' ? 'bg-amber text-slate-900 shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
        >
          arXiv
        </button>
        <button
          onClick={() => setActiveTab('local')}
          className={`px-6 py-2 rounded-lg font-bold transition-all ${activeTab === 'local' ? 'bg-amber text-slate-900 shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
        >
          Local File
        </button>

        <div className="ml-auto flex items-center gap-4">
          <button
            onClick={() => setShowOptions(!showOptions)}
            className={`px-4 py-2 rounded-lg text-xs font-bold border transition-all flex items-center gap-2 ${
              showOptions ? 'bg-amber/10 border-amber text-amber shadow-[0_0_15px_rgba(245,158,11,0.1)]' : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-500'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            IMPORT SETTINGS
          </button>
        </div>
      </div>

      {showOptions && (
        <div className="mb-8 p-6 bg-slate-800/40 border border-amber/20 rounded-2xl animate-in fade-in slide-in-from-top-4 duration-300">
          <h3 className="text-sm font-bold text-amber mb-4 uppercase tracking-widest flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber animate-pulse"></span>
            Global Import Defaults
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Target Library</label>
              <select
                aria-label="Select Target Library"
                value={selectedLibraryPath}
                onChange={(e) => setSelectedLibraryPath(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-amber/50 outline-none"
              >
                {libraries.map(lib => (
                  <option key={lib.path} value={lib.path}>{lib.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Default Tags (comma separated)</label>
              <input
                type="text"
                placeholder="e.g. AI, Physics, To Read"
                value={globalTags}
                onChange={(e) => setGlobalTags(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-amber/50 outline-none placeholder:text-slate-700"
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Force Series</label>
              <input
                type="text"
                placeholder="e.g. ArXiv Papers"
                value={globalSeries}
                onChange={(e) => setGlobalSeries(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-slate-200 focus:ring-2 focus:ring-amber/50 outline-none placeholder:text-slate-700"
              />
            </div>
          </div>
        </div>
      )}

      <div className="min-h-[400px]">
        {activeTab === 'annas' && (
          <div className="animate-in fade-in slide-in-from-left-4 duration-300">
            <div className="flex gap-3 mb-8">
              <input
                type="text"
                placeholder="Search Anna's Archive (Title, Author, ISBN...)"
                value={annasQuery}
                onChange={(e) => setAnnasQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAnnasSearch()}
                className="flex-1 px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber/50"
              />
              <button
                onClick={handleAnnasSearch}
                disabled={annasLoading}
                className="px-8 py-3 bg-amber text-slate-900 font-bold rounded-xl hover:bg-amber-400 active:scale-95 transition-all disabled:opacity-50"
              >
                {annasLoading ? 'SEARCHING...' : 'SEARCH'}
              </button>
              <a
                href="https://en.wikipedia.org/wiki/Anna%27s_Archive#Mirrors"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-3 bg-slate-800 text-slate-400 font-bold rounded-xl border border-slate-700 hover:text-amber hover:border-amber/50 transition-all flex items-center justify-center gap-2"
                title="Check working mirrors on Wikipedia"
              >
                <span className="text-xs">MIRRORS</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>

            {annasError && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl mb-8">{annasError}</div>}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {annasResults.map((book) => (
                <div key={book.detail_item} className="p-4 bg-slate-800/40 border border-slate-700/50 rounded-xl hover:border-amber/30 transition-all group">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-slate-100 line-clamp-1 group-hover:text-amber transition-colors">{book.title}</h3>
                    <span className="text-[10px] bg-slate-700 px-2 py-0.5 rounded text-slate-400 uppercase tracking-widest">{book.formats}</span>
                  </div>
                  <p className="text-sm text-slate-400 mb-4 line-clamp-1">{book.author}</p>
                  <div className="flex flex-col gap-2">
                    {restrictedMd5s[book.detail_item] && (
                      <div className="text-[10px] text-amber-500 font-bold bg-amber-500/10 p-2 rounded border border-amber-500/20 mb-1">
                        Landers found. Please use source page to handle CAPTCHA/timers manually.
                      </div>
                    )}
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAnnasImport(book.detail_item, book.title)}
                        disabled={importingMd5 === book.detail_item}
                        className={`flex-1 py-2 ${restrictedMd5s[book.detail_item] ? 'bg-amber-500/20 text-amber-500 border border-amber-500/30' : 'bg-slate-700 hover:bg-amber hover:text-slate-900 text-slate-200'} text-xs font-bold rounded-lg transition-all disabled:opacity-50`}
                      >
                        {importingMd5 === book.detail_item ? 'IMPORTING...' : restrictedMd5s[book.detail_item] ? 'RETRY DIRECT' : 'DIRECT IMPORT'}
                      </button>
                      <a
                        href={book.detail_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`px-4 py-2 ${restrictedMd5s[book.detail_item] ? 'bg-amber text-slate-900 border-amber' : 'bg-slate-800 border-slate-600 text-slate-400'} border hover:text-slate-200 text-xs font-bold rounded-lg transition-all flex items-center justify-center`}
                      >
                        {restrictedMd5s[book.detail_item] ? 'OPEN SOURCE' : 'SOURCE'}
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'gutenberg' && (
          <div className="animate-in fade-in slide-in-from-left-4 duration-300">
            <div className="flex gap-3 mb-8">
              <input
                type="text"
                placeholder="Search Project Gutenberg..."
                value={gutenQuery}
                onChange={(e) => setGutenQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGutenSearch()}
                className="flex-1 px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber/50"
              />
              <button
                onClick={handleGutenSearch}
                disabled={gutenLoading}
              className="px-8 py-3 bg-amber text-slate-900 font-bold rounded-xl hover:bg-amber-400 active:scale-95 transition-all disabled:opacity-50"
              >
                {gutenLoading ? 'SEARCHING...' : 'SEARCH'}
              </button>
            </div>

            {gutenError && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl mb-8">{gutenError}</div>}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {gutenResults.map((book) => (
                <div key={book.id} className="p-4 bg-slate-800/40 border border-slate-700/50 rounded-xl hover:border-amber/30 transition-all group">
                  <h3 className="font-bold text-slate-100 line-clamp-1 mb-1 group-hover:text-amber transition-colors">{book.title}</h3>
                  <p className="text-sm text-slate-400 mb-4 line-clamp-1">{book.authors.join(', ')}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleGutenImport(book.id, book.title)}
                      disabled={importingGutenId === book.id}
                      className="flex-1 py-2 bg-slate-700 hover:bg-amber hover:text-slate-900 text-slate-200 text-xs font-bold rounded-lg transition-all disabled:opacity-50"
                    >
                      {importingGutenId === book.id ? 'IMPORTING...' : 'IMPORT EPUB'}
                    </button>
                    <a
                      href={book.detail_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-slate-800 border border-slate-600 text-slate-400 hover:text-slate-200 text-xs font-bold rounded-lg transition-all"
                    >
                      SOURCE
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'arxiv' && (
          <div className="animate-in fade-in slide-in-from-left-4 duration-300">
            <div className="flex gap-3 mb-8">
              <input
                type="text"
                placeholder="Search arXiv (Title, Author, ID...)"
                value={arxivQuery}
                onChange={(e) => setArxivQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleArxivSearch()}
                className="flex-1 px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber/50"
              />
              <button
                onClick={handleArxivSearch}
                disabled={arxivLoading}
              className="px-8 py-3 bg-amber text-slate-900 font-bold rounded-xl hover:bg-amber-400 active:scale-95 transition-all disabled:opacity-50"
              >
                {arxivLoading ? 'SEARCHING...' : 'SEARCH'}
              </button>
            </div>

            {arxivError && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl mb-8">{arxivError}</div>}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {arxivResults.map((paper) => (
                <div key={paper.id} className="p-5 bg-slate-800/40 border border-slate-700/50 rounded-2xl hover:border-amber/30 transition-all flex flex-col">
                  <div className="flex-1">
                    <h3 className="font-bold text-slate-100 mb-2 line-clamp-2 leading-snug">{paper.title}</h3>
                    <p className="text-xs text-amber/80 font-medium mb-3 uppercase tracking-wider">{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ' et al.' : ''}</p>
                    <p className="text-xs text-slate-400 line-clamp-4 leading-relaxed mb-4 italic">
                      {paper.summary}
                    </p>
                  </div>
                  <div className="flex gap-2 pt-2 border-t border-slate-700/30">
                    <button
                      onClick={() => handleArxivImport(paper.id, paper.title)}
                      disabled={importingArxivId === paper.id}
                      className="flex-1 py-2.5 bg-slate-700 hover:bg-amber hover:text-slate-900 text-slate-200 text-xs font-bold rounded-xl transition-all disabled:opacity-50"
                    >
                      {importingArxivId === paper.id ? 'IMPORTING...' : 'IMPORT PDF'}
                    </button>
                    <a
                      href={paper.abs_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-5 py-2.5 bg-slate-800 border border-slate-600 text-slate-400 hover:text-slate-200 text-xs font-bold rounded-xl transition-all"
                    >
                      ABSTRACT
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'local' && (
          <div className="animate-in fade-in slide-in-from-left-4 duration-300 max-w-2xl">
            <div className="bg-slate-800/30 border border-slate-700/50 p-8 rounded-2xl">
              <h2 className="text-xl font-bold text-slate-100 mb-6">Local Path Import</h2>
              <form onSubmit={handleLocalSubmit} className="space-y-6">
                <div>
                  <label htmlFor="local-path" className="block text-sm font-medium text-slate-400 mb-2">Full file path on server</label>
                  <input
                    id="local-path"
                    type="text"
                    placeholder="e.g. D:\Downloads\book.epub"
                    value={localPath}
                    onChange={(e) => setLocalPath(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-amber/50"
                  />
                </div>
                <button
                  type="submit"
                  disabled={localLoading || !localPath.trim()}
                  className="w-full py-3 bg-amber text-slate-900 font-bold rounded-xl hover:bg-amber-400 active:scale-95 transition-all disabled:opacity-50"
                >
                  {localLoading ? 'IMPORTING...' : 'START IMPORT'}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
