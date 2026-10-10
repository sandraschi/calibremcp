'use client';

import { listLibraries, switchLibrary } from '@/common/api';
import {
  Activity,
  BookMarked,
  BookOpen,
  BookmarkCheck,
  Building2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Code2,
  CopyCheck,
  Download,
  FileText,
  FlaskConical,
  GitBranch,
  HelpCircle,
  Layers,
  LayoutDashboard,
  LayoutGrid,
  Library,
  ListChecks,
  MessageSquare,
  Search,
  Settings,
  Sparkles,
  Tags,
  TrendingUp,
  Upload,
  Users,
  Wrench,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';

interface NavItem {
  href: string;
  label: string;
  icon: typeof BookOpen;
}

interface NavGroup {
  id: string;
  label: string;
  icon: typeof BookOpen;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    id: 'content',
    label: 'Content',
    icon: Library,
    items: [
      { href: '/libraries', label: 'Libraries', icon: Library },
      { href: '/books', label: 'Books', icon: BookOpen },
      { href: '/authors', label: 'Authors', icon: Users },
      { href: '/series', label: 'Series', icon: BookMarked },
      { href: '/series/analysis', label: 'Series Analysis', icon: GitBranch },
      { href: '/tags', label: 'Tags', icon: Tags },
      { href: '/publishers', label: 'Publishers', icon: Building2 },
    ],
  },
  {
    id: 'discover',
    label: 'Discover',
    icon: Search,
    items: [
      { href: '/inbox', label: 'Inbox', icon: FileText },
      { href: '/search', label: 'Search', icon: Search },
      { href: '/rag', label: 'Semantic Search', icon: Sparkles },
      { href: '/collections', label: 'Collections', icon: BookmarkCheck },
      { href: '/curated', label: 'Curated', icon: FlaskConical },
      { href: '/reading', label: 'Reading & Priorities', icon: TrendingUp },
      { href: '/import', label: 'Import', icon: Upload },
      { href: '/export', label: 'Export', icon: Download },
    ],
  },
  {
    id: 'ai',
    label: 'AI & Tools',
    icon: Sparkles,
    items: [
      { href: '/chat', label: 'Chat', icon: MessageSquare },
      { href: '/agentic', label: 'Agentic', icon: GitBranch },
      { href: '/skills', label: 'Skills', icon: ListChecks },
      { href: '/tools', label: 'Tools', icon: Wrench },
    ],
  },
  {
    id: 'manage',
    label: 'Manage',
    icon: Wrench,
    items: [
      { href: '/library-health', label: 'Library Health', icon: Activity },
      { href: '/duplicates', label: 'Duplicates', icon: CopyCheck },
      { href: '/bulk', label: 'Bulk Ops', icon: Layers },
    ],
  },
  {
    id: 'system',
    label: 'System',
    icon: Settings,
    items: [
      { href: '/apps', label: 'Our Apps', icon: LayoutGrid },
      { href: '/api-docs', label: 'API Docs', icon: Code2 },
      { href: '/logs', label: 'Logs', icon: FileText },
      { href: '/settings', label: 'Settings', icon: Settings },
      { href: '/help', label: 'Help', icon: HelpCircle },
    ],
  },
];

const EXPANDED_KEY = 'calibre-sidebar-expanded';

