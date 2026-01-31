import { NextRequest } from 'next/server';
import { proxyPost } from '@/lib/proxy';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return await proxyPost('/api/annas/search', body);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return Response.json(
      { error: 'Backend unreachable', detail: msg },
      { status: 502 }
    );
  }
}
