'use client';

import { useConnection } from '@/app/store/connection';
import { useZoom } from '@/hooks/useZoom';
import { useCallback, useEffect, useState } from 'react';
import { Sidebar } from './sidebar';
import { Topbar } from './topbar';

const BACKEND_PORT = 10720;
const BACKOFF = [1, 2, 4, 8, 16, 30];

export function AppLayout({ children }: { children: React.ReactNode }) {
  useZoom();
  const [collapsed, setCollapsed] = useState(false);

  const tick = useCallback(() => {
    let attempt = 0;
    const poll = async () => {
      try {
        const r = await fetch(`http://127.0.0.1:${BACKEND_PORT}/api/health`, {
          signal: AbortSignal.timeout(5000),
        });
        if (r.ok) {
          useConnection.setState({ state: 'connected' });
          attempt = 0;
        } else useConnection.setState({ state: 'offline', lastError: `HTTP ${r.status}` });
      } catch (e) {
        useConnection.setState({
          state: 'offline',
          lastError: e instanceof Error ? e.message : 'Network error',
        });
      }
      attempt = Math.min(++attempt, BACKOFF.length - 1);
      setTimeout(poll, BACKOFF[attempt] * 1000);
    };
    poll();
  }, []);

  useEffect(() => {
    tick();
  }, [tick]);

  // Tauri event bridge
  useEffect(() => {
    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        const { listen } = await import('@tauri-apps/api/event');
        unlisten = await listen<string>('backend-status', (event) => {
          if (event.payload === 'ready') useConnection.setState({ state: 'connected' });
          else if (event.payload?.startsWith('error:'))
            useConnection.setState({ state: 'error', lastError: event.payload });
        });
      } catch {
        // Not inside Tauri — HTTP polling handles it
      }
    })();
    return () => {
      if (unlisten) unlisten();
    };
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem('sidebar-collapsed');
    if (stored !== null) setCollapsed(stored === 'true');
  }, []);

  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', String(collapsed));
  }, [collapsed]);

  return (
    <div className="h-screen flex flex-col">
      <Topbar />
      <div className="flex flex-1">
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />
        <main className="flex-1 min-w-0 flex flex-col">{children}</main>
      </div>
    </div>
  );
}
