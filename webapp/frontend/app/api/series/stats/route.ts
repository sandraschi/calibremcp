import { NextRequest } from 'next/server';
import { proxyGet } from '@/lib/proxy';

export async function GET(_request: NextRequest) {
  try {
    return await proxyGet('/api/series/stats');
  } catch {
    return new Response(null, { status: 502 });
  }
}
