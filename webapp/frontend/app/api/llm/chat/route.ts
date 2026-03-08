import { NextRequest } from 'next/server';
import { proxyPost } from '@/common/proxy';
import { NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return await proxyPost('/api/llm/chat', body, { timeoutMs: 90000 });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json(
      { error: msg.includes('abort') ? 'Request timed out. LLM may be slow.' : msg },
      { status: 502 }
    );
  }
}
