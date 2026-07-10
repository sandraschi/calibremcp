"use client";

import { type Book, getSeriesBooks } from "@/common/api";
import Link from "next/link";
import { useEffect, useState } from "react";

export function SeriesDetailClient({ id }: { id: string }) {
	const seriesId = Number.parseInt(id, 10);
	const [data, setData] = useState<{
		items?: Book[];
		series?: { name?: string };
	} | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		if (Number.isNaN(seriesId)) {
			setLoading(false);
			return;
		}
		setLoading(true);
		getSeriesBooks(seriesId, { limit: 100 })
			.then((d) => setData(d))
			.catch((e) => setError(String((e as Error).message)))
			.finally(() => setLoading(false));
	}, [seriesId]);

	if (Number.isNaN(seriesId)) {
		return (
			<div className="container mx-auto p-6">
				<p className="text-slate-400">Invalid series ID</p>
			</div>
		);
	}

	if (loading) {
		return (
			<div className="container mx-auto p-6">
				<p className="text-slate-400">Loading series…</p>
			</div>
		);
	}

	if (error || !data) {
		return (
			<div className="container mx-auto p-6">
				<h1 className="text-3xl font-bold mb-6 text-slate-100">Series</h1>
				<div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
					<p className="font-medium">Could not load series</p>
					<p className="mt-2 text-sm text-slate-400">
						{error ?? "Unknown error"}
					</p>
				</div>
			</div>
		);
	}

	const seriesName = data.series?.name ?? `Series #${seriesId}`;
	const books = data.items ?? [];

	return (
		<div className="container mx-auto p-6">
			<h1 className="text-3xl font-bold mb-6 text-slate-100">{seriesName}</h1>
			<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{books.map((b) => (
					<Link
						key={b.id}
						href={`/book/${b.id}`}
						className="rounded-lg border border-slate-700 bg-slate-800/50 p-4 hover:border-amber/50 transition-colors"
					>
						<p className="font-medium text-slate-100">{b.title}</p>
					</Link>
				))}
			</div>
		</div>
	);
}
