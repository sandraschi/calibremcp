'use client';

import { useState } from 'react';
import { APPS_CATALOG, type AppEntry } from '@/lib/apps-catalog';
import { ExternalLink } from 'lucide-react';

async function checkUrlUp(url: string, timeoutMs = 2500): Promise<boolean> {
  try {
    const c = new AbortController();
    const t = setTimeout(() => c.abort(), timeoutMs);
    const r = await fetch(url, { method: 'GET', signal: c.signal, cache: 'no-store' });
    clearTimeout(t);
    return r.ok;
  } catch {
    return false;
  }
}

type LaunchStatus = 'idle' | 'starting' | 'done' | 'error';

export default function OurAppsPage() {
  const [launchTarget, setLaunchTarget] = useState<{ app: AppEntry; status: LaunchStatus; error?: string } | null>(null);

  const handleOpen = async (app: AppEntry) => {
    const url = app.url;
    const up = await checkUrlUp(url);
    if (up) {
      window.open(url, '_blank', 'noopener,noreferrer');
      return;
    }
    if (app.port == null) {
      window.open(url, '_blank', 'noopener,noreferrer');
      return;
    }
    setLaunchTarget({ app, status: 'starting' });
    try {
      const r = await fetch('/api/webapp-launch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ port: app.port }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        setLaunchTarget((t) =>
          t ? { ...t, status: 'error', error: (data.detail ?? data.error ?? `HTTP ${r.status}`) as string } : null
        );
        return;
      }
      if (data.error) {
        setLaunchTarget((t) => (t ? { ...t, status: 'error', error: data.error } : null));
        return;
      }
      setLaunchTarget((t) => (t ? { ...t, status: 'done' } : null));
      window.open(url, '_blank', 'noopener,noreferrer');
      setTimeout(() => setLaunchTarget(null), 1500);
    } catch (e) {
      setLaunchTarget((t) =>
        t ? { ...t, status: 'error', error: e instanceof Error ? e.message : 'Request failed' } : null
      );
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Our Apps</h1>
      <p className="text-slate-400 mb-8 max-w-2xl">
        Webapps and MCP servers you can open from here. Each card explains what the app is and what you can do with it.
      </p>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {APPS_CATALOG.map((app) => {
          const launching = launchTarget?.app.url === app.url;
          return (
            <article
              key={app.url}
              className="rounded-lg border border-slate-600 bg-slate-800/80 p-5 flex flex-col"
            >
              <div className="flex items-start justify-between gap-2 mb-3">
                <h2 className="text-lg font-semibold text-slate-100">{app.label}</h2>
                <button
                  type="button"
                  onClick={() => handleOpen(app)}
                  disabled={launching && launchTarget?.status === 'starting'}
                  className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-amber/20 text-amber hover:bg-amber/30 text-sm font-medium disabled:opacity-60"
                >
                  <ExternalLink className="w-4 h-4" />
                  {launching && launchTarget?.status === 'starting' ? 'Opening…' : 'Open'}
                </button>
              </div>
              <p className="text-slate-300 text-sm mb-3">{app.whatItIs}</p>
              <p className="text-slate-400 text-sm flex-1">{app.whatYouCanDo}</p>
              {app.port != null && (
                <p className="text-slate-500 text-xs mt-2">{app.url.replace('http://', '')}</p>
              )}
            </article>
          );
        })}
      </div>

      {launchTarget?.status === 'error' && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50"
          role="dialog"
          aria-modal="true"
        >
          <div className="rounded-lg bg-slate-800 border border-slate-600 shadow-xl px-6 py-4 max-w-sm text-center">
            <p className="text-red-400 font-medium">Could not start {launchTarget.app.label}</p>
            <p className="text-slate-400 text-sm mt-1">{launchTarget.error}</p>
            <p className="text-slate-500 text-xs mt-2">Run the start script in the repo manually.</p>
            <button
              type="button"
              onClick={() => setLaunchTarget(null)}
              className="mt-3 px-4 py-2 rounded bg-slate-700 text-slate-200 hover:bg-slate-600 text-sm"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
