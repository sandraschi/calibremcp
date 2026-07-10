import { BookDetailClient } from "./book-detail-client";

export function generateStaticParams() {
	return [{ id: "0" }];
}

export default async function BookDetailPage({
	params,
}: {
	params: Promise<{ id: string }>;
}) {
	const { id } = await params;
	return <BookDetailClient id={id} />;
}
