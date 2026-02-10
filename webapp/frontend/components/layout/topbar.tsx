'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Library, HelpCircle, FileText, ExternalLink, ChevronDown, Container } from 'lucide-react';
import { listLibraries, switchLibrary, getHelp, getSystemStatus } from '@/lib/api';
import { HelpModal } from './help-modal';
import { LoggerModal } from './logger-modal';
import { APPS_CATALOG } from '@/lib/apps-catalog';

/** Naive list of Docker (or similar) containers with a web UI port. Later: standardize frontend vs infra. */
const CONTAINER_LINKS: { label: string; url: string; port: number }[] = [
  { label: "Portainer", url: "http://127.0.0.1:9001", port: 9001 },
  { label: "Traefik", url: "http://127.0.0.1:8080", port: 8080 },
  { label: "Grafana", url: "http://127.0.0.1:3100", port: 3100 },
  { label: "MyAI Dashboard", url: "http://127.0.0.1:3060", port: 3060 },
  { label: "MyAI Calibre Plus", url: "http://127.0.0.1:10734", port: 10734 },
  { label: "MyAI Plex Plus", url: "http://127.0.0.1:10760", port: 10760 },
  { label: "MyAI Document Viewer", url: "http://127.0.0.1:10744", port: 10744 },
  { label: "MyAI Future You", url: "http://127.0.0.1:10746", port: 10746 },
  { label: "MyAI Immich", url: "http://127.0.0.1:10756", port: 10756 },
  { label: "MyAI Voice AI", url: "http://127.0.0.1:10778", port: 10778 },
  { label: "MyAI Traefik", url: "http://127.0.0.1:10790", port: 10790 },
];

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

interface LaunchModalState {
  label: string;
  url: string;
  status: 'starting' | 'done' | 'error';
  error?: string;
}

