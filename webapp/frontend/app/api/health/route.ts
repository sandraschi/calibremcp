import { proxyGet } from '@/common/proxy';

/** Fleet / tools that expect `/api/health` on the webapp origin. */
export async function GET() {
  try {
    return await proxyGet('/health');
  } catch {
    return new Response(null, { status: 502 });
  }
}
