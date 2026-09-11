'use client';

import { getContentServerUrl, getLibraryStats } from '@/common/api';
import {
  Activity,
  BookMarked,
  BookOpen,
  BookmarkCheck,
  CopyCheck,
  ExternalLink,
  Globe,
  Library,
  MessageSquare,
  Search,
  Sparkles,
  Tags,
  TrendingUp,
  Users,
} from 'lucide-react';
import Link from 'next/link';
import { Suspense, useEffect, useState } from 'react';

function HomePageInner() {
  const [stats, setStats] = useState<{
    total_books: number;
    total_authors: number;
    total_series: number;
    total_tags: number;
    library_name: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getLibraryStats()
      .then((s) => {
        if (!cancelled) {
          setStats({
            total_books: s.total_books,
            total_authors: s.total_authors,
            total_series: s.total_series,
            total_tags: s.total_tags,
            library_name: s.library_name,
          });
        }
      })
      .catch(() => {
        if (!cancelled) setStats(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const cards = [
    {
      href: '/books',
      label: 'Books',
      value: stats?.total_books ?? '—',
      icon: BookOpen,
    },
    {
      href: '/authors',
      label: 'Authors',
      value: stats?.total_authors ?? '—',
      icon: Users,
    },
    {
      href: '/series',
      label: 'Series',
      value: stats?.total_series ?? '—',
      icon: BookMarked,
    },
    {
      href: '/tags',
      label: 'Tags',
      value: stats?.total_tags ?? '—',
      icon: Tags,
    },
  ];

  if (loading) {
    return (
      <main className="min-h-screen">
        <div className="container mx-auto p-6">
          <p className="text-slate-400">Loading overview…</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      <div className="container mx-auto p-6 space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-1 text-slate-100">Overview</h1>
          {stats?.library_name && (
            <p className="text-slate-400 text-sm">
              Active Library:{' '}
              <span className="text-slate-200 font-medium">{stats.library_name}</span>
            </p>
          )}
        </div>

        {/* Calibre Content Server Live Banner */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-slate-800 via-slate-800/90 to-slate-900 border border-slate-700/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow">
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-100">Calibre Content Server</span>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-800/70">
                  ONLINE
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Modern web reader with offline reading, bookmarks & OPDS active at{' '}
                <code className="text-[11px] text-amber">{getContentServerUrl()}</code>
              </p>
            </div>
          </div>
          <a
            href={getContentServerUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-amber text-slate-950 text-xs font-bold hover:bg-amber/90 transition-colors shadow shrink-0"
          >
            <span>Open Web Reader</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        {/* Core Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {cards.map(({ href, label, value, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className="block p-6 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-amber/50 transition-colors shadow-sm"
            >
              <Icon className="w-7 h-7 text-amber mb-2" />
              <p className="text-2xl font-bold text-slate-100">{value}</p>
              <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider">{label}</p>
            </Link>
          ))}
        </div>

        {/* Advanced Tools & Discovery Grid */}
        <div className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
            Library Operations & AI Tools
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              href="/library-health"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <Activity className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">Library Health</span>
                <span className="text-[11px] text-slate-400">Integrity & missing metadata</span>
              </div>
            </Link>
            <Link
              href="/duplicates"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <CopyCheck className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">Duplicates</span>
                <span className="text-[11px] text-slate-400">Find duplicate editions</span>
              </div>
            </Link>
            <Link
              href="/reading"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <TrendingUp className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">
                  Reading & Priorities
                </span>
                <span className="text-[11px] text-slate-400">Prioritized unread queue</span>
              </div>
            </Link>
            <Link
              href="/collections"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <BookmarkCheck className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">Collections</span>
                <span className="text-[11px] text-slate-400">Dynamic virtual shelves</span>
              </div>
            </Link>
            <Link
              href="/rag"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <Sparkles className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">Semantic Search</span>
                <span className="text-[11px] text-slate-400">LanceDB vector RAG</span>
              </div>
            </Link>
            <Link
              href="/chat"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <MessageSquare className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">AI Chat</span>
                <span className="text-[11px] text-slate-400">Ollama / OpenAI assistant</span>
              </div>
            </Link>
            <Link
              href="/search"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <Search className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">Search</span>
                <span className="text-[11px] text-slate-400">Filter tags, authors, text</span>
              </div>
            </Link>
            <Link
              href="/libraries"
              className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/70 border border-slate-700 hover:border-amber/50 transition-colors"
            >
              <Library className="w-5 h-5 text-amber shrink-0" />
              <div>
                <span className="text-slate-200 text-sm font-semibold block">Libraries</span>
                <span className="text-[11px] text-slate-400">Switch & manage catalogs</span>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}

export default function Home() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen">
          <div className="container mx-auto p-6">
            <p className="text-slate-400">Loading…</p>
          </div>
        </main>
      }
    >
      <HomePageInner />
    </Suspense>
  );
}
