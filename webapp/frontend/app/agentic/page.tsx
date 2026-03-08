import Link from 'next/link';

export default function AgenticPage() {
  return (
    <div className="container mx-auto p-6 max-w-3xl">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Agentic Workflow</h1>
      <p className="text-slate-400 mb-6">
        CalibreMCP supports FastMCP 3.1 sampling and agentic workflows: the AI can chain multiple tools in one flow without you calling each step manually.
      </p>

      <section className="space-y-4 text-slate-300">
        <h2 className="text-xl font-semibold text-slate-200">How it works</h2>
        <ol className="list-decimal list-inside space-y-2">
          <li><strong>Discover:</strong> List libraries, switch to one (<code className="text-amber bg-slate-800 px-1 rounded">manage_libraries</code>).</li>
          <li><strong>Search:</strong> Use <code className="text-amber bg-slate-800 px-1 rounded">query_books</code>, <code className="text-amber bg-slate-800 px-1 rounded">calibre_metadata_search</code>, or <code className="text-amber bg-slate-800 px-1 rounded">search_fulltext</code>.</li>
          <li><strong>Act:</strong> Open a book (<code className="text-amber bg-slate-800 px-1 rounded">manage_viewer</code>), show metadata, or run bulk operations.</li>
        </ol>
        <p>
          Each tool returns <code className="text-amber bg-slate-800 px-1 rounded">success</code>, <code className="text-amber bg-slate-800 px-1 rounded">message</code>, and data so the next step can be chosen automatically.
        </p>

        <h2 className="text-xl font-semibold text-slate-200 mt-6">Where to use it</h2>
        <p>
          In <strong>Chat</strong> (with an MCP-connected LLM) or any MCP client: ask e.g. &quot;Open a random unread science fiction book&quot; or &quot;Find programming books about Python and recommend one.&quot; The model will call the tools in sequence (sampling/agentic mode).
        </p>

        <p className="pt-4">
          <Link href="/chat" className="text-amber hover:underline">Open Chat</Link>
          {' · '}
          <Link href="/skills" className="text-amber hover:underline">Skills</Link>
          {' · '}
          <Link href="/rag" className="text-amber hover:underline">Semantic Search</Link>
        </p>
      </section>
    </div>
  );
}
