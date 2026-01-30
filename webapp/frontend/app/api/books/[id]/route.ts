import { NextRequest } from 'next/server';
import { getBackendUrl, proxyFetch } from '@/lib/proxy';

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  try {
    const res = await proxyFetch(`${getBackendUrl()}/api/books/${id}`);
    if (!res.ok) return new Response(null, { status: res.status });
    const data = await res.json();
    return Response.json(data);
  } catch {
    return new Response(null, { status: 502 });
  }
}
