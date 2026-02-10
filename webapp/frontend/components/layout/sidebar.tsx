'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Library,
  BookOpen,
  Search,
  Users,
  BookMarked,
  Tags,
  Building2,
  Download,
  Upload,
  FileText,
  Settings,
  HelpCircle,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
} from 'lucide-react';

const navItems = [
  { href: '/', label: 'Overview', icon: LayoutDashboard },
  { href: '/apps', label: 'Our Apps', icon: LayoutGrid },
  { href: '/libraries', label: 'Libraries', icon: Library },
  { href: '/books', label: 'Books', icon: BookOpen },
  { href: '/search', label: 'Search', icon: Search },
  { href: '/authors', label: 'Authors', icon: Users },
  { href: '/series', label: 'Series', icon: BookMarked },
  { href: '/tags', label: 'Tags', icon: Tags },
  { href: '/publishers', label: 'Publishers', icon: Building2 },
  { href: '/import', label: 'Import', icon: Upload },
  { href: '/export', label: 'Export', icon: Download },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/logs', label: 'Logs', icon: FileText },
  { href: '/settings', label: 'Settings', icon: Settings },
  { href: '/help', label: 'Help', icon: HelpCircle },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={`shrink-0 flex flex-col border-r border-slate-600 bg-slate-900 transition-[width] duration-200 ${
        collapsed ? 'w-16 min-w-[4rem]' : 'w-56 min-w-[14rem]'
      }`}
    >
      <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-amber/20 text-amber'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              } ${collapsed ? 'justify-center px-2' : ''}`}
              title={collapsed ? label : undefined}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>
      <button
        type="button"
        onClick={onToggle}
        className="flex items-center justify-center py-2 border-t border-slate-700 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
      </button>
    </aside>
  );
}
