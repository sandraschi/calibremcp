import { proxyPost } from "@/common/proxy";
import type { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
	try {
		const body = await request.json();
		return await proxyPost("/api/viewer/open-file", body);
	} catch (e) {
		const msg = e instanceof Error ? e.message : String(e);
		return Response.json(
			{ error: "Backend unreachable", detail: msg },
			{ status: 502 },
		);
	}
}
