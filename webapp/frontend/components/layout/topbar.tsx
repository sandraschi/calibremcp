"use client";

import { useConnection } from "@/app/store/connection";
import {
	API_BASE,
	type FleetApp,
	fetchFleetStatus,
	getHelp,
	getSystemStatus,
} from "@/common/api";
import {
	ChevronDown,
	ExternalLink,
	FileText,
	HelpCircle,
	Minus,
	Moon,
	Plus,
	Sun,
	Wifi,
	WifiOff,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { HelpModal } from "./help-modal";
import { LoggerModal } from "./logger-modal";

async function checkUrlUp(url: string, timeoutMs = 2500): Promise<boolean> {
	try {
		const c = new AbortController();
		const t = setTimeout(() => c.abort(), timeoutMs);
		const r = await fetch(url, {
			method: "GET",
			signal: c.signal,
			cache: "no-store",
		});
		clearTimeout(t);
		return r.ok;
	} catch {
		return false;
	}
}

interface LaunchModalState {
	label: string;
	url: string;
	status: "starting" | "done" | "error";
	error?: string;
}

// EXPERIMENTAL light mode (invert hack). Not fleet standard — see globals.css.
// Toggling `.dark` off the root flips the invert filter; persisted so the
// choice survives reloads. Delete this + the CSS block to revert.
const THEME_KEY = "calibre-light-mode";

function useExperimentalTheme() {
	const [light, setLight] = useState(() => {
		if (typeof window === "undefined") return false;
		try {
			return localStorage.getItem(THEME_KEY) === "1";
		} catch {
			return false;
		}
	});

	useEffect(() => {
		document.documentElement.classList.toggle("dark", !light);
		try {
			localStorage.setItem(THEME_KEY, light ? "1" : "0");
		} catch {
			// ignore storage errors
		}
	}, [light]);

	return { light, toggle: () => setLight((v) => !v) };
}

export function Topbar() {
	const [showZoo, setShowZoo] = useState(false);
	const [showHelp, setShowHelp] = useState(false);
	const [showLogger, setShowLogger] = useState(false);
	const [launchModal, setLaunchModal] = useState<LaunchModalState | null>(null);
	const [fleetApps, setFleetApps] = useState<FleetApp[]>([]);
	const [fleetLoading, setFleetLoading] = useState(true);
	const zooRef = useRef<HTMLDivElement>(null);
	const { light, toggle } = useExperimentalTheme();

	useEffect(() => {
		let cancelled = false;
		const refresh = async () => {
			try {
				const data = await fetchFleetStatus();
				if (!cancelled) {
					setFleetApps(data.webapps.filter((a) => a.up));
					setFleetLoading(false);
				}
			} catch {
				if (!cancelled) setFleetLoading(false);
			}
		};
		refresh();
		const interval = setInterval(refresh, 30_000);
		return () => {
			cancelled = true;
			clearInterval(interval);
		};
	}, []);

	useEffect(() => {
		if (!showZoo) return;
		const close = (e: MouseEvent) => {
			if (zooRef.current && !zooRef.current.contains(e.target as Node))
				setShowZoo(false);
		};
		document.addEventListener("click", close);
		return () => document.removeEventListener("click", close);
	}, [showZoo]);

	const handleWebappClick = async (app: {
		label: string;
		url: string;
		port?: number;
	}) => {
		setShowZoo(false);
		const url = app.url;
		const up = await checkUrlUp(url);
		if (up) {
			window.open(url, "_blank", "noopener,noreferrer");
			return;
		}
		if (app.port == null) {
			window.open(url, "_blank", "noopener,noreferrer");
			return;
		}
		setLaunchModal({ label: app.label, url, status: "starting" });
		try {
			const r = await fetch(`${API_BASE}/api/webapp-launch`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ port: app.port }),
			});
			const data = await r.json().catch(() => ({}));
			if (!r.ok) {
				setLaunchModal((m) =>
					m
						? {
								...m,
								status: "error",
								error: data.detail ?? data.error ?? `HTTP ${r.status}`,
							}
						: null,
				);
				return;
			}
			if (data.error) {
				setLaunchModal((m) =>
					m ? { ...m, status: "error", error: data.error } : null,
				);
				return;
			}
			setLaunchModal((m) => (m ? { ...m, status: "done" } : null));
			window.open(url, "_blank", "noopener,noreferrer");
			setTimeout(() => setLaunchModal(null), 1500);
		} catch (e) {
			setLaunchModal((m) =>
				m
					? {
							...m,
							status: "error",
							error: e instanceof Error ? e.message : "Request failed",
						}
					: null,
			);
		}
	};

	return (
		<>
			<header
				className="sticky top-0 z-50 border-b border-slate-700 shadow-sm"
				style={{ backgroundColor: "var(--background)" }}
			>
				<div className="container mx-auto px-4 h-14 flex items-center justify-between gap-4">
					<Link
						href="/"
						className="font-heading text-xl font-semibold text-amber shrink-0"
					>
						Calibre
					</Link>

					<div className="flex-1" />

					<div className="flex items-center gap-2 shrink-0">
						{/* Connection Status */}
						<ConnectionBadge />
						<button
							type="button"
							onClick={toggle}
							className="p-2 rounded-md text-slate-400 hover:bg-slate-700 hover:text-amber"
							title={light ? "Switch to dark (experimental light mode)" : "Switch to light (experimental, ugly)"}
							aria-label="Toggle light mode (experimental)"
						>
							{light ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
						</button>
						<div className="relative" ref={zooRef}>
							<button
								type="button"
								onClick={() => setShowZoo(!showZoo)}
								className="flex items-center gap-1.5 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-700/50 hover:text-amber text-sm"
								title="Jump to other webapps"
							>
								<ExternalLink className="w-4 h-4" />
								<span className="hidden sm:inline">Webapps</span>
								<ChevronDown
									className={`w-4 h-4 transition-transform ${showZoo ? "rotate-180" : ""}`}
								/>
							</button>
							{showZoo && (
								<div
									className="absolute right-0 mt-1 py-1 w-56 max-h-80 overflow-auto rounded-lg border border-slate-600 shadow-xl z-50"
									style={{ backgroundColor: "rgb(30, 41, 59)" }}
								>
									{fleetLoading && (
										<div className="px-4 py-2 text-xs text-slate-500">
											Scanning fleet ports...
										</div>
									)}
									{!fleetLoading && fleetApps.length === 0 && (
										<div className="px-4 py-2 text-xs text-slate-500">
											No fleet webapps detected
										</div>
									)}
									{fleetApps.map((app) => (
										<button
											key={app.url}
											type="button"
											onClick={() => handleWebappClick(app)}
											className="block w-full text-left px-4 py-2 text-sm text-slate-200 hover:bg-slate-700/80 hover:text-amber"
										>
											<span className="inline-block w-2 h-2 rounded-full bg-emerald-400 mr-2 align-middle" />
											{app.label}
											<span className="text-slate-500 text-xs ml-1">
												:{app.port}
											</span>
										</button>
									))}
									<Link
										href="/apps"
										onClick={() => setShowZoo(false)}
										className="block w-full text-left px-4 py-2 text-sm text-slate-400 hover:bg-slate-700/80 hover:text-amber border-t border-slate-600 mt-1"
									>
										Our Apps (full list)
									</Link>
								</div>
							)}
						</div>
						<ZoomControls />
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
							title="Logs"
						>
							<FileText className="w-5 h-5" />
						</button>
					</div>
				</div>
			</header>

			{showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
			{showLogger && <LoggerModal onClose={() => setShowLogger(false)} />}
			{launchModal && (
				<div
					className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50"
					role="dialog"
					aria-modal="true"
				>
					<div className="rounded-lg bg-slate-800 border border-slate-600 shadow-xl px-6 py-4 max-w-sm text-center">
						{launchModal.status === "starting" && (
							<>
								<p className="text-slate-200 font-medium">
									Starting {launchModal.label}
								</p>
								<p className="text-slate-400 text-sm mt-1">Please wait...</p>
							</>
						)}
						{launchModal.status === "done" && (
							<p className="text-amber">Opened {launchModal.label}</p>
						)}
						{launchModal.status === "error" && (
							<>
								<p className="text-red-400 font-medium">
									Could not start {launchModal.label}
								</p>
								<p className="text-slate-400 text-sm mt-1">
									{launchModal.error}
								</p>
								<p className="text-slate-500 text-xs mt-2">
									Run the start script in the repo manually.
								</p>
								<button
									type="button"
									onClick={() => setLaunchModal(null)}
									className="mt-3 px-4 py-2 rounded bg-slate-700 text-slate-200 hover:bg-slate-600 text-sm"
								>
									Close
								</button>
							</>
						)}
					</div>
				</div>
			)}
		</>
	);
}

function ConnectionBadge() {
	const { state, lastError } = useConnection();

	const colorMap: Record<string, string> = {
		connected: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
		connecting: "bg-amber-500/10 text-amber-500 border-amber-500/20",
		offline: "bg-red-500/10 text-red-500 border-red-500/20",
		error: "bg-red-500/10 text-red-500 border-red-500/20",
	};

	const labelMap: Record<string, string> = {
		connected: "System Online",
		connecting: "Connecting...",
		offline: `Offline${lastError ? ` (${lastError.slice(0, 60)})` : ""}`,
		error: `Error${lastError ? ` (${lastError.slice(0, 60)})` : ""}`,
	};

	return (
		<div
			data-testid="connection-status"
			className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs border ${colorMap[state] || colorMap.connecting}`}
		>
			<span className="relative flex h-2 w-2">
				{state !== "offline" && state !== "error" && (
					<span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-75" />
				)}
				<span className="relative inline-flex h-2 w-2 rounded-full bg-current" />
			</span>
			<span data-testid="connection-label">
				{labelMap[state] || "Connecting..."}
			</span>
		</div>
	);
}

const ZOOM_LEVELS = [0.8, 1.0, 1.25, 1.5, 2.0, 3.0];

function applyZoomCSS(level: number) {
	document.documentElement.style.zoom = String(level);
}

function ZoomControls() {
	const [level, setLevel] = useState(1.0);

	// Read saved zoom from localStorage after mount to avoid hydration mismatch
	useEffect(() => {
		const saved = (() => {
			try {
				const raw = localStorage.getItem("tauri-zoom");
				return raw ? Number.parseFloat(raw) : null;
			} catch {
				return null;
			}
		})();
		if (saved && ZOOM_LEVELS.includes(saved)) setLevel(saved);
	}, []);

	// Sync with external zoom changes (cross-tab)
	useEffect(() => {
		const sync = () => {
			try {
				const raw = localStorage.getItem("tauri-zoom");
				if (raw) {
					const parsed = Number.parseFloat(raw);
					if (ZOOM_LEVELS.includes(parsed)) setLevel(parsed);
				}
			} catch {}
		};
		window.addEventListener("storage", sync);
		return () => window.removeEventListener("storage", sync);
	}, []);

	const change = (direction: 1 | -1 | "reset") => {
		let next: number;
		if (direction === "reset") {
			next = 1.0;
		} else {
			const i = ZOOM_LEVELS.indexOf(level) + direction;
			if (i < 0 || i >= ZOOM_LEVELS.length) return;
			next = ZOOM_LEVELS[i];
		}
		localStorage.setItem("tauri-zoom", String(next));
		applyZoomCSS(next);
		setLevel(next);
	};

	const atMin = level <= ZOOM_LEVELS[0];
	const atMax = level >= ZOOM_LEVELS[ZOOM_LEVELS.length - 1];

	return (
		<div
			className="flex items-center gap-0.5 text-slate-400"
			title={`Zoom: ${Math.round(level * 100)}%`}
		>
			<button
				type="button"
				onClick={() => change(-1)}
				disabled={atMin}
				className="p-1 rounded hover:bg-slate-700 hover:text-amber disabled:opacity-30 disabled:cursor-not-allowed"
			>
				<Minus size={14} />
			</button>
			<span className="text-xs w-8 text-center select-none tabular-nums">
				{Math.round(level * 100)}%
			</span>
			<button
				type="button"
				onClick={() => change(1)}
				disabled={atMax}
				className="p-1 rounded hover:bg-slate-700 hover:text-amber disabled:opacity-30 disabled:cursor-not-allowed"
			>
				<Plus size={14} />
			</button>
		</div>
	);
}
