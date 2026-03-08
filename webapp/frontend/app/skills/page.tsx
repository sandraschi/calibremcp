import Link from 'next/link';
import { listSkills } from '@/common/api';

export default async function SkillsPage() {
  let skills: { id: string; name: string; prompt: string }[] = [];
  try {
    const res = await listSkills();
    skills = res.skills ?? [];
  } catch {
    // use fallback
    skills = [
      { id: 'reading_recommendations', name: 'Reading Recommendations', prompt: 'reading_recommendations' },
      { id: 'library_health', name: 'Library Health', prompt: 'library_health' },
      { id: 'semantic_search', name: 'Semantic Search (Metadata RAG)', prompt: 'calibre_semantic_search' },
      { id: 'agentic_workflow', name: 'Agentic Workflow', prompt: 'calibre_mcp_guide' },
    ];
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Skills</h1>
      <p className="text-slate-400 mb-6">
        CalibreMCP skills are predefined workflows you can run via prompts in Chat or MCP clients. Each skill maps to a prompt that guides the AI to use the right tools.
      </p>

      <ul className="grid gap-3 max-w-2xl">
        {skills.map((s) => (
          <li
            key={s.id}
            className="rounded-lg border border-slate-600 bg-slate-800/50 p-4 flex items-center justify-between"
          >
            <div>
              <span className="font-medium text-slate-200">{s.name}</span>
              <span className="text-slate-500 ml-2 text-sm">prompt: {s.prompt}</span>
            </div>
            <Link
              href="/chat"
              className="text-sm text-amber hover:underline"
            >
              Use in Chat
            </Link>
          </li>
        ))}
      </ul>

      <p className="mt-6 text-slate-500 text-sm">
        For agentic tool chaining and sampling, see the <Link href="/agentic" className="text-amber hover:underline">Agentic</Link> page.
      </p>
    </div>
  );
}
