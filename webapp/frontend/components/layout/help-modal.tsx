'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { Book, Server, Globe, ExternalLink } from 'lucide-react';
import { HELP_SECTIONS } from '@/lib/help-content';
import { getHelp } from '@/lib/api';

type SectionKey = keyof typeof HELP_SECTIONS;

const SECTION_ICONS: Record<SectionKey, React.ElementType> = {
  calibre: Book,
  calibreMcp: Server,
  webapp: Globe,
};

/** Modal order: Webapp first (primary), then Calibre, then MCP with drilldown */
const MODAL_TABS: SectionKey[] = ['webapp', 'calibre', 'calibreMcp'];

interface HelpModalProps {
  onClose: () => void;
}

export function HelpModal({ onClose }: HelpModalProps) {
  const [tab, setTab] = useState<SectionKey>('webapp');
  const [mcpLevel, setMcpLevel] = useState('basic');
  const [mcpContent, setMcpContent] = useState<string | null>(null);
  const [mcpLoading, setMcpLoading] = useState(false);
  const [mcpError, setMcpError] = useState<string | null>(null);

  const loadMcpHelp = useCallback(async () => {
    setMcpLoading(true);
    setMcpError(null);
    try {
      const data = await getHelp(mcpLevel);
      const text = typeof data === 'string' ? data : (data as { message?: string }).message ?? JSON.stringify(data, null, 2);
      setMcpContent(text);
    } catch (e) {
      setMcpError(e instanceof Error ? e.message : 'Failed to load');
      setMcpContent(null);
    } finally {
      setMcpLoading(false);
    }
  }, [mcpLevel]);

  const section = HELP_SECTIONS[tab];
  const Icon = SECTION_ICONS[tab];

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950"
      onClick={onClose}
    >
      <div
        className="bg-slate-800 border border-slate-600 rounded-lg shadow-xl max-w-2xl w-full max-h-[85vh] flex flex-col"
        style={{ backgroundColor: '#1e293b' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-slate-600 shrink-0">
          <h2 className="text-lg font-semibold text-amber">Help</h2>
          <div className="flex items-center gap-2">
            <Link
              href="/help"
              className="flex items-center gap-1 text-sm text-slate-400 hover:text-amber"
            >
              Full help page
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>
            <button
              type="button"
              onClick={onClose}
              className="text-slate-400 hover:text-white"
            >
              Close
            </button>
          </div>
        </div>

        <div className="flex border-b border-slate-600 shrink-0">
          {MODAL_TABS.map((key) => {
            const Svg = SECTION_ICONS[key];
            return (
              <button
                key={key}
                type="button"
                onClick={() => setTab(key)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  tab === key
                    ? 'border-amber text-amber bg-slate-800'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Svg className="w-4 h-4" />
                {HELP_SECTIONS[key].title}
              </button>
            );
          })}
        </div>

        <div className="p-4 overflow-auto flex-1 min-h-0">
          <div className="flex items-center gap-2 mb-3">
            <Icon className="w-5 h-5 text-amber shrink-0" />
            <h3 className="text-base font-semibold text-slate-200">{section.title}</h3>
          </div>
          <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-sans mb-4">
            {section.content.trim()}
          </div>

          {tab === 'calibreMcp' && (
            <div className="mt-4 pt-4 border-t border-slate-600">
              <div className="flex items-center gap-2 flex-wrap mb-2">
                <span className="text-slate-400 text-sm font-medium">MCP server help (from server)</span>
                <select
                  value={mcpLevel}
                  onChange={(e) => setMcpLevel(e.target.value)}
                  className="px-2 py-1 rounded bg-slate-700 text-slate-200 text-sm"
                >
                  <option value="basic">Basic</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
                <button
                  type="button"
                  onClick={loadMcpHelp}
                  disabled={mcpLoading}
                  className="px-3 py-1.5 rounded bg-amber text-slate-900 text-sm font-medium hover:bg-amber/90 disabled:opacity-50"
                >
                  {mcpLoading ? 'Loading...' : 'Load'}
                </button>
              </div>
              {mcpError && <p className="text-red-400 text-sm mb-2">{mcpError}</p>}
              {mcpContent !== null && (
                <pre className="p-3 rounded bg-slate-900 text-slate-300 text-xs whitespace-pre-wrap overflow-auto max-h-60">
                  {mcpContent}
                </pre>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
