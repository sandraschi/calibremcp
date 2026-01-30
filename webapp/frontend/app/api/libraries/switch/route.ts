import { NextRequest } from 'next/server';
import { proxyPost, getBackendUrl } from '@/lib/proxy';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return await proxyPost('/api/libraries/switch', body);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return Response.json(
      { error: 'Backend unreachable', detail: msg, backend: getBackendUrl() },
      { status: 502 }
    );
  }
}
