'use client';

import Link from 'next/link';

interface AuthorLinksProps {
  authors: (string | { name?: string })[];
  className?: string;
  stopPropagation?: boolean;
  separator?: string;
}

export function AuthorLinks({
  authors,
  className = '',
  stopPropagation = false,
  separator = ', ',
}: AuthorLinksProps) {
  const names =
    authors
      ?.map((a) => (typeof a === 'string' ? a : ((a as { name?: string }).name ?? '')))
      .filter(Boolean) ?? [];

  if (names.length === 0) return <span className={className}>Unknown</span>;

  const clickHandler = stopPropagation ? (e: React.MouseEvent) => e.stopPropagation() : undefined;

  return (
    <span className={className}>
      {names.map((name, i) => (
        <span key={`${name}-${i}`}>
          {i > 0 && separator}
          <Link
            href={`/books?search=${encodeURIComponent(`author:"${name}"`)}`}
            onClick={clickHandler}
            className="text-amber-400 hover:text-amber-300 hover:underline"
          >
            {name}
          </Link>
        </span>
      ))}
    </span>
  );
}
