"use client";

import type { Book } from "@/common/api";
import { BookModal } from "@/components/books/book-modal";
import { useRouter } from "next/navigation";

export function BookModalWrapper({ book }: { book: Book }) {
	const router = useRouter();
	return <BookModal book={book} onClose={() => router.back()} />;
}
