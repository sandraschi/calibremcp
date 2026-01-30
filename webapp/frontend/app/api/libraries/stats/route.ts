import { NextRequest } from 'next/server';
import { proxyGet, getBackendUrl } from '@/lib/proxy';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    return await proxyGet('/api/libraries/stats', searchParams);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return Response.json(
      { error: 'Backend unreachable', detail: msg, backend: getBackendUrl() },
      { status: 502 }
    );
  }
}
