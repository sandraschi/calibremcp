'use client';

import { useState } from 'react';
import { HELP_SECTIONS } from '@/lib/help-content';
import { Book, Server, Globe } from 'lucide-react';

type SectionKey = keyof typeof HELP_SECTIONS;

const SECTION_ICONS: Record<SectionKey, React.ElementType> = {
  calibre: Book,
  calibreMcp: Server,
  webapp: Globe,
};

export default function HelpPage() {
  const [active, setActive] = useState<SectionKey>('calibre');
  const section = HELP_SECTIONS[active];
  const Icon = SECTION_ICONS[active];

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Help</h1>

      <div className="flex gap-2 mb-6 border-b border-slate-700">
        {(Object.keys(HELP_SECTIONS) as SectionKey[]).map((key) => {
          const Svg = SECTION_ICONS[key];
          return (
            <button
              key={key}
              type="button"
              onClick={() => setActive(key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                active === key
                  ? 'border-amber text-amber'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Svg className="w-4 h-4" />
              {HELP_SECTIONS[key].title}
            </button>
          );
        })}
      </div>

      <article className="prose prose-invert prose-slate max-w-none">
        <div className="flex items-center gap-2 mb-4">
          <Icon className="w-6 h-6 text-amber" />
          <h2 className="text-xl font-semibold text-slate-200 m-0">{section.title}</h2>
        </div>
        <div className="p-4 rounded-lg bg-slate-800 border border-slate-600 text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-sans">
          {section.content.trim()}
        </div>
      </article>
    </div>
  );
}
