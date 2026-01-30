import { NextRequest } from 'next/server';
import { proxyGet } from '@/lib/proxy';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    return await proxyGet('/api/search/', searchParams);
  } catch {
    return new Response(null, { status: 502 });
  }
}
