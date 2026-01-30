'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Library, HelpCircle, FileText } from 'lucide-react';
import { listLibraries, switchLibrary, getHelp, getSystemStatus } from '@/lib/api';
import { HelpModal } from './help-modal';
import { LoggerModal } from './logger-modal';

export function Topbar() {
  const router = useRouter();
  const [libraries, setLibraries] = useState<{ name: string; path: string }[]>([]);
  const [currentLibrary, setCurrentLibrary] = useState<string | null>(null);
  const [showLibDropdown, setShowLibDropdown] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showLogger, setShowLogger] = useState(false);
  const [switching, setSwitching] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listLibraries().then((data) => {
      setLibraries(data.libraries);
      setCurrentLibrary(data.current_library ?? null);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!showLibDropdown) return;
    const close = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowLibDropdown(false);
      }
    };
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, [showLibDropdown]);

  const handleSwitchLibrary = async (name: string) => {
    if (name === currentLibrary) {
      setShowLibDropdown(false);
      return;
    }
    setSwitching(true);
    try {
      await switchLibrary(name);
      setCurrentLibrary(name);
      setShowLibDropdown(false);
      router.refresh();
    } catch {
      // ignore
    } finally {
      setSwitching(false);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-slate-700 bg-slate-900/95 backdrop-blur">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between gap-4">
          <Link href="/" className="font-heading text-xl font-semibold text-amber shrink-0">
            Calibre
          </Link>

          <div className="flex-1" />

          <div className="flex items-center gap-2 shrink-0">
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setShowLibDropdown(!showLibDropdown)}
                disabled={switching || libraries.length === 0}
                className="flex items-center gap-2 px-3 py-2 rounded-md bg-slate-800 text-slate-200 hover:bg-slate-700 text-sm max-w-[180px] truncate"
                title={currentLibrary ?? 'Select library'}
              >
                <Library className="w-4 h-4 shrink-0" />
                <span className="truncate">{currentLibrary || 'Select library'}</span>
              </button>
              {showLibDropdown && (
                <div className="absolute right-0 mt-1 py-1 w-64 max-h-64 overflow-auto rounded-md bg-slate-800 border border-slate-600 shadow-lg">
                  {libraries.map((lib) => (
                    <button
                      key={lib.name}
                      type="button"
                      onClick={() => handleSwitchLibrary(lib.name)}
                      className={`block w-full text-left px-4 py-2 text-sm hover:bg-slate-700 ${
                        lib.name === currentLibrary ? 'text-amber' : 'text-slate-200'
                      }`}
                    >
                      {lib.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => setShowHelp(true)}
              className="p-2 rounded-md text-slate-400 hover:bg-slate-700 hover:text-amber"
              title="Help"
            >
              <HelpCircle className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={() => setShowLogger(true)}
              className="p-2 rounded-md text-slate-400 hover:bg-slate-700 hover:text-amber"
              title="System status"
            >
              <FileText className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
      {showLogger && <LoggerModal onClose={() => setShowLogger(false)} />}
    </>
  );
}
