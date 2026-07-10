/**
 * Build outbound links for a book from Calibre identifiers + title/author fallbacks.
 *
 * “Important” works often have Wikipedia articles; many books only match search.
 * We offer: saved Wikipedia id, best-guess article URLs, Special:Search, Wikidata, etc.
 */

import type { Book } from "./api";

export type ExternalBookLink = { label: string; href: string };

function firstAuthorName(authors: Book["authors"] | undefined): string {
	const a = authors?.[0];
	if (!a) return "";
	return typeof a === "string" ? a : ((a as { name?: string }).name ?? "");
}

function normIsbn(v: string): string {
	return v.replace(/[-\s]/g, "");
}

/** Wikipedia /wiki/ path segment: spaces → underscores, then encode (Calibre-style titles). */
function wikipediaPathSegment(raw: string): string {
	const t = raw.trim().replace(/\s+/g, "_");
	return encodeURIComponent(t).replace(/%20/g, "_");
}

function isHttpUrl(s: string): boolean {
	return /^https?:\/\//i.test(s.trim());
}

/** SF Encyclopedia entry slug (same idea as media_agentic._sfe_slug). */
function sfEncyclopediaSlug(title: string): string {
	return title
		.replace(/[^\w\s]/g, "")
		.trim()
		.toLowerCase()
		.replace(/\s+/g, "_");
}

/** TVTropes Literature CamelCase slug (same idea as media_agentic._tvtropes_slug). */
function tvTropesLiteratureSlug(title: string): string {
	return title
		.replace(/[^\w\s]/g, "")
		.trim()
		.split(/\s+/)
		.filter(Boolean)
		.map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
		.join("");
}

/** Fleet **tvtropes-mcp** webapp (local mirror UI). See tvtropes-mcp/docs/CROSS_MCP.md. */
export function tvtropesMcpWebappBase(): string {
	const raw =
		typeof process !== "undefined"
			? process.env.NEXT_PUBLIC_TVTROPES_MCP_URL?.trim()
			: "";
	if (!raw || raw === "0" || raw.toLowerCase() === "false") return "";
	return raw || "http://127.0.0.1:10965";
}

/** Deep-link into tvtropes-mcp: `/?lookup=Literature/HarryPotter` (cached mirror, not tvtropes.org). */
export function tvtropesMcpLookupHref(
	namespace: string,
	pageName: string,
): string {
	const base = tvtropesMcpWebappBase().replace(/\/$/, "");
	const ns = namespace.replace(/^\/+|\/+$/g, "");
	const page = pageName.replace(/^\/+|\/+$/g, "");
	return `${base}/?lookup=${ns}/${page}`;
}

