"use client";

import { listLibraries, switchLibrary } from "@/common/api";
import {
	BookMarked,
	BookOpen,
	Building2,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	Code2,
	Download,
	FileText,
	GitBranch,
	HelpCircle,
	LayoutDashboard,
	LayoutGrid,
	Library,
	ListChecks,
	MessageSquare,
	Search,
	Settings,
	Sparkles,
	Tags,
	Upload,
	Users,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const navItems = [
	{ href: "/", label: "Overview", icon: LayoutDashboard },
	{ href: "/apps", label: "Our Apps", icon: LayoutGrid },
	{ href: "/books", label: "Books", icon: BookOpen },
	{ href: "/search", label: "Search", icon: Search },
	{ href: "/rag", label: "Semantic Search", icon: Sparkles },
	{ href: "/skills", label: "Skills", icon: ListChecks },
	{ href: "/agentic", label: "Agentic", icon: GitBranch },
	{ href: "/authors", label: "Authors", icon: Users },
	{ href: "/series", label: "Series", icon: BookMarked },
	{ href: "/series/analysis", label: "Series Analysis", icon: GitBranch },
	{ href: "/tags", label: "Tags", icon: Tags },
	{ href: "/publishers", label: "Publishers", icon: Building2 },
	{ href: "/import", label: "Import", icon: Upload },
	{ href: "/export", label: "Export", icon: Download },
	{ href: "/chat", label: "Chat", icon: MessageSquare },
	{ href: "/api-docs", label: "API Docs", icon: Code2 },
	{ href: "/logs", label: "Logs", icon: FileText },
	{ href: "/settings", label: "Settings", icon: Settings },
	{ href: "/help", label: "Help", icon: HelpCircle },
];

interface SidebarProps {
	collapsed: boolean;
	onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
	const pathname = usePathname();
	const router = useRouter();
	const [libraries, setLibraries] = useState<
		{ name: string; path: string; book_count?: number }[]
	>([]);
	const [currentLibrary, setCurrentLibrary] = useState<string | null>(null);
	const [showLibDropdown, setShowLibDropdown] = useState(false);
	const [switching, setSwitching] = useState(false);
	const libRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		listLibraries()
			.then((data) => {
				setLibraries(data.libraries);
				setCurrentLibrary(data.current_library ?? null);
			})
			.catch(() => {});
	}, []);

	useEffect(() => {
		if (!showLibDropdown) return;
		const close = (e: MouseEvent) => {
			if (libRef.current && !libRef.current.contains(e.target as Node)) {
				setShowLibDropdown(false);
			}
		};
		document.addEventListener("click", close);
		return () => document.removeEventListener("click", close);
	}, [showLibDropdown]);

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

	return (
		<aside
			className={`shrink-0 flex flex-col border-r border-slate-600 bg-slate-900 transition-[width] duration-200 ${
				collapsed ? "w-16 min-w-[4rem]" : "w-64 min-w-[16rem]"
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
										{currentLibrary || "No library"}
									</div>
									{currentLib && (
										<div className="text-xs text-slate-400">
											{currentLib.book_count
												? `${currentLib.book_count.toLocaleString()} books`
												: "—"}
										</div>
									)}
								</div>
								<ChevronDown
									className={`w-4 h-4 shrink-0 text-slate-400 transition-transform ${showLibDropdown ? "rotate-180" : ""}`}
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
												lib.name === currentLibrary
													? "text-amber font-medium"
													: "text-slate-300"
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
					title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
				>
					{collapsed ? (
						<ChevronRight className="w-4 h-4" />
					) : (
						<ChevronLeft className="w-4 h-4" />
					)}
				</button>
			</div>

			<nav className="flex-1 py-2 px-2 space-y-0.5 overflow-y-auto">
				{navItems.map(({ href, label, icon: Icon }) => {
					const isActive =
						pathname === href || (href !== "/" && pathname.startsWith(href));
					return (
						<Link
							key={href}
							href={href}
							aria-label={label}
							className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
								isActive
									? "bg-amber/20 text-amber"
									: "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
							} ${collapsed ? "justify-center px-2" : ""}`}
							title={collapsed ? label : undefined}
						>
							<Icon className="w-5 h-5 shrink-0" />
							{!collapsed && <span>{label}</span>}
						</Link>
					);
				})}
			</nav>
		</aside>
	);
}
