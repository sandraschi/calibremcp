import { NextRequest } from 'next/server';
import { proxyGet } from '@/lib/proxy';
import { NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    return await proxyGet('/api/publishers/', searchParams);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json(
      { error: msg.includes('abort') ? 'Request timed out' : msg },
      { status: 502 }
    );
  }
}
