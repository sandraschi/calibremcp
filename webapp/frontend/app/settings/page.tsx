'use client';

import { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '@/common/api';

export default function SettingsPage() {
  const [provider, setProvider] = useState('ollama');
  const [annasMirrors, setAnnasMirrorsState] = useState('');
  const [gutenbergMirror, setGutenbergMirror] = useState('');
  const [savingMirrors, setSavingMirrors] = useState(false);
  const [mirrorResult, setMirrorResult] = useState<{ success: boolean; message: string } | null>(null);

  const [baseUrl, setBaseUrl] = useState('http://127.0.0.1:11434');
  const [apiKey, setApiKey] = useState('');
  const [models, setModels] = useState<string[]>([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [modelError, setModelError] = useState<string | null>(null);

  const fetchModels = async () => {
    setLoadingModels(true);
    setModelError(null);
    try {
      const params = new URLSearchParams();
      if (provider) params.set('provider', provider);
      if (baseUrl) params.set('base_url', baseUrl);
      const res = await fetch(`/api/llm/models?${params}`);
      const data = await res.json();
      if (data.models) {
        setModels(data.models);
      } else {
        setModels([]);
        setModelError(data.error ?? 'No models');
      }
    } catch (e) {
      setModels([]);
      setModelError(e instanceof Error ? e.message : 'Failed');
    } finally {
      setLoadingModels(false);
    }
  };

  useEffect(() => {
    async function loadSettings() {
      try {
        const s = await getSettings();
        setAnnasMirrorsState(s.annas_mirrors.join(', '));
        setGutenbergMirror(s.gutenberg_mirror);
      } catch (e) {
        console.error('Failed to load settings', e);
      }
    }
    loadSettings();
  }, []);

  const handleSaveMirrors = async () => {
    setSavingMirrors(true);
    setMirrorResult(null);
    try {
      const annas = annasMirrors.split(',').map((m) => m.trim()).filter(Boolean);
      const res = await updateSettings({
        annas_mirrors: annas,
        gutenberg_mirror: gutenbergMirror,
      });
      setMirrorResult(res);
      setTimeout(() => setMirrorResult(null), 3000);
    } catch (e) {
      setMirrorResult({ success: false, message: e instanceof Error ? e.message : 'Save failed' });
    } finally {
      setSavingMirrors(false);
    }
  };

  useEffect(() => {
    if (provider === 'ollama') setBaseUrl('http://127.0.0.1:11434');
    if (provider === 'lmstudio') setBaseUrl('http://127.0.0.1:1234/v1');
    if (provider === 'openai') setBaseUrl('https://api.openai.com/v1');
  }, [provider]);

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Settings</h1>

      <section className="mb-10 p-6 bg-slate-800/50 rounded-xl border border-slate-700/50">
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-slate-100">
          <span className="w-2 h-6 bg-amber rounded-full"></span>
          External Mirrors
        </h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Anna&apos;s Archive Mirrors (comma-separated)
            </label>
            <input
              type="text"
              value={annasMirrors}
              onChange={(e) => setAnnasMirrorsState(e.target.value)}
              placeholder="https://annas-archive.se, https://annas-archive.li"
              className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-amber/50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Project Gutenberg Mirror
            </label>
            <input
              type="text"
              value={gutenbergMirror}
              onChange={(e) => setGutenbergMirror(e.target.value)}
              placeholder="https://www.gutenberg.org"
              className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-amber/50"
            />
          </div>

          <div className="flex items-center gap-4 pt-2">
            <button
              type="button"
              onClick={handleSaveMirrors}
              disabled={savingMirrors}
              className="px-6 py-2 rounded-lg bg-amber text-slate-950 font-bold hover:bg-amber-400 active:scale-95 transition-all disabled:opacity-50"
            >
              {savingMirrors ? 'Saving...' : 'Save Mirror Settings'}
            </button>
            {mirrorResult && (
              <span className={mirrorResult.success ? 'text-emerald-400 text-sm animate-pulse' : 'text-red-400 text-sm'}>
                {mirrorResult.message}
              </span>
            )}
          </div>
        </div>
      </section>

      <section className="p-6 bg-slate-800/50 rounded-xl border border-slate-700/50 mb-8">
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-slate-100">
          <span className="w-2 h-6 bg-blue-500 rounded-full"></span>
          AI / LLM Provider
        </h2>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="llm-provider" className="block text-sm font-medium text-slate-300 mb-2">Provider</label>
            <select
              id="llm-provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            >
              <option value="ollama">Ollama</option>
              <option value="lmstudio">LM Studio</option>
              <option value="openai">OpenAI / Cloud API</option>
            </select>
          </div>
          <div>
            <label htmlFor="llm-base-url" className="block text-sm font-medium text-slate-300 mb-2">Base URL</label>
            <input
              id="llm-base-url"
              type="url"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            />
          </div>
          {provider === 'openai' && (
            <div>
              <label htmlFor="llm-api-key" className="block text-sm font-medium text-slate-300 mb-2">API Key</label>
              <input
                id="llm-api-key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              />
            </div>
          )}
          <button
            type="button"
            onClick={fetchModels}
            disabled={loadingModels}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 disabled:opacity-50"
          >
            {loadingModels ? 'Loading...' : 'Test Connection & List Models'}
          </button>
          {modelError && <p className="text-red-400 text-sm mt-2">{modelError}</p>}
          {models.length > 0 && (
            <div className="mt-4 p-4 bg-slate-900 rounded-lg border border-slate-700">
              <p className="text-sm font-semibold text-slate-100 mb-2">Available models</p>
              <ul className="text-sm text-slate-400 grid grid-cols-2 gap-2 max-h-40 overflow-auto scrollbar-thin">
                {models.map((m) => (
                  <li key={m} className="truncate px-2 py-1 bg-slate-800 rounded">{m}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
