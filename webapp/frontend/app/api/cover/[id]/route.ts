import { NextRequest } from 'next/server';
import { getBackendUrl, proxyFetch } from '@/lib/proxy';

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const bookId = parseInt(id, 10);
  if (isNaN(bookId) || bookId < 1) {
    return Response.json({ error: 'Invalid book ID' }, { status: 400 });
  }

  try {
    const res = await proxyFetch(`${getBackendUrl()}/api/books/${bookId}/cover`);
    if (!res.ok) return new Response(null, { status: res.status });
    return new Response(res.body, {
      status: 200,
      headers: {
        'Content-Type': res.headers.get('content-type') ?? 'image/jpeg',
        'Cache-Control': 'public, max-age=3600',
      },
    });
  } catch {
    return new Response(null, { status: 502 });
  }
}