function groupForPath(pathname: string): string | null {
  for (const g of NAV_GROUPS) {
    if (g.items.some((i) => (i.href === '/' ? pathname === '/' : pathname.startsWith(i.href)))) {
      return g.id;
    }
  }
  return null;
}

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [libraries, setLibraries] = useState<{ name: string; path: string; book_count?: number }[]>(
    [],
  );
  const [currentLibrary, setCurrentLibrary] = useState<string | null>(null);
  const [showLibDropdown, setShowLibDropdown] = useState(false);
  const [switching, setSwitching] = useState(false);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const libRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listLibraries()
      .then((data) => {
        setLibraries(data.libraries);
        setCurrentLibrary(data.current_library ?? null);
      })
      .catch(() => {});
  }, []);

  // Restore expanded groups; always keep the active group open.
  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(EXPANDED_KEY);
      setExpanded(raw ? (JSON.parse(raw) as Record<string, boolean>) : {});
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    const active = groupForPath(pathname ?? '');
    if (active) {
      setExpanded((prev) => (prev[active] ? prev : { ...prev, [active]: true }));
    }
  }, [pathname]);

  useEffect(() => {
    if (!showLibDropdown) return;
    const close = (e: MouseEvent) => {
      if (libRef.current && !libRef.current.contains(e.target as Node)) {
        setShowLibDropdown(false);
      }
    };
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, [showLibDropdown]);

  const toggleGroup = (id: string) => {
    setExpanded((prev) => {
      const next = { ...prev, [id]: !prev[id] };
      try {
        window.localStorage.setItem(EXPANDED_KEY, JSON.stringify(next));
      } catch {
        /* ignore */
      }
      return next;
    });
  };

  const handleSwitch = async (name: string) => {
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
      /* ignore */
    } finally {
      setSwitching(false);
    }
  };

  const currentLib = libraries.find((l) => l.name === currentLibrary);

  const isItemActive = (href: string) =>
    pathname === href || (href !== '/' && (pathname ?? '').startsWith(href));

  const itemCls = (active: boolean) =>
    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      active ? 'bg-amber/20 text-amber' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
    } ${collapsed ? 'justify-center px-2' : ''}`;

  return (
    <aside
      className={`shrink-0 flex flex-col border-r border-slate-600 bg-slate-900 transition-[width] duration-200 ${
        collapsed ? 'w-16 min-w-[4rem]' : 'w-64 min-w-[16rem]'
      }`}
    >
      {/* Current library indicator + collapse toggle */}
      <div
        className="px-3 pt-4 pb-2 border-b border-slate-700 flex items-start justify-between"
        ref={libRef}
      >
        <div className="min-w-0 flex-1">
          {collapsed ? (
            <div className="flex justify-center">
              <Library className="w-5 h-5 text-amber" />
            </div>
          ) : (
            <>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Current Library
              </div>
              <button
                type="button"
                onClick={() => setShowLibDropdown(!showLibDropdown)}
                disabled={switching || libraries.length === 0}
                className="flex items-center justify-between w-full rounded-md px-2 py-2 bg-slate-800 hover:bg-slate-700 text-left transition-colors group"
              >
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-amber truncate">
                    {currentLibrary || 'No library'}
                  </div>
                  {currentLib && (
                    <div className="text-xs text-slate-400">
                      {currentLib.book_count
                        ? `${currentLib.book_count.toLocaleString()} books`
                        : '—'}
                    </div>
                  )}
                </div>
                <ChevronDown
                  className={`w-4 h-4 shrink-0 text-slate-400 transition-transform ${showLibDropdown ? 'rotate-180' : ''}`}
                />
              </button>
              {showLibDropdown && (
                <div className="mt-1 py-1 max-h-64 overflow-auto rounded-md border border-slate-600 shadow-xl bg-slate-800">
                  {libraries.map((lib) => (
                    <button
                      key={lib.name}
                      type="button"
                      onClick={() => handleSwitch(lib.name)}
                      className={`block w-full text-left px-3 py-2 text-sm hover:bg-slate-700 ${
                        lib.name === currentLibrary ? 'text-amber font-medium' : 'text-slate-300'
                      }`}
                    >
                      <div className="truncate">{lib.name}</div>
                      {lib.book_count && (
                        <div className="text-xs text-slate-500">
                          {lib.book_count.toLocaleString()} books
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
        <button
          type="button"
          onClick={onToggle}
          className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-700 shrink-0 mt-1"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      <nav className="flex-1 py-2 px-2 space-y-0.5 overflow-y-auto" aria-label="Main navigation">
        {/* Overview stays top-level */}
        <Link
          href="/"
          aria-label="Overview"
          className={itemCls(pathname === '/')}
          title={collapsed ? 'Overview' : undefined}
        >
          <LayoutDashboard className="w-5 h-5 shrink-0" />
          {!collapsed && <span>Overview</span>}
        </Link>

        {collapsed
          ? // Collapsed: flat icon rail across all groups.
            NAV_GROUPS.flatMap((g) =>
              g.items.map(({ href, label, icon: Icon }) => (
                <Link
                  key={href}
                  href={href}
                  aria-label={label}
                  className={itemCls(isItemActive(href))}
                  title={label}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                </Link>
              )),
            )
          : NAV_GROUPS.map((group) => {
              const GroupIcon = group.icon;
              const open = !!expanded[group.id];
              const hasActive = group.items.some((i) => isItemActive(i.href));
              return (
                <div key={group.id} className="pt-1">
                  <button
                    type="button"
                    onClick={() => toggleGroup(group.id)}
                    aria-expanded={open}
                    className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-colors ${
                      hasActive
                        ? 'text-amber'
                        : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/60'
                    }`}
                  >
                    <GroupIcon className="w-4 h-4 shrink-0" />
                    <span className="flex-1 text-left">{group.label}</span>
                    <ChevronDown
                      className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`}
                    />
                  </button>
                  {open && (
                    <div className="ml-2 pl-2 border-l border-slate-700/60 space-y-0.5 mt-0.5">
                      {group.items.map(({ href, label, icon: Icon }) => (
                        <Link
                          key={href}
                          href={href}
                          aria-label={label}
                          className={itemCls(isItemActive(href))}
                        >
                          <Icon className="w-5 h-5 shrink-0" />
                          <span>{label}</span>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
      </nav>
    </aside>
  );
}