export function Topbar() {
  const router = useRouter();
  const [libraries, setLibraries] = useState<{ name: string; path: string }[]>([]);
  const [currentLibrary, setCurrentLibrary] = useState<string | null>(null);
  const [showLibDropdown, setShowLibDropdown] = useState(false);
  const [showZoo, setShowZoo] = useState(false);
  const [showContainers, setShowContainers] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showLogger, setShowLogger] = useState(false);
  const [switching, setSwitching] = useState(false);
  const [launchModal, setLaunchModal] = useState<LaunchModalState | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const zooRef = useRef<HTMLDivElement>(null);
  const containersRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listLibraries().then((data) => {
      setLibraries(data.libraries);
      setCurrentLibrary(data.current_library ?? null);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!showLibDropdown) return;
    const close = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowLibDropdown(false);
      }
    };
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, [showLibDropdown]);

  useEffect(() => {
    if (!showZoo) return;
    const close = (e: MouseEvent) => {
      if (zooRef.current && !zooRef.current.contains(e.target as Node)) setShowZoo(false);
    };
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, [showZoo]);

  useEffect(() => {
    if (!showContainers) return;
    const close = (e: MouseEvent) => {
      if (containersRef.current && !containersRef.current.contains(e.target as Node)) setShowContainers(false);
    };
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, [showContainers]);

  const handleSwitchLibrary = async (name: string) => {
    if (name === currentLibrary) {
      setShowLibDropdown(false);
      return;
    }
    setSwitching(true);
    try {
      await switchLibrary(name);
      setCurrentLibrary(name);
      setShowLibDropdown(false);
      router.refresh();
    } catch {
      // ignore
    } finally {
      setSwitching(false);
    }
  };

  const handleContainerClick = (item: { label: string; url: string }) => {
    setShowContainers(false);
    window.open(item.url, '_blank', 'noopener,noreferrer');
  };

  const handleWebappClick = async (app: { label: string; url: string; port?: number }) => {
    setShowZoo(false);
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
    setLaunchModal({ label: app.label, url, status: 'starting' });
    try {
      const r = await fetch('/api/webapp-launch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ port: app.port }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        setLaunchModal((m) => m ? { ...m, status: 'error', error: data.detail ?? data.error ?? `HTTP ${r.status}` } : null);
        return;
      }
      if (data.error) {
        setLaunchModal((m) => m ? { ...m, status: 'error', error: data.error } : null);
        return;
      }
      setLaunchModal((m) => m ? { ...m, status: 'done' } : null);
      window.open(url, '_blank', 'noopener,noreferrer');
      setTimeout(() => setLaunchModal(null), 1500);
    } catch (e) {
      setLaunchModal((m) => m ? { ...m, status: 'error', error: e instanceof Error ? e.message : 'Request failed' } : null);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-slate-700 bg-slate-900/95 backdrop-blur">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between gap-4">
          <Link href="/" className="font-heading text-xl font-semibold text-amber shrink-0">
            Calibre
          </Link>

          <div className="flex-1" />

          <div className="flex items-center gap-2 shrink-0">
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setShowLibDropdown(!showLibDropdown)}
                disabled={switching || libraries.length === 0}
                className="flex items-center gap-2 px-3 py-2 rounded-md bg-slate-800 text-slate-200 hover:bg-slate-700 text-sm max-w-[180px] truncate"
                title={currentLibrary ?? 'Select library'}
              >
                <Library className="w-4 h-4 shrink-0" />
                <span className="truncate">{currentLibrary || 'Select library'}</span>
              </button>
              {showLibDropdown && (
                <div className="absolute right-0 mt-1 py-1 w-64 max-h-64 overflow-auto rounded-md bg-slate-800 border border-slate-600 shadow-lg">
                  {libraries.map((lib) => (
                    <button
                      key={lib.name}
                      type="button"
                      onClick={() => handleSwitchLibrary(lib.name)}
                      className={`block w-full text-left px-4 py-2 text-sm hover:bg-slate-700 ${
                        lib.name === currentLibrary ? 'text-amber' : 'text-slate-200'
                      }`}
                    >
                      {lib.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="relative" ref={zooRef}>
              <button
                type="button"
                onClick={() => setShowZoo(!showZoo)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-700/50 hover:text-amber text-sm"
                title="Jump to other webapps"
              >
                <ExternalLink className="w-4 h-4" />
                <span className="hidden sm:inline">Webapps</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showZoo ? "rotate-180" : ""}`} />
              </button>
              {showZoo && (
                <div className="absolute right-0 mt-1 py-1 w-56 max-h-80 overflow-auto rounded-lg bg-slate-800 border border-slate-600 shadow-xl z-50">
                  {APPS_CATALOG.map((app) => (
                    <button
                      key={app.url}
                      type="button"
                      onClick={() => handleWebappClick(app)}
                      className="block w-full text-left px-4 py-2 text-sm text-slate-200 hover:bg-slate-700/80 hover:text-amber"
                    >
                      {app.label}
                      {app.port != null && <span className="text-slate-500 text-xs ml-1">:{app.port}</span>}
                    </button>
                  ))}
                  <Link
                    href="/apps"
                    onClick={() => setShowZoo(false)}
                    className="block w-full text-left px-4 py-2 text-sm text-slate-400 hover:bg-slate-700/80 hover:text-amber border-t border-slate-600 mt-1"
                  >
                    Our Apps (full list)
                  </Link>
                </div>
              )}
            </div>
            <div className="relative" ref={containersRef}>
              <button
                type="button"
                onClick={() => setShowContainers(!showContainers)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-700/50 hover:text-amber text-sm"
                title="Jump to container UIs (Docker, etc.)"
              >
                <Container className="w-4 h-4" />
                <span className="hidden sm:inline">Containers</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showContainers ? "rotate-180" : ""}`} />
              </button>
              {showContainers && (
                <div className="absolute right-0 mt-1 py-1 w-56 max-h-80 overflow-auto rounded-lg bg-slate-800 border border-slate-600 shadow-xl z-50">
                  {CONTAINER_LINKS.map((item) => (
                    <button
                      key={item.url}
                      type="button"
                      onClick={() => handleContainerClick(item)}
                      className="block w-full text-left px-4 py-2 text-sm text-slate-200 hover:bg-slate-700/80 hover:text-amber"
                    >
                      {item.label}
                      <span className="text-slate-500 text-xs ml-1">:{item.port}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => setShowHelp(true)}
              className="p-2 rounded-md text-slate-400 hover:bg-slate-700 hover:text-amber"
              title="Help"
            >
              <HelpCircle className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={() => setShowLogger(true)}
              className="p-2 rounded-md text-slate-400 hover:bg-slate-700 hover:text-amber"
              title="System status"
            >
              <FileText className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
      {showLogger && <LoggerModal onClose={() => setShowLogger(false)} />}
      {launchModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50" role="dialog" aria-modal="true">
          <div className="rounded-lg bg-slate-800 border border-slate-600 shadow-xl px-6 py-4 max-w-sm text-center">
            {launchModal.status === 'starting' && (
              <>
                <p className="text-slate-200 font-medium">Starting {launchModal.label}</p>
                <p className="text-slate-400 text-sm mt-1">Please wait...</p>
              </>
            )}
            {launchModal.status === 'done' && (
              <p className="text-amber">Opened {launchModal.label}</p>
            )}
            {launchModal.status === 'error' && (
              <>
                <p className="text-red-400 font-medium">Could not start {launchModal.label}</p>
                <p className="text-slate-400 text-sm mt-1">{launchModal.error}</p>
                <p className="text-slate-500 text-xs mt-2">Run the start script in the repo manually.</p>
                <button
                  type="button"
                  onClick={() => setLaunchModal(null)}
                  className="mt-3 px-4 py-2 rounded bg-slate-700 text-slate-200 hover:bg-slate-600 text-sm"
                >
                  Close
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
