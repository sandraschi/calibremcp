'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { getLogs, getSystemStatus, type LogsResponse } from '@/lib/api';

const POLL_INTERVAL_MS = 2000;
const MAX_POLL_INTERVAL_MS = 30000;
const BACKOFF_MULTIPLIER = 1.5;

export default function LogsPage() {
  const [mode, setMode] = useState<'logs' | 'status'>('logs');
  const [logs, setLogs] = useState<LogsResponse | null>(null);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [level, setLevel] = useState('');
  const [tail, setTail] = useState(500);
  const [live, setLive] = useState(false);
  const pollIntervalRef = useRef(POLL_INTERVAL_MS);
  const pollTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchLogs = useCallback(async () => {
    try {
      const res = await getLogs({
        tail,
        filter: filter || undefined,
        level: level || undefined,
      });
      setLogs(res);
      setError(res.error ?? null);
      setLoading(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setLogs(null);
      setLoading(false);
    }
  }, [tail, filter, level]);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await getSystemStatus('diagnostic');
      setStatus(res);
      setError(null);
      setLoading(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus(null);
      setLoading(false);
    }
  }, []);

  const load = useCallback(() => {
    setLoading(true);
    if (mode === 'logs') {
      fetchLogs();
    } else {
      fetchStatus();
    }
  }, [mode, fetchLogs, fetchStatus]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!live || mode !== 'logs') return;
    const schedule = () => {
      pollTimerRef.current = setTimeout(() => {
        fetchLogs();
        pollIntervalRef.current = Math.min(
          pollIntervalRef.current * BACKOFF_MULTIPLIER,
          MAX_POLL_INTERVAL_MS
        );
        schedule();
      }, pollIntervalRef.current);
    };
    schedule();
    return () => {
      if (pollTimerRef.current) clearTimeout(pollTimerRef.current);
      pollIntervalRef.current = POLL_INTERVAL_MS;
    };
  }, [live, mode, fetchLogs]);

  const handleRefresh = () => {
    pollIntervalRef.current = POLL_INTERVAL_MS;
    load();
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Logs</h1>

      <div className="flex flex-wrap gap-4 mb-4 items-end">
        <div>
          <label className="block text-sm text-slate-400 mb-1">View</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as 'logs' | 'status')}
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200"
          >
            <option value="logs">Log file</option>
            <option value="status">System status</option>
          </select>
        </div>

        {mode === 'logs' && (
          <>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Filter</label>
              <input
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Substring..."
                className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 w-40"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Level</label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200"
              >
                <option value="">All</option>
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Tail</label>
              <input
                type="number"
                value={tail}
                onChange={(e) => setTail(Number(e.target.value) || 500)}
                min={100}
                max={10000}
                step={100}
                className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 w-24"
              />
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={live}
                onChange={(e) => setLive(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-slate-400">Live tail (poll with backoff)</span>
            </label>
          </>
        )}

        <button
          type="button"
          onClick={handleRefresh}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-4 mb-4 text-slate-200">
          <p className="font-medium">Error</p>
          <p className="text-sm text-slate-400 mt-1">{error}</p>
          {logs?.file && <p className="text-xs text-slate-500 mt-1">Log file: {logs.file}</p>}
        </div>
      )}

      {loading && !logs && !status && (
        <p className="text-slate-500">Loading...</p>
      )}

      {mode === 'logs' && logs && (
        <div className="rounded-lg bg-slate-800 border border-slate-600 overflow-hidden">
          {logs.file && (
            <p className="text-xs text-slate-500 px-4 py-2 border-b border-slate-600">
              {logs.file} (showing last {logs.lines.length} of {logs.total})
            </p>
          )}
          <pre className="p-4 text-slate-300 text-sm overflow-auto max-h-[70vh] whitespace-pre-wrap font-mono">
            {logs.lines.length ? logs.lines.join('') : 'No matching lines'}
          </pre>
        </div>
      )}

      {mode === 'status' && status && (
        <pre className="p-4 rounded-lg bg-slate-800 border border-slate-600 text-slate-300 text-sm overflow-auto max-h-[70vh] whitespace-pre-wrap font-mono">
          {JSON.stringify(status, null, 2)}
        </pre>
      )}
    </div>
  );
}