/** Parse `Literature/Slug` from a tvtropes.org pmwiki URL if present. */
function parseTvtropesLookupPath(url: string): string | null {
	const m = url.match(/pmwiki\.php\/([^?#]+)/i);
	if (!m) return null;
	return decodeURIComponent(m[1].replace(/^\//, ""));
}

/**
 * Wrap a direct `https://tvtropes.org/...` URL for **human** opens when you still need the live site
 * (optional; prefer {@link tvtropesMcpLookupHref} via fleet **tvtropes-mcp**).
 *
 * Set **`NEXT_PUBLIC_TVTROPES_VIA`** only when you must proxy raw tvtropes.org (legacy).
 */
export function wrapTvTropesUserUrl(directTvTropesUrl: string): string {
	const raw =
		typeof process !== "undefined"
			? (process.env.NEXT_PUBLIC_TVTROPES_VIA?.trim() ?? "")
			: "";
	if (!raw) return directTvTropesUrl;

	const lower = raw.toLowerCase();
	if (lower.startsWith("jina")) {
		const colon = raw.indexOf(":");
		const rest = colon >= 0 ? raw.slice(colon + 1).trim() : "";
		const host = (rest || "https://r.jina.ai").replace(/\/$/, "");
		return `${host}/${directTvTropesUrl}`;
	}

	if (raw.includes("{url}")) {
		return raw.replaceAll("{url}", encodeURIComponent(directTvTropesUrl));
	}

	if (raw.endsWith("=") || raw.endsWith("?")) {
		return `${raw}${encodeURIComponent(directTvTropesUrl)}`;
	}

	return `${raw}${raw.includes("?") ? "&" : "?"}u=${encodeURIComponent(directTvTropesUrl)}`;
}

/** True when fleet tvtropes-mcp webapp links are enabled (default port 10965). */
export function isTvTropesFleetMirrorEnabled(): boolean {
	return Boolean(tvtropesMcpWebappBase());
}

/** True when `NEXT_PUBLIC_TVTROPES_VIA` is set (legacy raw-site proxy). */
export function isTvTropesViaConfigured(): boolean {
	return Boolean(
		typeof process !== "undefined" &&
			process.env.NEXT_PUBLIC_TVTROPES_VIA?.trim(),
	);
}

function lowerKeyMap(
	id: Record<string, string> | undefined,
): Record<string, string> {
	if (!id) return {};
	const m: Record<string, string> = {};
	for (const [k, v] of Object.entries(id)) {
		if (v == null || String(v).trim() === "") continue;
		m[String(k).toLowerCase()] = String(v).trim();
	}
	return m;
}

export function buildBookExternalLinks(book: {
	title: string;
	authors?: Book["authors"];
	identifiers?: Record<string, string>;
}): ExternalBookLink[] {
	const out: ExternalBookLink[] = [];
	const seen = new Set<string>();
	const push = (label: string, href: string) => {
		if (!href || seen.has(href)) return;
		seen.add(href);
		out.push({ label, href });
	};

	const id = lowerKeyMap(book.identifiers);
	const title = book.title?.trim() ?? "";
	const author = firstAuthorName(book.authors).trim();
	const workQuery = [title, author].filter(Boolean).join(" ");

	// --- Saved Wikipedia (Calibre identifier or full wiki URL) ---
	const wikiId =
		id.wikipedia ??
		id.wiki ??
		id["wikipedia-en"] ??
		id["en.wikipedia"] ??
		id.ewikipedia;
	if (wikiId) {
		if (isHttpUrl(wikiId) && wikiId.includes("wikipedia.org")) {
			push("Wikipedia (saved link)", wikiId);
		} else {
			const seg = wikipediaPathSegment(wikiId.replace(/^\/wiki\//i, ""));
			push("Wikipedia (saved article)", `https://en.wikipedia.org/wiki/${seg}`);
		}
	}

	const rawIsbn =
		id.isbn13 ?? id.isbn10 ?? id.isbn ?? id["isbn-13"] ?? id["isbn-10"];
	const isbn = rawIsbn ? normIsbn(String(rawIsbn)) : "";

	if (isbn && /^[\dX]{10,13}$/i.test(isbn)) {
		push(
			"Open Library (ISBN)",
			`https://openlibrary.org/isbn/${encodeURIComponent(isbn)}#book`,
		);
		push(
			"WorldCat",
			`https://www.worldcat.org/search?q=isbn%3A${encodeURIComponent(isbn)}`,
		);
		push(
			"Google Books",
			`https://www.google.com/search?tbm=bks&q=${encodeURIComponent(`isbn:${isbn}`)}`,
		);
		push(
			"LibraryThing",
			`https://www.librarything.com/isbn/${encodeURIComponent(isbn)}`,
		);
		push(
			"Wikipedia (ISBN search)",
			`https://en.wikipedia.org/wiki/Special:Search?search=${encodeURIComponent(isbn)}`,
		);
	}

	// Open Library work / edition ids
	const ol =
		id.openlibrary ??
		id.ol ??
		id["openlibrary-work"] ??
		id["openlibrary-edition"];
	if (ol) {
		const s = String(ol).trim();
		if (/^OL\d+W$/i.test(s)) {
			push(
				"Open Library (work)",
				`https://openlibrary.org/works/${encodeURIComponent(s)}`,
			);
		} else if (/^OL\d+M$/i.test(s)) {
			push(
				"Open Library (edition)",
				`https://openlibrary.org/books/${encodeURIComponent(s)}`,
			);
		} else {
			push(
				"Open Library (search)",
				`https://openlibrary.org/search?q=${encodeURIComponent(s)}`,
			);
		}
	}

	const asinRaw = id.asin ?? id.amazon;
	if (asinRaw) {
		const d = String(asinRaw)
			.replace(/^asin:/i, "")
			.trim();
		if (/^[A-Z0-9]{10}$/i.test(d)) {
			push("Amazon", `https://www.amazon.com/dp/${encodeURIComponent(d)}`);
		}
	}

	const gr = id.goodreads;
	if (gr) {
		const gid = String(gr).replace(/\D/g, "");
		if (gid) push("Goodreads", `https://www.goodreads.com/book/show/${gid}`);
	}

	const doi = id.doi;
	if (doi)
		push("DOI", `https://doi.org/${encodeURIComponent(String(doi).trim())}`);

	const lccn = id.lccn;
	if (lccn) {
		const clean = String(lccn).replace(/\s+/g, "");
		if (clean)
			push(
				"Library of Congress",
				`https://lccn.loc.gov/${encodeURIComponent(clean)}`,
			);
	}

	const oclc = id.oclc ?? id["oclc-number"] ?? id.worldcat;
	if (oclc) {
		const n = String(oclc).replace(/\D/g, "");
		if (n) push("WorldCat (OCLC)", `https://www.worldcat.org/oclc/${n}`);
	}

	const gut = id.gutenberg ?? id["project gutenberg"] ?? id.pg;
	if (gut) {
		const n = String(gut).replace(/\D/g, "");
		if (n) push("Project Gutenberg", `https://www.gutenberg.org/ebooks/${n}`);
	}

	const url = id.url ?? id.uri;
	if (url && isHttpUrl(url)) {
		push("Saved URL", url.trim());
	}

	// --- TV Tropes: prefer fleet **tvtropes-mcp** mirror (10965); avoid raw tvtropes.org in browser ---
	const tropesFleetBase = tvtropesMcpWebappBase();
	const tropesId =
		id.tvtropes ?? id["tv tropes"] ?? id.tvtropesorg ?? id["tv tropes org"];
	if (tropesFleetBase && tropesId) {
		let d = tropesId.trim();
		if (!isHttpUrl(d)) {
			if (d.startsWith("//")) d = `https:${d}`;
			else if (d.startsWith("/")) d = `https://tvtropes.org${d}`;
			else if (/pmwiki\.php/i.test(d))
				d = `https://tvtropes.org/${d.replace(/^\/+/, "")}`;
			else if (d.includes("/")) {
				const slash = d.indexOf("/");
				push(
					"TV Tropes (fleet mirror)",
					tvtropesMcpLookupHref(d.slice(0, slash), d.slice(slash + 1)),
				);
			} else {
				const slug = tvTropesLiteratureSlug(d) || d;
				push(
					"TV Tropes (fleet mirror)",
					tvtropesMcpLookupHref("Literature", slug),
				);
			}
		}
		if (d.includes("tvtropes.org")) {
			const lookup = parseTvtropesLookupPath(d);
			if (lookup) {
				const slash = lookup.indexOf("/");
				if (slash > 0) {
					push(
						"TV Tropes (fleet mirror)",
						tvtropesMcpLookupHref(
							lookup.slice(0, slash),
							lookup.slice(slash + 1),
						),
					);
				} else {
					push(
						"TV Tropes (fleet mirror)",
						tvtropesMcpLookupHref("Literature", lookup),
					);
				}
			}
			if (isTvTropesViaConfigured()) {
				push("TV Tropes (live site)", wrapTvTropesUserUrl(d));
			}
		}
	}

	if (title && tropesFleetBase) {
		const tt = tvTropesLiteratureSlug(title);
		if (tt.length > 1) {
			push("TV Tropes (fleet mirror)", tvtropesMcpLookupHref("Literature", tt));
		}
	}

	// --- Wikipedia: best-guess article URLs (may 404 for obscure titles) ---
	if (title && !wikiId) {
		const t = wikipediaPathSegment(title);
		push("Wikipedia (title)", `https://en.wikipedia.org/wiki/${t}`);
		push(
			"Wikipedia (novel disambiguation)",
			`https://en.wikipedia.org/wiki/${wikipediaPathSegment(`${title} (novel)`)}`,
		);
		push(
			"Wikipedia (book disambiguation)",
			`https://en.wikipedia.org/wiki/${wikipediaPathSegment(`${title} (book)`)}`,
		);
	}

	if (workQuery) {
		push(
			"Wikipedia (search)",
			`https://en.wikipedia.org/wiki/Special:Search?search=${encodeURIComponent(workQuery)}`,
		);
		push(
			"Wikidata (search)",
			`https://www.wikidata.org/w/index.php?search=${encodeURIComponent(workQuery)}`,
		);
		push(
			"Web search",
			`https://www.google.com/search?q=${encodeURIComponent(`${workQuery} book`)}`,
		);
		push(
			"TV Tropes (Google site search)",
			`https://www.google.com/search?q=${encodeURIComponent(`site:tvtropes.org ${workQuery}`)}`,
		);
	}

	if (title) {
		const sfe = sfEncyclopediaSlug(title);
		if (sfe) {
			push(
				"SF Encyclopedia (guess)",
				`https://www.sf-encyclopedia.com/entry/${sfe}`,
			);
		}
		if (!tropesFleetBase && isTvTropesViaConfigured()) {
			const tt = tvTropesLiteratureSlug(title);
			if (tt.length > 1) {
				const direct = `https://tvtropes.org/pmwiki/pmwiki.php/Literature/${tt}`;
				push("TV Tropes — Literature (live site)", wrapTvTropesUserUrl(direct));
			}
		}
	}

	return out;
}

/** Deep-link into the RAG page with mode + optional book id / query prefilled. */
export function ragToolHref(opts: {
	mode: "metadata" | "passages" | "synopsis" | "research";
	bookId?: number;
	query?: string;
}): string {
	const p = new URLSearchParams();
	p.set("mode", opts.mode);
	if (opts.bookId != null && !Number.isNaN(opts.bookId)) {
		p.set("bookId", String(opts.bookId));
	}
	if (opts.query?.trim()) p.set("query", opts.query.trim());
	return `/rag?${p.toString()}`;
}
