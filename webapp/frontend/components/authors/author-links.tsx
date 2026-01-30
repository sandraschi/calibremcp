'use client';

/**
 * Renders author names as Wikipedia search links.
 * Clicking an author opens Wikipedia search in a new tab.
 */

function getWikipediaSearchUrl(name: string): string {
  return `https://en.wikipedia.org/wiki/Special:Search?search=${encodeURIComponent(name)}`;
}

interface AuthorLinksProps {
  authors: (string | { name?: string })[];
  className?: string;
  /** Stop click from bubbling (e.g. when inside a card that opens modal) */
  stopPropagation?: boolean;
  separator?: string;
}

export function AuthorLinks({ authors, className = '', stopPropagation = false, separator = ', ' }: AuthorLinksProps) {
  const names = authors?.map((a) =>
    typeof a === 'string' ? a : (a as { name?: string }).name ?? ''
  ).filter(Boolean) ?? [];

  if (names.length === 0) return <span className={className}>Unknown</span>;

  return (
    <span className={className}>
      {names.map((name, i) => (
        <span key={`${name}-${i}`}>
          {i > 0 && separator}
          <a
            href={getWikipediaSearchUrl(name)}
            target="_blank"
            rel="noopener noreferrer"
            onClick={stopPropagation ? (e) => e.stopPropagation() : undefined}
            className="text-amber-400 hover:text-amber-300 hover:underline"
          >
            {name}
          </a>
        </span>
      ))}
    </span>
  );
}
