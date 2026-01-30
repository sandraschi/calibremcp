import { NextRequest } from 'next/server';
import { proxyGet, proxyPost } from '@/lib/proxy';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    return await proxyGet('/api/books/', searchParams);
  } catch {
    return new Response(null, { status: 502 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return await proxyPost('/api/books/', body);
  } catch {
    return new Response(null, { status: 502 });
  }
}
