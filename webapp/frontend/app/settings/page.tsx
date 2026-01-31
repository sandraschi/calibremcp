'use client';

import { useState, useEffect } from 'react';
import { getAnnasMirrors, setAnnasMirrors } from '@/lib/api';

export default function SettingsPage() {
  const [provider, setProvider] = useState('ollama');
  const [annasMirrors, setAnnasMirrorsState] = useState('');
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
    setAnnasMirrorsState(getAnnasMirrors());
  }, []);

  useEffect(() => {
    if (provider === 'ollama') setBaseUrl('http://127.0.0.1:11434');
    if (provider === 'lmstudio') setBaseUrl('http://127.0.0.1:1234/v1');
    if (provider === 'openai') setBaseUrl('https://api.openai.com/v1');
  }, [provider]);

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Settings</h1>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4 text-slate-200">LLM / AI</h2>
        <p className="text-slate-400 text-sm mb-4">
          Configure Ollama, LM Studio, or OpenAI-compatible API for the chat.
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
            >
              <option value="ollama">Ollama</option>
              <option value="lmstudio">LM Studio</option>
              <option value="openai">OpenAI / Cloud API</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Base URL</label>
            <input
              type="url"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
            />
          </div>
          {provider === 'openai' && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
              />
              <p className="text-slate-500 text-xs mt-1">Stored in browser only (use env for production)</p>
            </div>
          )}
          <div>
            <button
              type="button"
              onClick={fetchModels}
              disabled={loadingModels}
              className="px-4 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50"
            >
              {loadingModels ? 'Loading...' : 'List models'}
            </button>
          </div>
          {modelError && <p className="text-red-400 text-sm">{modelError}</p>}
          {models.length > 0 && (
            <div>
              <p className="text-sm font-medium text-slate-300 mb-2">Available models ({models.length})</p>
              <ul className="text-sm text-slate-400 space-y-1 max-h-40 overflow-auto">
                {models.map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4 text-slate-200">
          Anna&apos;s Archive
        </h2>
        <p className="text-slate-400 text-sm mb-4">
          Mirror URL(s) for Anna&apos;s Archive search. Leave empty to use
          defaults. Comma-separated for multiple mirrors.
        </p>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Mirror URL(s)
          </label>
          <input
            type="text"
            value={annasMirrors}
            onChange={(e) => setAnnasMirrorsState(e.target.value)}
            onBlur={() => setAnnasMirrors(annasMirrors)}
            placeholder="https://annas-archive.se, https://annas-archive.in"
            className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
          <p className="text-slate-500 text-xs mt-1">
            Stored in browser. Used by Import page search.
          </p>
        </div>
      </section>
    </div>
  );
}
