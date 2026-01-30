import { NextRequest } from 'next/server';
import { proxyGet } from '@/lib/proxy';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  try {
    const { searchParams } = new URL(request.url);
    return await proxyGet(`/api/series/${id}/books`, searchParams);
  } catch {
    return new Response(null, { status: 502 });
  }
}
