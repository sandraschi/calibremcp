import { NextRequest } from 'next/server';
import { proxyPost } from '@/lib/proxy';

/** Proxy POST to backend webapp-launch (may take up to ~90s while starting target app). */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return await proxyPost('/api/webapp-launch', body, { timeoutMs: 95000 });
  } catch {
    return new Response(JSON.stringify({ error: 'Backend unreachable' }), { status: 502 });
  }
}
