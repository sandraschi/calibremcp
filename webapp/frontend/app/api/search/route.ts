import { proxyGet } from "@/common/proxy";
import type { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
	try {
		const { searchParams } = new URL(request.url);
		return await proxyGet("/api/search/", searchParams);
	} catch {
		return new Response(null, { status: 502 });
	}
}
