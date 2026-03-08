import { NextRequest } from 'next/server';
import { proxyPost } from '@/common/proxy';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return await proxyPost('/api/export/json', body);
  } catch {
    return new Response(null, { status: 502 });
  }
}
