import { proxyGet } from '@/common/proxy';

/** Same payload as FastAPI `GET /health` on the backend — probes often hit the web origin, not :10720. */
export async function GET() {
  try {
    return await proxyGet('/health');
  } catch {
    return new Response(null, { status: 502 });
  }
}
