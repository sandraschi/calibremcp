'use client';

import { HELP_SECTIONS } from '@/common/help-content';
import { HelpMarkdown } from '@/components/help/help-markdown';
import { Book, BookOpen, Compass, Globe, Server, Share2 } from 'lucide-react';
import { useMemo, useState } from 'react';

type SectionKey = keyof typeof HELP_SECTIONS;

const SECTION_ICONS: Record<SectionKey, React.ElementType> = {
  webapp: Globe,
  guides: Compass,
  ebooks: BookOpen,
  contentServer: Share2,
  calibre: Book,
  calibreMcp: Server,
};

const HELP_TAB_ORDER: SectionKey[] = [
  'webapp',
  'guides',
  'ebooks',
  'contentServer',
  'calibre',
  'calibreMcp',
];

interface Heading {
  level: number;
  text: string;
  id: string;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-');
}

function extractHeadings(markdown: string): Heading[] {
  const out: Heading[] = [];
  for (const line of markdown.split('\n')) {
    const m = /^(#{2,3})\s+(.+)$/.exec(line.trim());
    if (m) {
      const text = m[2].trim();
      out.push({ level: m[1].length, text, id: slugify(text) });
    }
  }
  return out;
}

export default function HelpPage() {
  const [active, setActive] = useState<SectionKey>('webapp');
  const section = HELP_SECTIONS[active];
  const Icon = SECTION_ICONS[active];

  const headings = useMemo(() => extractHeadings(section.content), [section.content]);

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Help</h1>

      <div className="flex gap-2 mb-6 border-b border-slate-700 overflow-x-auto">
        {HELP_TAB_ORDER.map((key) => {
          const TabIcon = SECTION_ICONS[key];
          return (
            <button
              key={key}
              type="button"
              onClick={() => setActive(key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                active === key
                  ? 'border-amber text-amber'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <TabIcon className="w-4 h-4" />
              {HELP_SECTIONS[key].title}
            </button>
          );
        })}
      </div>

      <div className="flex flex-col lg:flex-row gap-6 items-start">
        <article className="flex-1 min-w-0 rounded-lg bg-slate-800/40 border border-slate-700 p-6">
          <div className="flex items-center gap-2 mb-2 pb-4 border-b border-slate-700/60">
            <Icon className="w-6 h-6 text-amber" />
            <span className="text-xl font-semibold text-slate-200">{section.title}</span>
          </div>
          <HelpMarkdown content={section.content} />
        </article>

        {headings.length > 0 && (
          <aside className="hidden lg:block w-56 shrink-0 sticky top-6 rounded-lg bg-slate-800/40 border border-slate-700 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">
              On this page
            </p>
            <nav aria-label="Section contents">
              <ul className="space-y-1">
                {headings.map((h) => (
                  <li key={h.id} className={h.level === 3 ? 'ml-3' : ''}>
                    <a
                      href={`#${h.id}`}
                      className="block text-xs text-slate-400 hover:text-amber leading-snug py-0.5"
                    >
                      {h.text}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </aside>
        )}
      </div>
    </div>
  );
}
