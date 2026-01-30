'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect, FormEvent } from 'react';
import { listAuthors, listTags } from '@/lib/api';

interface SearchBarProps {
  initialQuery?: string;
  initialAuthor?: string;
  initialTag?: string;
  initialMinRating?: string;
}

export function SearchBar({
  initialQuery = '',
  initialAuthor = '',
  initialTag = '',
  initialMinRating = ''
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [author, setAuthor] = useState(initialAuthor);
  const [tag, setTag] = useState(initialTag);
  const [minRating, setMinRating] = useState(initialMinRating);
  const [authors, setAuthors] = useState<{ id: number; name: string }[]>([]);
  const [tags, setTags] = useState<{ id: number; name: string }[]>([]);

  useEffect(() => {
    listAuthors({ limit: 300 }).then((r) => {
      const items = (r.items ?? []).map((a, i) => ({
        id: (a as { id?: number }).id ?? i,
        name: (a as { name?: string }).name ?? String(a)
      }));
      if (initialAuthor && !items.some((a) => a.name === initialAuthor)) {
        items.unshift({ id: -1, name: initialAuthor });
      }
      setAuthors(items);
    }).catch(() => {});
    listTags({ limit: 300 }).then((r) => {
      const items = (r.items ?? []).map((t, i) => ({
        id: (t as { id?: number }).id ?? i,
        name: (t as { name?: string }).name ?? String(t)
      }));
      if (initialTag && !items.some((t) => t.name === initialTag)) {
        items.unshift({ id: -1, name: initialTag });
      }
      setTags(items);
    }).catch(() => {});
  }, [initialAuthor, initialTag]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set('query', query.trim());
    if (author) params.set('author', author);
    if (tag) params.set('tag', tag);
    if (minRating) params.set('min_rating', minRating);
    router.push(`/search?${params.toString()}`);
  };

  const handleClear = () => {
    setQuery('');
    setAuthor('');
    setTag('');
    setMinRating('');
    router.push('/search');
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-800 border border-slate-600 p-4 rounded-lg mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-slate-300 mb-1">
            Search Text
          </label>
          <input
            type="text"
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Title, author, tags..."
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
          />
        </div>
        <div>
          <label htmlFor="author" className="block text-sm font-medium text-slate-300 mb-1">
            Author
          </label>
          <select
            id="author"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
          >
            <option value="">Any author</option>
            {authors.map((a) => (
              <option key={a.id} value={a.name}>
                {a.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="tag" className="block text-sm font-medium text-slate-300 mb-1">
            Tag
          </label>
          <select
            id="tag"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
          >
            <option value="">Any tag</option>
            {tags.map((t) => (
              <option key={t.id} value={t.name}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="min_rating" className="block text-sm font-medium text-slate-300 mb-1">
            Min Rating
          </label>
          <select
            id="min_rating"
            value={minRating}
            onChange={(e) => setMinRating(e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
          >
            <option value="">Any</option>
            <option value="5">5 stars</option>
            <option value="4">4+ stars</option>
            <option value="3">3+ stars</option>
            <option value="2">2+ stars</option>
            <option value="1">1+ stars</option>
          </select>
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        <button
          type="submit"
          className="px-4 py-2 bg-amber text-slate-900 rounded-md hover:bg-amber/90 font-medium"
        >
          Search
        </button>
        <button
          type="button"
          onClick={handleClear}
          className="px-4 py-2 bg-slate-700 text-slate-200 rounded-md hover:bg-slate-600"
        >
          Clear
        </button>
      </div>
    </form>
  );
}
