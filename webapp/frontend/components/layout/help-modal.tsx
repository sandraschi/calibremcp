'use client';

import { useState, useEffect } from 'react';
import { getHelp } from '@/lib/api';

interface HelpModalProps {
  onClose: () => void;
}

export function HelpModal({ onClose }: HelpModalProps) {
  const [content, setContent] = useState<string>('Loading...');
  const [level, setLevel] = useState('basic');

  useEffect(() => {
    getHelp(level)
      .then((data) => {
        const text = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        setContent(text);
      })
      .catch((e) => setContent(`Error: ${e instanceof Error ? e.message : 'Failed to load'}`));
  }, [level]);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950" onClick={onClose}>
      <div
        className="bg-slate-800 border border-slate-600 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col"
        style={{ backgroundColor: '#1e293b' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-slate-600">
          <h2 className="text-lg font-semibold text-amber">Help</h2>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="px-2 py-1 rounded bg-slate-700 text-slate-200 text-sm"
          >
            <option value="basic">Basic</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="expert">Expert</option>
          </select>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white"
          >
            Close
          </button>
        </div>
        <pre className="p-4 overflow-auto text-sm text-slate-300 whitespace-pre-wrap font-mono">
          {content}
        </pre>
      </div>
    </div>
  );
}
