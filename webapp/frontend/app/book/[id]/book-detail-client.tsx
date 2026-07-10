"use client";

import { type Book, getBook } from "@/common/api";
import { useEffect, useState } from "react";
import { BookModalWrapper } from "./book-modal-wrapper";

export function BookDetailClient({ id }: { id: string }) {
	const bookId = Number.parseInt(id, 10);
	const [book, setBook] = useState<Book | null>(null);
	const [error, setError] = useState(false);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		if (Number.isNaN(bookId)) {
			setLoading(false);
			return;
		}
		setLoading(true);
		setError(false);
		getBook(bookId)
			.then((b) => setBook(b))
			.catch(() => setError(true))
			.finally(() => setLoading(false));
	}, [bookId]);

	if (Number.isNaN(bookId)) {
		return (
			<div className="container mx-auto p-6">
				<p className="text-slate-400">Invalid book ID</p>
			</div>
		);
	}

	if (loading) {
		return (
			<div className="container mx-auto p-6">
				<p className="text-slate-400">Loading book…</p>
			</div>
		);
	}

	if (error || !book) {
		return (
			<div className="container mx-auto p-6">
				<p className="text-slate-400">Book not found</p>
			</div>
		);
	}

	return <BookModalWrapper book={book} />;
}
