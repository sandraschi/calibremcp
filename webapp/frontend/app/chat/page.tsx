"use client";

import { API_BASE, listSkills } from "@/common/api";
import { Download, Trash2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

interface Message {
	role: "user" | "assistant";
	content: string;
	ts?: string;
}

const STORAGE_KEY = "calibre-mcp-chat-history";
const PERSONALITY_KEY = "calibre-mcp-chat-personality";
const MAX_MESSAGES = 100;

const PERSONALITIES = [
	{ id: "default", label: "Default", preprompt: "" },
	{
		id: "librarian",
		label: "Librarian",
		preprompt:
			"You are a helpful librarian assistant. Be concise and focus on book recommendations, metadata, and library organization.",
	},
	{
		id: "casual",
		label: "Casual Reader",
		preprompt:
			"You are a friendly book lover. Chat naturally about books, reading habits, and recommendations.",
	},
	{
		id: "scholar",
		label: "Scholar",
		preprompt:
			"You are an academic scholar. Provide detailed analysis of books, authors, and literary themes. Cite metadata when relevant.",
	},
	{
		id: "custom",
		label: "Custom",
		preprompt: "",
	},
];

function buildSystemPrompt(
	skillPrompt: string,
	personalityPrompt: string,
	context: string,
): string {
	const parts = [skillPrompt, context].filter(Boolean).join("\n\n---\n\n");
	if (!personalityPrompt) return parts || "";
	return `${parts}\n\n---\n\n## Role\n${personalityPrompt}`;
}

const EXAMPLE_PROMPTS = [
	"What books do I have by Tolkien?",
	"Recommend unread books in my library",
	"Find books about science fiction",
	"What series are incomplete?",
	"Show me recently added books",
	"Summarize my library stats",
];

function loadMessages(): Message[] {
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (raw) return JSON.parse(raw);
	} catch {}
	return [];
}

function saveMessages(msgs: Message[]) {
	try {
		const trimmed = msgs.slice(-MAX_MESSAGES);
		localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
	} catch {}
}

function loadPersonality(): string {
	try {
		return localStorage.getItem(PERSONALITY_KEY) || "default";
	} catch {}
	return "default";
}

async function checkProvider(): Promise<"connected" | "offline" | "detecting"> {
	try {
		const r = await fetch(`${API_BASE}/health`);
		if (r.ok) return "connected";
	} catch {}
	return "offline";
}

