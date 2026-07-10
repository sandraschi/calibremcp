"use client";

import { getLogs } from "@/common/api";
import { RefreshCw } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface LoggerModalProps {
	onClose: () => void;
}

function levelColor(line: string): string {
	const upper = line.toUpperCase();
	if (upper.includes("ERROR")) return "text-red-400";
	if (upper.includes("WARN") || upper.includes("WARNING"))
		return "text-yellow-400";
	if (upper.includes("INFO")) return "text-green-400";
	if (upper.includes("DEBUG") || upper.includes("TRACE"))
		return "text-zinc-500";
	return "text-zinc-300";
}

export function LoggerModal({ onClose }: LoggerModalProps) {
	const [lines, setLines] = useState<string[]>([]);
	const [filter, setFilter] = useState("");
	const [error, setError] = useState("");
	const [autoScroll, setAutoScroll] = useState(true);
	const [minLevel, setMinLevel] = useState("DEBUG");
	const bottomRef = useRef<HTMLDivElement>(null);
	const scrollRef = useRef<HTMLDivElement>(null);

	const LEVEL_ORDER = ["ERROR", "WARN", "INFO", "DEBUG"];

	function lineLevel(line: string): string {
		const upper = line.toUpperCase();
		if (upper.includes("ERROR")) return "ERROR";
		if (upper.includes("WARN") || upper.includes("WARNING")) return "WARN";
		if (upper.includes("INFO")) return "INFO";
		if (upper.includes("DEBUG") || upper.includes("TRACE")) return "DEBUG";
		return "INFO";
	}

	function levelRank(lvl: string): number {
		const idx = LEVEL_ORDER.indexOf(lvl);
		return idx >= 0 ? idx : -1;
	}

	const filteredLines = lines.filter(
		(line) => levelRank(lineLevel(line)) <= levelRank(minLevel),
	);

	const load = () => {
		setError("");
		getLogs({ tail: 200, filter: filter || undefined })
			.then((data) => {
				setLines(data.lines ?? []);
				if (data.error) setError(data.error);
			})
			.catch((e) =>
				setError(e instanceof Error ? e.message : "Failed to load logs"),
			);
	};

	useEffect(() => {
		load();
	}, [filter]);

	useEffect(() => {
		if (autoScroll) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [lines, autoScroll]);

	const handleScroll = () => {
		if (!scrollRef.current) return;
		const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
		const atBottom = scrollHeight - scrollTop - clientHeight < 40;
		if (!atBottom) setAutoScroll(false);
	};

	return (
		<div
			className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950"
			onClick={onClose}
		>
			<div
				className="border border-slate-600 rounded-lg shadow-xl max-w-4xl w-full max-h-[85vh] flex flex-col"
				style={{ backgroundColor: "#1e293b" }}
				onClick={(e) => e.stopPropagation()}
			>
				{/* Header */}
				<div className="flex items-center justify-between p-4 border-b border-slate-600">
					<h2 className="text-lg font-semibold text-amber">Logs</h2>
					<div className="flex items-center gap-2">
						<select
							value={minLevel}
							onChange={(e) => setMinLevel(e.target.value)}
							className="px-2 py-1 rounded text-xs bg-slate-800 border border-slate-600 text-zinc-300"
						>
							<option value="ERROR">Error</option>
							<option value="WARN">Warning</option>
							<option value="INFO">Info</option>
							<option value="DEBUG">Debug</option>
						</select>
						<input
							type="text"
							value={filter}
							onChange={(e) => setFilter(e.target.value)}
							placeholder="Search..."
							className="px-3 py-1 rounded bg-slate-700 text-slate-200 text-sm placeholder-slate-500 w-36"
						/>
						<button
							type="button"
							onClick={load}
							className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-700"
							title="Refresh"
						>
							<RefreshCw size={16} />
						</button>
						<button
							type="button"
							onClick={() => setAutoScroll(!autoScroll)}
							className={`px-2 py-1 rounded text-xs border ${
								autoScroll
									? "bg-amber/20 border-amber/50 text-amber"
									: "bg-slate-700 border-slate-600 text-slate-400"
							}`}
							title="Toggle auto-scroll"
						>
							Auto
						</button>
						<button
							type="button"
							onClick={onClose}
							className="text-slate-400 hover:text-white ml-1"
						>
							Close
						</button>
					</div>
				</div>

				{error && (
					<div className="px-4 py-2 text-sm text-red-400 border-b border-slate-600">
						{error}
					</div>
				)}

				{/* Log lines */}
				<div
					ref={scrollRef}
					onScroll={handleScroll}
					className="p-4 overflow-auto text-xs font-mono flex-1 leading-5"
				>
					{filteredLines.length === 0 && !error && (
						<span className="text-slate-500">No log entries</span>
					)}
					{filteredLines.map((line, i) => (
						<div key={i} className={levelColor(line)}>
							{line}
						</div>
					))}
					<div ref={bottomRef} />
				</div>
			</div>
		</div>
	);
}
