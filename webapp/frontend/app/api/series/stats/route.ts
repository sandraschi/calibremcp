import { proxyGet } from "@/common/proxy";
import type { NextRequest } from "next/server";

export async function GET(_request: NextRequest) {
	try {
		return await proxyGet("/api/series/stats");
	} catch {
		return new Response(null, { status: 502 });
	}
}
