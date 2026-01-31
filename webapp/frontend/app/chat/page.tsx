'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const PERSONALITIES = [
  { id: 'default', label: 'Default', preprompt: '' },
  { id: 'librarian', label: 'Librarian', preprompt: 'You are a helpful librarian assistant. Be concise and focus on book recommendations, metadata, and library organization.' },
  { id: 'casual', label: 'Casual', preprompt: 'You are a friendly book lover. Chat naturally about books, reading habits, and recommendations.' },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState('llama3.2');
  const [personality, setPersonality] = useState('default');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: 'user', content: input.trim() };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setLoading(true);

    const preprompt = PERSONALITIES.find((p) => p.id === personality)?.preprompt ?? '';
    const messagesToSend = preprompt
      ? [{ role: 'system' as const, content: preprompt }, ...messages, userMsg]
      : [...messages, userMsg];
    try {
      const res = await fetch('/api/llm/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: messagesToSend.map((x) => ({ role: x.role, content: x.content })),
          model,
          stream: false,
        }),
      });
      const text = await res.text();
      let data: Record<string, unknown>;
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        setMessages((m) => [
          ...m,
          { role: 'assistant', content: `Failed: Backend returned invalid response (${text.slice(0, 100)}...)` },
        ]);
        return;
      }
      if (data.error) {
        setMessages((m) => [
          ...m,
          { role: 'assistant', content: `Error: ${data.error}` },
        ]);
      } else {
        const msg = data.message as { content?: string } | undefined;
        const choices = data.choices as Array<{ message?: { content?: string } }> | undefined;
        const content =
          msg?.content ?? choices?.[0]?.message?.content ?? JSON.stringify(data);
        setMessages((m) => [...m, { role: 'assistant', content }]);
      }
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `Failed: ${e instanceof Error ? e.message : 'Unknown error'}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 flex flex-col h-[calc(100vh-8rem)]">
      <h1 className="text-3xl font-bold mb-4 text-slate-100">Chat</h1>
      <div className="flex flex-wrap gap-4 mb-4 items-end">
        <div>
          <label className="block text-sm text-slate-400 mb-1">Personality</label>
          <select
            value={personality}
            onChange={(e) => setPersonality(e.target.value)}
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
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
            placeholder="e.g. llama3.2"
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber w-36"
          />
        </div>
        <span className="text-slate-500 text-sm self-center">Configure provider in Settings</span>
      </div>
      <div className="flex-1 overflow-auto rounded-lg bg-slate-800 border border-slate-600 p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-slate-500 text-center py-8">
            Ask about your library, books, or anything. Uses Ollama/LM Studio by default.
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-amber/20 text-slate-200'
                  : 'bg-slate-700 text-slate-200'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 rounded-lg px-4 py-2 text-slate-400">...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message..."
          disabled={loading}
          className="flex-1 px-4 py-3 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-3 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
    </div>
  );
}
