"use client";

import { type Book, searchBooks } from "@/common/api";
import { BookGrid } from "@/components/books/book-grid";
import { SearchBar } from "@/components/search/search-bar";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

function buildSearchPageUrl(
	base: string,
	page: number,
	p: {
		query?: string;
		author?: string;
		tag?: string;
		min_rating?: string;
		fulltext?: string;
	},
): string {
	const params = new URLSearchParams();
	if (page > 1) params.set("page", page.toString());
	if (p.query) params.set("query", p.query);
	if (p.author) params.set("author", p.author);
	if (p.tag) params.set("tag", p.tag);
	if (p.min_rating) params.set("min_rating", p.min_rating);
	if (p.fulltext) params.set("fulltext", p.fulltext);
	const q = params.toString();
	return q ? `${base}?${q}` : base;
}

function SearchPageInner() {
	const searchParams = useSearchParams();
	const query = searchParams?.get("query") ?? undefined;
	const author = searchParams?.get("author") ?? undefined;
	const tag = searchParams?.get("tag") ?? undefined;
	const minRating = searchParams?.get("min_rating") ?? undefined;
	const fulltextParam = searchParams?.get("fulltext") ?? undefined;
	const page = Math.max(
		1,
		Number.parseInt(searchParams?.get("page") ?? "1", 10),
	);
	const limit = 50;
	const offset = (page - 1) * limit;

	const fulltextMode = fulltextParam === "1" && query?.trim();
	const hasSearchParams = Boolean(
		fulltextMode || query || author || tag || minRating,
	);

	const [data, setData] = useState<{ items?: Book[]; total?: number }>({
		items: [],
		total: 0,
	});
	const [loading, setLoading] = useState(false);

	useEffect(() => {
		if (!hasSearchParams) {
			setData({ items: [], total: 0 });
			setLoading(false);
			return;
		}

		let cancelled = false;
		setLoading(true);
		searchBooks({
			query,
			author: fulltextMode ? undefined : author,
			tag: fulltextMode ? undefined : tag,
			min_rating: fulltextMode
				? undefined
				: minRating
					? Number.parseInt(minRating, 10)
					: undefined,
			fulltext: Boolean(fulltextMode),
			limit,
			offset,
		})
			.then((res) => {
				if (!cancelled) setData(res);
			})
			.catch(() => {
				if (!cancelled) setData({ items: [], total: 0 });
			})
			.finally(() => {
				if (!cancelled) setLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, [
		query,
		author,
		tag,
		minRating,
		fulltextMode,
		hasSearchParams,
		limit,
		offset,
	]);

	const total = data.total ?? 0;
	const totalPages = Math.ceil(total / limit);
	const hasPrev = page > 1;
	const hasNext = page < totalPages;
	const base = "/search";

	const params = {
		query,
		author,
		tag,
		min_rating: minRating,
		fulltext: fulltextParam === "1" ? "1" : undefined,
	};

	return (
		<div className="container mx-auto p-6">
			<h1 className="text-3xl font-bold mb-6 text-slate-100">Search Books</h1>
			<SearchBar
				initialQuery={query}
				initialAuthor={author}
				initialTag={tag}
				initialMinRating={minRating}
				initialFulltext={fulltextParam === "1"}
			/>

			{hasSearchParams && loading && (
				<div className="mt-6 text-center text-slate-400">
					<p>Searching…</p>
				</div>
			)}

			{hasSearchParams && !loading && (
				<>
					{data.items && data.items.length > 0 ? (
						<>
							<div className="mt-6">
								<BookGrid books={data.items} />
							</div>
							{total > limit && (
								<nav
									className="mt-6 flex flex-wrap items-center justify-center gap-2"
									aria-label="Pagination"
								>
									<p className="w-full text-center text-sm text-slate-400 mb-2">
										Showing {offset + 1}-{Math.min(offset + limit, total)} of{" "}
										{total} books
									</p>
									<div className="flex items-center gap-2">
										{hasPrev ? (
											<Link
												href={buildSearchPageUrl(base, page - 1, params)}
												className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
											>
												Previous
											</Link>
										) : (
											<span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">
												Previous
											</span>
										)}
										<span className="px-3 py-2 text-sm text-slate-400">
											Page {page} of {totalPages}
										</span>
										{hasNext ? (
											<Link
												href={buildSearchPageUrl(base, page + 1, params)}
												className="px-4 py-2 text-sm font-medium rounded-md bg-slate-700 hover:bg-slate-600 text-slate-200"
											>
												Next
											</Link>
										) : (
											<span className="px-4 py-2 text-sm text-slate-500 cursor-not-allowed">
												Next
											</span>
										)}
									</div>
								</nav>
							)}
						</>
					) : (
						<div className="mt-6 text-center text-gray-500">
							<p>No books found matching your search criteria.</p>
						</div>
					)}
				</>
			)}

			{!hasSearchParams && (
				<div className="mt-6 text-center text-slate-400">
					<p>Enter search criteria above to find books.</p>
				</div>
			)}
		</div>
	);
}

export default function SearchPage() {
	return (
		<Suspense
			fallback={
				<div className="container mx-auto p-6">
					<p className="text-slate-400">Loading…</p>
				</div>
			}
		>
			<SearchPageInner />
		</Suspense>
	);
}
