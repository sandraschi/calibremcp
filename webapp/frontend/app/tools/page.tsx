'use client';

import { getBaseUrl, listSkills } from '@/common/api';
import Link from 'next/link';
import { Suspense, useEffect, useState } from 'react';

interface Capabilities {
  success: boolean;
  data?: {
    server?: string;
    version?: string;
    transports?: string[];
    endpoints?: string[];
    features?: Record<string, boolean>;
  };
}

interface Diagnostics {
  tools?: { total?: number; categories?: string[] };
  tool_count?: number;
}

const BACKEND_HINT = 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721).';

function ToolsPageInner() {
  const [caps, setCaps] = useState<Capabilities | null>(null);
  const [diag, setDiag] = useState<Diagnostics | null>(null);
  const [skillCount, setSkillCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const base = getBaseUrl();
        const [capsRes, diagRes] = await Promise.all([
          fetch(`${base}/api/capabilities`).then((r) => {
            if (!r.ok) throw new Error(`capabilities ${r.status}`);
            return r.json() as Promise<Capabilities>;
          }),
          fetch(`${base}/api/v1/diagnostics`).then((r) => {
            if (!r.ok) throw new Error(`diagnostics ${r.status}`);
            return r.json() as Promise<Diagnostics>;
          }),
        ]);
        let skills = 0;
        try {
          const s = await listSkills();
          skills = s.skills?.length ?? 0;
        } catch {
          skills = 0;
        }
        if (!cancelled) {
          setCaps(capsRes);
          setDiag(diagRes);
          setSkillCount(skills);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-6" data-testid="tools-page">
        <p className="text-slate-300" data-testid="tools-loading">
          Loading tools…
        </p>
      </div>
    );
  }

  if (error || !caps?.data) {
    return (
      <div className="container mx-auto p-6" data-testid="tools-page">
        <h1 className="text-3xl font-bold mb-2 text-slate-100" data-testid="tools-title">
          Tools
        </h1>
        <p className="text-slate-300 mb-2" data-testid="tools-error">
          Backend unreachable: {error ?? 'no capability data'}. {BACKEND_HINT}
        </p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="rounded border border-slate-600 px-3 py-1 text-slate-200"
          data-testid="tools-retry"
        >
          Retry
        </button>
      </div>
    );
  }

  const endpoints = caps.data.endpoints ?? [];
  const toolTotal = diag?.tools?.total ?? diag?.tool_count ?? 0;

  return (
    <div className="container mx-auto p-6" data-testid="tools-page">
      <h1 className="text-3xl font-bold mb-2 text-slate-100" data-testid="tools-title">
        Tools
      </h1>
      <p className="text-slate-300 mb-6" data-testid="tools-summary">
        {caps.data.server ?? 'calibre-mcp'} {caps.data.version ? `v${caps.data.version}` : ''} —{' '}
        {toolTotal} MCP tools registered, {skillCount ?? 0} skills, {endpoints.length} REST
        endpoints. Full reference lives under{' '}
        <Link href="/api-docs" className="underline">
          API Docs
        </Link>
        .
      </p>
      {endpoints.length === 0 ? (
        <p className="text-slate-300" data-testid="tools-empty">
          No endpoints reported by /api/capabilities.
        </p>
      ) : (
        <ul className="grid gap-2 max-w-2xl" data-testid="tools-list">
          {endpoints.map((ep) => (
            <li
              key={ep}
              className="rounded-lg border border-slate-600 bg-slate-800/50 px-4 py-2 font-mono text-sm text-slate-200"
            >
              {ep}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function ToolsPage() {
  return (
    <Suspense fallback={<p className="p-6 text-slate-300">Loading tools…</p>}>
      <ToolsPageInner />
    </Suspense>
  );
}
