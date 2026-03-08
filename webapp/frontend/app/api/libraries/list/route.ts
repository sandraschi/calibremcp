import { NextRequest } from 'next/server';
import { proxyGet, getBackendUrl } from '@/common/proxy';

export async function GET(_request: NextRequest) {
  try {
    return await proxyGet('/api/libraries/list');
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return Response.json(
      {
        error: 'Backend unreachable',
        detail: msg.includes('ECONNREFUSED') ? 'Connection refused - is the backend running?' : msg,
        backend: getBackendUrl(),
        hint: 'From repo root run webapp\\start.ps1 (backend 10720, frontend 10721)',
      },
      { status: 502 }
    );
  }
}
