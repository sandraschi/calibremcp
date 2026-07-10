"use client";

import { getLibraryStats } from "@/common/api";
import {
	BookMarked,
	BookOpen,
	Library,
	MessageSquare,
	Search,
	Tags,
	Users,
} from "lucide-react";
import Link from "next/link";
import { Suspense, useEffect, useState } from "react";

function HomePageInner() {
	const [stats, setStats] = useState<{
		total_books: number;
		total_authors: number;
		total_series: number;
		total_tags: number;
		library_name: string;
	} | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		let cancelled = false;
		setLoading(true);
		getLibraryStats()
			.then((s) => {
				if (!cancelled) {
					setStats({
						total_books: s.total_books,
						total_authors: s.total_authors,
						total_series: s.total_series,
						total_tags: s.total_tags,
						library_name: s.library_name,
					});
				}
			})
			.catch(() => {
				if (!cancelled) setStats(null);
			})
			.finally(() => {
				if (!cancelled) setLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	const cards = [
		{
			href: "/books",
			label: "Books",
			value: stats?.total_books ?? "—",
			icon: BookOpen,
		},
		{
			href: "/authors",
			label: "Authors",
			value: stats?.total_authors ?? "—",
			icon: Users,
		},
		{
			href: "/series",
			label: "Series",
			value: stats?.total_series ?? "—",
			icon: BookMarked,
		},
		{
			href: "/tags",
			label: "Tags",
			value: stats?.total_tags ?? "—",
			icon: Tags,
		},
	];

	if (loading) {
		return (
			<main className="min-h-screen">
				<div className="container mx-auto p-6">
					<p className="text-slate-400">Loading overview…</p>
				</div>
			</main>
		);
	}

	return (
		<main className="min-h-screen">
			<div className="container mx-auto p-6">
				<h1 className="text-3xl font-bold mb-2 text-slate-100">Overview</h1>
				{stats?.library_name && (
					<p className="text-slate-500 mb-6">Library: {stats.library_name}</p>
				)}
				<div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
					{cards.map(({ href, label, value, icon: Icon }) => (
						<Link
							key={href}
							href={href}
							className="block p-6 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50 transition-colors"
						>
							<Icon className="w-8 h-8 text-amber mb-2" />
							<p className="text-2xl font-bold text-slate-100">{value}</p>
							<p className="text-sm text-slate-400">{label}</p>
						</Link>
					))}
				</div>
				<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
					<Link
						href="/books"
						className="flex items-center gap-3 p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50"
					>
						<BookOpen className="w-6 h-6 text-amber shrink-0" />
						<span className="text-slate-200 font-medium">Browse books</span>
					</Link>
					<Link
						href="/search"
						className="flex items-center gap-3 p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50"
					>
						<Search className="w-6 h-6 text-amber shrink-0" />
						<span className="text-slate-200 font-medium">Search</span>
					</Link>
					<Link
						href="/libraries"
						className="flex items-center gap-3 p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50"
					>
						<Library className="w-6 h-6 text-amber shrink-0" />
						<span className="text-slate-200 font-medium">Libraries</span>
					</Link>
					<Link
						href="/chat"
						className="flex items-center gap-3 p-4 rounded-lg bg-slate-800 border border-slate-600 hover:border-amber/50"
					>
						<MessageSquare className="w-6 h-6 text-amber shrink-0" />
						<span className="text-slate-200 font-medium">AI Chat</span>
					</Link>
				</div>
			</div>
		</main>
	);
}

export default function Home() {
	return (
		<Suspense
			fallback={
				<main className="min-h-screen">
					<div className="container mx-auto p-6">
						<p className="text-slate-400">Loading…</p>
					</div>
				</main>
			}
		>
			<HomePageInner />
		</Suspense>
	);
}