export default function ChatPage() {
	const [messages, setMessages] = useState<Message[]>(loadMessages);
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [model, setModel] = useState("");
	const [providerStatus, setProviderStatus] = useState<
		"connected" | "offline" | "detecting"
	>("detecting");
	const [personality, setPersonality] = useState(loadPersonality);
	const [skillContent, setSkillContent] = useState("");
	const [skillName, setSkillName] = useState("");
	const [contextInfo, setContextInfo] = useState("");
	const [customPrompt, setCustomPrompt] = useState("");

	// Load custom prompt and saved model from localStorage
	useEffect(() => {
		try {
			const saved = localStorage.getItem("calibre-mcp-chat-custom-prompt");
			if (saved) setCustomPrompt(saved);
		} catch {}
		try {
			const saved = localStorage.getItem("calibre-webapp-default-llm-model");
			if (saved) setModel(saved);
		} catch {}
	}, []);
	const bottomRef = useRef<HTMLDivElement>(null);

	const scrollToBottom = useCallback(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, []);

	useEffect(() => {
		scrollToBottom();
	}, [messages, scrollToBottom]);

	// Persist messages on every change
	useEffect(() => {
		saveMessages(messages);
	}, [messages]);

	// Persist personality selection
	useEffect(() => {
		try {
			localStorage.setItem(PERSONALITY_KEY, personality);
		} catch {}
	}, [personality]);

	// Provider detection + model discovery
	useEffect(() => {
		let cancelled = false;
		(async () => {
			const status = await checkProvider();
			if (cancelled) return;
			setProviderStatus(status);

			try {
				const r = await fetch(`${API_BASE}/api/llm/models`);
				if (r.ok) {
					const data = await r.json();
					const apiModels: string[] = data.models ?? [];
					if (apiModels.length > 0) {
						const saved = localStorage.getItem(
							"calibre-webapp-default-llm-model",
						);
						if (!saved || !apiModels.includes(saved)) setModel(apiModels[0]);
					}
				}
			} catch {}

			// Load primary skill as base system prompt
			try {
				const skillsData = await listSkills();
				if (!cancelled && skillsData.skills?.length > 0) {
					const primary = skillsData.skills[0];
					setSkillContent(primary.prompt || "");
					setSkillName(primary.name || primary.id || "");
				}
			} catch {}

			// Fetch live library context
			try {
				const r = await fetch(`${API_BASE}/api/libraries/list`);
				if (r.ok) {
					const libData: {
						libraries: Array<{ name: string; book_count?: number }>;
						current_library?: string;
					} = await r.json();
					if (libData.libraries?.length > 0) {
						const libSummary = libData.libraries
							.map(
								(lib) =>
									`  - ${lib.name}${lib.name === libData.current_library ? " (active)" : ""} (${lib.book_count ?? "?"} books)`,
							)
							.join("\n");
						setContextInfo(`\n\n## Your Calibre Libraries\n\n${libSummary}`);
					}
				}
			} catch {}
		})();
		return () => {
			cancelled = true;
		};
	}, []);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!input.trim() || loading) return;
		const userMsg: Message = {
			role: "user",
			content: input.trim(),
			ts: new Date().toISOString(),
		};
		const updated = [...messages, userMsg];
		setMessages(updated);
		setInput("");
		setLoading(true);

		const useCustom = personality === "custom";
		const preprompt = useCustom
			? customPrompt
			: (PERSONALITIES.find((p) => p.id === personality)?.preprompt ?? "");
		const systemContent = buildSystemPrompt(
			skillContent,
			preprompt,
			contextInfo,
		);
		const messagesToSend = systemContent
			? [
					{ role: "system" as const, content: systemContent },
					...messages,
					userMsg,
				]
			: [...messages, userMsg];
		try {
			const res = await fetch(`${API_BASE}/api/llm/agentic`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					messages: messagesToSend.map((x) => ({
						role: x.role,
						content: x.content,
					})),
					model: model || "llama3.2",
				}),
			});
			const text = await res.text();
			let data: Record<string, unknown>;
			try {
				data = text ? JSON.parse(text) : {};
			} catch {
				setMessages((m) => [
					...m,
					{
						role: "assistant",
						content: `Failed: Backend returned invalid response (${text.slice(0, 100)}...)`,
					},
				]);
				return;
			}
			if (data.error) {
				setMessages((m) => [
					...m,
					{ role: "assistant", content: `Error: ${data.error}` },
				]);
			} else {
				const msg = data.message as { content?: string } | undefined;
				const choices = data.choices as
					| Array<{ message?: { content?: string } }>
					| undefined;
				const content =
					msg?.content ??
					choices?.[0]?.message?.content ??
					JSON.stringify(data);
				setMessages((m) => [
					...m,
					{ role: "assistant", content, ts: new Date().toISOString() },
				]);
			}
		} catch (e) {
			setMessages((m) => [
				...m,
				{
					role: "assistant",
					content: `Failed: ${e instanceof Error ? e.message : "Unknown error"}`,
				},
			]);
		} finally {
			setLoading(false);
		}
	};

	const handleClear = () => {
		setMessages([]);
		try {
			localStorage.removeItem(STORAGE_KEY);
		} catch {}
	};

	const handleExport = () => {
		const lines = messages.map(
			(m) =>
				`[${m.ts || "unknown"}] ${m.role === "user" ? "You" : "Assistant"}: ${m.content}`,
		);
		const blob = new Blob([lines.join("\n")], { type: "text/plain" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `calibre-mcp-chat-${new Date().toISOString().slice(0, 10)}.txt`;
		a.click();
		URL.revokeObjectURL(url);
	};

	return (
		<div
			className="mx-auto p-6 flex flex-col flex-1 min-h-0"
			data-testid="chat-page"
		>
			{/* Controls bar */}
			<div
				className="flex flex-wrap gap-4 mb-4 items-end"
				data-testid="chat-controls"
			>
				<div>
					<label className="block text-sm text-slate-400 mb-1">
						Personality
					</label>
					<select
						value={personality}
						onChange={(e) => setPersonality(e.target.value)}
						className="px-4 py-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber"
						data-testid="personality-select"
					>
						{PERSONALITIES.map((p) => (
							<option key={p.id} value={p.id}>
								{p.label}
							</option>
						))}
					</select>
				</div>
				<div>
					<label className="block text-sm text-slate-400 mb-1">Model</label>
					<input
						type="text"
						value={model}
						onChange={(e) => setModel(e.target.value)}
						placeholder="llama3.2"
						className="px-4 py-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber w-36"
					/>
				</div>
				{skillName && (
					<div className="self-center">
						<span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-1 rounded border border-zinc-700">
							skill:{skillName}
						</span>
					</div>
				)}
				{personality === "custom" && (
					<div className="self-stretch flex-1 max-w-md">
						<label className="block text-xs text-slate-400 mb-1">
							Custom Prompt
						</label>
						<textarea
							value={customPrompt}
							onChange={(e) => {
								setCustomPrompt(e.target.value);
								try {
									localStorage.setItem(
										"calibre-mcp-chat-custom-prompt",
										e.target.value,
									);
								} catch {}
							}}
							placeholder="Write your custom system prompt here..."
							rows={2}
							className="w-full px-3 py-1.5 rounded bg-zinc-800 border border-zinc-600 text-zinc-100 text-xs placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber resize-none"
						/>
					</div>
				)}
				<div className="flex items-center gap-2 self-center">
					<span
						className={`w-2 h-2 rounded-full ${
							providerStatus === "connected"
								? "bg-green-500"
								: providerStatus === "offline"
									? "bg-red-500"
									: "bg-gray-500"
						} animate-pulse`}
					/>
					<span className="text-zinc-400 text-sm">
						{providerStatus === "connected"
							? "Backend online"
							: providerStatus === "offline"
								? "Offline"
								: "Detecting..."}
					</span>
				</div>
				<div className="flex gap-1 self-center ml-auto">
					<button
						onClick={handleExport}
						disabled={messages.length === 0}
						className="p-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-400 hover:text-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed"
						title="Export conversation"
						data-testid="chat-export"
					>
						<Download size={18} />
					</button>
					<button
						onClick={handleClear}
						disabled={messages.length === 0}
						className="p-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-400 hover:text-red-400 disabled:opacity-30 disabled:cursor-not-allowed"
						title="Clear conversation"
						data-testid="chat-clear"
					>
						<Trash2 size={18} />
					</button>
				</div>
			</div>

			{/* Messages */}
			<div
				className="flex-1 overflow-auto rounded-lg bg-zinc-800 border border-zinc-600 p-4 space-y-4"
				data-testid="chat-messages"
			>
				{messages.length === 0 && (
					<div>
						<p className="text-zinc-500 text-center py-4">
							Ask about your library, books, or anything. Uses Ollama/LM Studio
							by default.
						</p>
						<div
							className="flex flex-wrap gap-2 justify-center mt-2"
							data-testid="example-prompts"
						>
							{EXAMPLE_PROMPTS.map((prompt) => (
								<button
									key={prompt}
									onClick={() => setInput(prompt)}
									className="px-3 py-1.5 text-xs rounded-full bg-zinc-700 border border-zinc-600 text-zinc-300 hover:bg-zinc-600 hover:text-zinc-100 transition-colors"
								>
									{prompt}
								</button>
							))}
						</div>
					</div>
				)}
				{messages.map((msg, i) => (
					<div
						key={i}
						className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
					>
						<div
							className={`max-w-[85%] rounded-lg px-4 py-2 ${
								msg.role === "user"
									? "bg-amber/20 text-zinc-200"
									: "bg-zinc-700 text-zinc-200"
							}`}
						>
							<p className="whitespace-pre-wrap">{msg.content}</p>
						</div>
					</div>
				))}
				{loading && (
					<div className="flex justify-start">
						<div className="bg-zinc-700 rounded-lg px-4 py-2 text-zinc-400 animate-pulse">
							Thinking...
						</div>
					</div>
				)}
				<div ref={bottomRef} />
			</div>

			{/* Input */}
			<form onSubmit={handleSubmit} className="mt-4 flex gap-2">
				<input
					type="text"
					value={input}
					onChange={(e) => setInput(e.target.value)}
					placeholder="Message..."
					disabled={loading}
					className="flex-1 px-4 py-3 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber disabled:opacity-50"
					data-testid="chat-input"
				/>
				<button
					type="submit"
					disabled={loading || !input.trim()}
					className="px-6 py-3 rounded-lg bg-amber text-zinc-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
					data-testid="chat-send"
				>
					Send
				</button>
			</form>
		</div>
	);
}
