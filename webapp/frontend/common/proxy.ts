import { NextResponse } from 'next/server';

/** Shared proxy helpers. Timeout 15s (backend+Calibre can be slow on cold start). */
const BACKEND_URL = (process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:10720').replace('localhost', '127.0.0.1');
const PROXY_TIMEOUT_MS = 15000;

export function getBackendUrl(): string {
  return BACKEND_URL;
}

export async function proxyFetch(
  url: string,
  init?: RequestInit & { timeout?: number }
): Promise<Response> {
  const timeout = init?.timeout ?? PROXY_TIMEOUT_MS;
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, {
      ...init,
      signal: controller.signal,
      cache: 'no-store',
    });
    return res;
  } finally {
    clearTimeout(t);
  }
}

/** Proxy GET and stream body through. Fails after timeout. Returns JSON error body on failure. */
export async function proxyGet(
  path: string,
  searchParams?: URLSearchParams | string
): Promise<NextResponse> {
  const url = searchParams
    ? `${BACKEND_URL}${path}?${typeof searchParams === 'string' ? searchParams : searchParams.toString()}`
    : `${BACKEND_URL}${path}`;
  const res = await proxyFetch(url);
  if (!res.ok) {
    let errBody: { error?: string; detail?: string } = { error: `Backend returned ${res.status}` };
    try {
      const text = await res.text();
      if (text) {
        try {
          errBody = JSON.parse(text);
        } catch {
          errBody = { error: text.slice(0, 500) };
        }
      }
    } catch {
      /* ignore */
    }
    return NextResponse.json(errBody, { status: res.status });
  }
  const text = await res.text();
  try {
    const data = text ? JSON.parse(text) : {};
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: `Invalid JSON: ${text.slice(0, 200)}` }, { status: 502 });
  }
}

/** Proxy POST with JSON body. Fails after timeout. Optionally pass timeoutMs for long-running requests (e.g. LLM chat). */
export async function proxyPost(
  path: string,
  body: unknown,
  options?: { timeoutMs?: number }
): Promise<NextResponse> {
  const timeout = options?.timeoutMs ?? PROXY_TIMEOUT_MS;
  const res = await proxyFetch(`${BACKEND_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    timeout,
  });
  if (!res.ok) {
    let errBody: { error?: string } = { error: `Backend returned ${res.status}` };
    try {
      const text = await res.text();
      if (text) {
        try {
          errBody = JSON.parse(text);
        } catch {
          errBody = { error: text.slice(0, 500) };
        }
      }
    } catch {
      /* ignore */
    }
    return NextResponse.json(errBody, { status: res.status });
  }
  const text = await res.text();
  if (!text) return NextResponse.json({ error: 'Empty response from backend' }, { status: 502 });
  try {
    const data = JSON.parse(text);
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ error: `Invalid JSON: ${text.slice(0, 200)}` }, { status: 502 });
  }
}
