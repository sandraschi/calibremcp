"use client";

import { API_BASE, type FleetApp, fetchFleetStatus } from "@/common/api";
import { ExternalLink, Loader2, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";

type LaunchStatus = "idle" | "starting" | "done" | "error";

export default function OurAppsPage() {
	const [apps, setApps] = useState<FleetApp[]>([]);
	const [containers, setContainers] = useState<FleetApp[]>([]);
	const [loading, setLoading] = useState(true);
	const [launchTarget, setLaunchTarget] = useState<{
		app: FleetApp;
		status: LaunchStatus;
		error?: string;
	} | null>(null);

	useEffect(() => {
		let cancelled = false;
		fetchFleetStatus()
			.then((data) => {
				if (!cancelled) {
					setApps(data.webapps);
					setContainers(data.containers);
					setLoading(false);
				}
			})
			.catch(() => {
				if (!cancelled) setLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	const handleOpen = async (app: FleetApp) => {
		const url = app.url;
		if (app.up) {
			window.open(url, "_blank", "noopener,noreferrer");
			return;
		}
		setLaunchTarget({ app, status: "starting" });
		try {
			const r = await fetch(`${API_BASE}/api/webapp-launch`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ port: app.port }),
			});
			const data = await r.json().catch(() => ({}));
			if (!r.ok) {
				setLaunchTarget((t) =>
					t
						? {
								...t,
								status: "error",
								error: (data.detail ??
									data.error ??
									`HTTP ${r.status}`) as string,
							}
						: null,
				);
				return;
			}
			if (data.error) {
				setLaunchTarget((t) =>
					t ? { ...t, status: "error", error: data.error } : null,
				);
				return;
			}
			setLaunchTarget((t) => (t ? { ...t, status: "done" } : null));
			window.open(url, "_blank", "noopener,noreferrer");
			setTimeout(() => setLaunchTarget(null), 1500);
		} catch (e) {
			setLaunchTarget((t) =>
				t
					? {
							...t,
							status: "error",
							error: e instanceof Error ? e.message : "Request failed",
						}
					: null,
			);
		}
	};

	if (loading) {
		return (
			<div className="container mx-auto p-6 flex items-center justify-center min-h-[50vh]">
				<Loader2 className="w-6 h-6 text-amber animate-spin" />
				<span className="ml-3 text-slate-400">Scanning fleet ports...</span>
			</div>
		);
	}

	return (
		<div className="container mx-auto p-6">
			<h1 className="text-3xl font-bold mb-2 text-slate-100">Our Apps</h1>
			<p className="text-slate-400 mb-8 max-w-2xl">
				Fleet webapps and containers discovered by probing known ports. Green =
				reachable, red = down.
			</p>

			<section className="mb-10">
				<h2 className="text-xl font-semibold text-slate-200 mb-4">
					Webapps ({apps.length})
				</h2>
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
					{apps.map((app) => {
						const launching = launchTarget?.app.url === app.url;
						return (
							<article
								key={app.url}
								className={`rounded-lg border p-4 flex flex-col ${app.up ? "border-emerald-500/30 bg-slate-800/80" : "border-slate-600 bg-slate-800/50"}`}
							>
								<div className="flex items-start justify-between gap-2 mb-2">
									<div className="flex items-center gap-2 min-w-0">
										{app.up ? (
											<Wifi className="w-4 h-4 text-emerald-400 shrink-0" />
										) : (
											<WifiOff className="w-4 h-4 text-red-400 shrink-0" />
										)}
										<h3 className="font-semibold text-slate-100 text-sm truncate">
											{app.label}
										</h3>
									</div>
									<span className="text-slate-500 text-xs shrink-0">
										:{app.port}
									</span>
								</div>
								<p className="text-slate-400 text-xs mb-3 flex-1">
									{app.description}
								</p>
								<button
									type="button"
									onClick={() => handleOpen(app)}
									disabled={launching && launchTarget?.status === "starting"}
									className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-amber/20 text-amber hover:bg-amber/30 text-sm font-medium disabled:opacity-60 self-start"
								>
									<ExternalLink className="w-3.5 h-3.5" />
									{launching && launchTarget?.status === "starting"
										? "Launching…"
										: app.up
											? "Open"
											: "Start"}
								</button>
							</article>
						);
					})}
				</div>
			</section>

			<section>
				<h2 className="text-xl font-semibold text-slate-200 mb-4">
					Containers ({containers.length})
				</h2>
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
					{containers.map((c) => (
						<article
							key={c.url}
							className={`rounded-lg border p-4 flex flex-col ${c.up ? "border-emerald-500/30 bg-slate-800/80" : "border-slate-600 bg-slate-800/50"}`}
						>
							<div className="flex items-start justify-between gap-2 mb-2">
								<div className="flex items-center gap-2 min-w-0">
									{c.up ? (
										<Wifi className="w-4 h-4 text-emerald-400 shrink-0" />
									) : (
										<WifiOff className="w-4 h-4 text-red-400 shrink-0" />
									)}
									<h3 className="font-semibold text-slate-100 text-sm truncate">
										{c.label}
									</h3>
								</div>
								<span className="text-slate-500 text-xs shrink-0">
									:{c.port}
								</span>
							</div>
							<p className="text-slate-400 text-xs">{c.description}</p>
						</article>
					))}
				</div>
			</section>

			{launchTarget?.status === "error" && (
				<div
					className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50"
					role="dialog"
					aria-modal="true"
				>
					<div className="rounded-lg bg-slate-800 border border-slate-600 shadow-xl px-6 py-4 max-w-sm text-center">
						<p className="text-red-400 font-medium">
							Could not start {launchTarget.app.label}
						</p>
						<p className="text-slate-400 text-sm mt-1">{launchTarget.error}</p>
						<p className="text-slate-500 text-xs mt-2">
							Run the start script in the repo manually.
						</p>
						<button
							type="button"
							onClick={() => setLaunchTarget(null)}
							className="mt-3 px-4 py-2 rounded bg-slate-700 text-slate-200 hover:bg-slate-600 text-sm"
						>
							Close
						</button>
					</div>
				</div>
			)}
		</div>
	);
}
