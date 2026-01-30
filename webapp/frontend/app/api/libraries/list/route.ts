import { NextRequest } from 'next/server';
import { proxyGet, getBackendUrl } from '@/lib/proxy';

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
        hint: 'Run: webapp\\start-local.bat or: cd webapp/backend; python -m uvicorn app.main:app --reload --port 13000',
      },
      { status: 502 }
    );
  }
}
